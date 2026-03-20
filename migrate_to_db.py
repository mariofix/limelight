#!/usr/bin/env python3
"""
Migrate data from SQLite to MySQL or PostgreSQL.

STEPS:
  1. Create the schema in the target DB first:
       FLASK_SQLALCHEMY_DATABASE_URI="mysql+pymysql://..." flask db upgrade
       # or
       FLASK_SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://..." flask db upgrade

  2. Run this script:
       python migrate_to_db.py \
           --source sqlite:///path/to/db.sqlite3 \
           --target mysql+pymysql://user:pass@host/dbname

     Or via environment variables:
       SOURCE_DB_URL=sqlite:///... TARGET_DB_URL=mysql+pymysql://... python migrate_to_db.py

NOTE: For MySQL, install pymysql:  pip install pymysql
      For PostgreSQL, install psycopg2:  pip install psycopg2-binary
"""

import argparse
import os
import sys

from sqlalchemy import MetaData, create_engine, func, select, text

# Insertion order respects foreign key dependencies.
# Tables not present in source/target are skipped automatically.
TABLE_ORDER = [
    "role",
    "user",
    "roles_users",
    "limelight_tag",
    "limelight_project",
    "limelight_project_tags",
    "limelight_project_stats",
    "limelight_project_queue",
]

BATCH_SIZE = 200


def migrate(source_url: str, target_url: str) -> None:
    src_engine = create_engine(source_url)
    tgt_engine = create_engine(target_url)

    src_meta = MetaData()
    src_meta.reflect(bind=src_engine)

    tgt_meta = MetaData()
    tgt_meta.reflect(bind=tgt_engine)

    is_mysql = tgt_engine.dialect.name == "mysql"
    is_postgres = tgt_engine.dialect.name == "postgresql"

    with src_engine.connect() as src_conn, tgt_engine.connect() as tgt_conn:
        if is_mysql:
            tgt_conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        for table_name in TABLE_ORDER:
            if table_name not in src_meta.tables:
                print(f"  skip   {table_name!r} — not in source")
                continue
            if table_name not in tgt_meta.tables:
                print(f"  skip   {table_name!r} — not in target (run flask db upgrade first)")
                continue

            src_table = src_meta.tables[table_name]
            tgt_table = tgt_meta.tables[table_name]

            total = src_conn.execute(select(func.count()).select_from(src_table)).scalar()
            if total == 0:
                print(f"  empty  {table_name!r}")
                continue

            tgt_conn.execute(tgt_table.delete())

            copied = 0
            offset = 0
            while True:
                rows = src_conn.execute(src_table.select().offset(offset).limit(BATCH_SIZE)).fetchall()
                if not rows:
                    break
                tgt_conn.execute(tgt_table.insert(), [dict(row._mapping) for row in rows])
                copied += len(rows)
                offset += BATCH_SIZE

            tgt_conn.commit()
            print(f"  done   {table_name!r}: {copied}/{total} rows")

        if is_mysql:
            tgt_conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            tgt_conn.commit()

        # Reset sequences on PostgreSQL so new inserts don't collide with migrated IDs
        if is_postgres:
            for table_name in TABLE_ORDER:
                if table_name not in tgt_meta.tables:
                    continue
                tgt_table = tgt_meta.tables[table_name]
                pk_cols = [c for c in tgt_table.primary_key.columns if c.autoincrement is True or c.autoincrement == "auto"]
                for col in pk_cols:
                    seq = f"{table_name}_{col.name}_seq"
                    tgt_conn.execute(text(f"SELECT setval('{seq}', (SELECT MAX({col.name}) FROM {table_name}))"))
            tgt_conn.commit()
            print("\n  PostgreSQL sequences reset.")


def _safe_target(url: str) -> str:
    """Hide credentials from log output."""
    if "@" in url:
        scheme = url.split("@")[0].rsplit(":", 1)[0]
        host_db = url.split("@", 1)[1]
        return f"{scheme}:***@{host_db}"
    return url


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copy all data from a SQLite database to MySQL or PostgreSQL.\n"
        "Run 'flask db upgrade' against the target DB before running this script.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--source", default=os.environ.get("SOURCE_DB_URL"), help="Source SQLite URL (sqlite:///...)")
    parser.add_argument("--target", default=os.environ.get("TARGET_DB_URL"), help="Target DB URL (mysql+pymysql://... or postgresql+psycopg2://...)")
    args = parser.parse_args()

    if not args.source:
        sys.exit("Error: --source or SOURCE_DB_URL is required")
    if not args.target:
        sys.exit("Error: --target or TARGET_DB_URL is required")

    print(f"Source : {args.source}")
    print(f"Target : {_safe_target(args.target)}")
    print()

    migrate(args.source, args.target)

    print("\nMigration complete.")
    print("Verify row counts and then update FLASK_SQLALCHEMY_DATABASE_URI in your .env.")


if __name__ == "__main__":
    main()
