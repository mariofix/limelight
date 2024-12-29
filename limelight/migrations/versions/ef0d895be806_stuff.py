"""Stuff

Revision ID: ef0d895be806
Revises: e619ebcf0856
Create Date: 2024-12-28 21:07:25.078057

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = "ef0d895be806"
down_revision = "e619ebcf0856"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("limelight_project", schema=None) as batch_op:
        batch_op.add_column(sa.Column("source_slug", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("source_data", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("source_data_date", sa.DateTime(timezone=True), nullable=True))
        batch_op.drop_column("git_data")
        batch_op.drop_column("git_data_date")
        batch_op.drop_column("fetch_date_next")
        batch_op.drop_column("git_url")
        batch_op.drop_column("fetch_date_last")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("limelight_project", schema=None) as batch_op:
        batch_op.add_column(sa.Column("fetch_date_last", sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column("git_url", sa.VARCHAR(length=128), nullable=True))
        batch_op.add_column(sa.Column("fetch_date_next", sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column("git_data_date", sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column("git_data", sqlite.JSON(), nullable=True))
        batch_op.drop_column("source_data_date")
        batch_op.drop_column("source_data")
        batch_op.drop_column("source_slug")

    # ### end Alembic commands ###