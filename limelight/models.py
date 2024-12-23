import datetime
from dataclasses import dataclass

from flask_security.models import fsqla_v3 as fsqla
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column

from .database import db

fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    def __str__(self):
        return self.name


class User(db.Model, fsqla.FsUserMixin):
    def __str__(self):
        return self.username


@declarative_mixin
class TimestampMixin:

    ___abstract__ = True

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


@dataclass
class Project(db.Model, TimestampMixin):
    __tablename__ = "limelight_project"

    id: Mapped[int] = mapped_column(primary_key=True)

    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    title: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    description: Mapped[str] = mapped_column(db.String(2048), nullable=True, default=None)

    project_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    source_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    documentation_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

    pypi_slug: Mapped[str] = mapped_column(db.String(128), nullable=True)
    conda_slug: Mapped[str] = mapped_column(db.String(128), nullable=True)

    fetch_date_last: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    fetch_date_next: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    fetch_runner_name: Mapped[str] = mapped_column(db.String(16), nullable=True)

    def __str__(self):
        return self.slug

    def pypi_json_url(self) -> str:
        return f"https://pypi.org/pypi/{self.pypi_slug}/json"

    def conda_json_url(self) -> str:
        return f"https://conda.com/p/{self.conda_slug}.json"
