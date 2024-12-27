import datetime
import enum
from dataclasses import dataclass
from typing import List

from flask_security.models import fsqla_v3 as fsqla
from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column, relationship
from sqlalchemy.types import JSON

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


class ProjectTypes(enum.Enum):
    application: str = "Application"
    framework: str = "Framework"
    library: str = "Library"
    module: str = "Module"
    project: str = "Project"


@dataclass
class Project(db.Model, TimestampMixin):
    __tablename__ = "limelight_project"

    id: Mapped[int] = mapped_column(primary_key=True)

    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    title: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    description: Mapped[str] = mapped_column(db.String(2048), nullable=True, default=None)
    category: Mapped[enum.Enum] = mapped_column(Enum(ProjectTypes), nullable=True, default=None)
    supported_python: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)

    project_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    source_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    documentation_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

    pypi_slug: Mapped[str] = mapped_column(db.String(128), nullable=True)
    pypi_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)
    pypi_data_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    conda_slug: Mapped[str] = mapped_column(db.String(128), nullable=True)
    conda_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)
    conda_data_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    git_url: Mapped[str] = mapped_column(db.String(128), nullable=True)
    git_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)
    git_data_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    fetch_date_last: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    fetch_date_next: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    tags: Mapped[List["ProjectTags"]] = relationship(back_populates="project")

    def __str__(self):
        return self.slug

    def pypi_json_url(self) -> str:
        return f"https://pypi.org/pypi/{self.pypi_slug}/json"

    def conda_json_url(self) -> str:
        return f"https://api.anaconda.org/package/{self.conda_slug}"


class Tag(db.Model, TimestampMixin):
    __tablename__ = "limelight_tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    title: Mapped[str] = mapped_column(db.String(128), nullable=False)
    description: Mapped[str] = mapped_column(db.String(2048), nullable=False)

    project: Mapped[List["ProjectTags"]] = relationship(back_populates="tags")

    def __str__(self):
        return self.slug


class ProjectTags(db.Model, TimestampMixin):
    __tablename__ = "limelight_project_tags"

    project_id: Mapped[int] = mapped_column(ForeignKey("limelight_project.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("limelight_tag.id"), primary_key=True)

    extra_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="tags")
    tags: Mapped["Tag"] = relationship(back_populates="project")
