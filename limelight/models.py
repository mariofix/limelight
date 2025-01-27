import datetime
import enum
from dataclasses import dataclass

import pendulum
from flask import current_app
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
    project: str = "Project"
    """Apps, Installables, Projects that uses Flask/Quart (eg: Flaskr)"""
    framework: str = "Framework"
    """Projects that implement or work tightly with Flask (eg: Flask-RESTX)"""
    extension: str = "Extension"
    """Projects that extends Flask and get included in app.extensions (eg: Flask-SQLAlchemy)"""
    module: str = "Module"
    """Projects that work tightly but doesn't get included in app.extensions (eg: Flask-AdminLTE3)"""


class ProjectTags(db.Model, TimestampMixin):
    __tablename__ = "limelight_project_tags"

    project_id: Mapped[int] = mapped_column(ForeignKey("limelight_project.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("limelight_tag.id"), primary_key=True)

    extra_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)


@dataclass
class Project(db.Model, TimestampMixin):
    __tablename__ = "limelight_project"

    id: Mapped[int] = mapped_column(primary_key=True)

    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    title: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    description: Mapped[str] = mapped_column(db.String(2048), nullable=True, default=None)
    category: Mapped[enum.Enum] = mapped_column(Enum(ProjectTypes), nullable=True, default=None)

    supported_python: Mapped[str] = mapped_column(db.String(128), nullable=True)
    supported_flask: Mapped[str] = mapped_column(db.String(128), nullable=True)
    readme: Mapped[str] = mapped_column(db.String(16000), nullable=True, default=None)
    readme_type: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
    license: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)

    last_release: Mapped[str] = mapped_column(db.String(16), nullable=True)
    last_release_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    first_release_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    project_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    source_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    documentation_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

    pypi_slug: Mapped[str] = mapped_column(db.String(128), nullable=True)
    pypi_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)
    pypi_data_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    conda_slug: Mapped[str] = mapped_column(db.String(128), nullable=True)
    conda_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)
    conda_data_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    source_slug: Mapped[str] = mapped_column(db.String(128), nullable=True)
    source_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)
    source_data_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    issues_open: Mapped[int] = mapped_column(nullable=True, default=None)
    issues_closed: Mapped[int] = mapped_column(nullable=True, default=None)

    stars: Mapped[int] = mapped_column(nullable=True, default=None)
    forks: Mapped[int] = mapped_column(nullable=True, default=None)
    network: Mapped[int] = mapped_column(nullable=True, default=None)
    watchers: Mapped[int] = mapped_column(nullable=True, default=None)
    subscribers: Mapped[int] = mapped_column(nullable=True, default=None)

    downloads: Mapped[int] = mapped_column(nullable=True, default=None)
    downloads_data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)
    downloads_data_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    tags: Mapped[list["Tag"]] = relationship(secondary="limelight_project_tags", back_populates="projects")

    def __str__(self):
        return self.slug

    def pypi_json_url(self) -> str | None:
        if not self.pypi_slug:
            return None
        return f"https://pypi.org/pypi/{self.pypi_slug}/json"

    def conda_json_url(self) -> str | None:
        if not self.conda_slug:
            return None
        return f"https://api.anaconda.org/package/{self.conda_slug}"

    def source_json_url(self) -> str | None:
        if not self.source_slug:
            return None
        if self.source_slug.startswith("github:"):
            return f"https://api.github.com/repos/{self.source_slug.split(':')[1]}"
        if self.source_slug.startswith("gitlab:"):
            return f"https://api.gitlab.com/info/{self.source_slug.split(':')[1]}"

    def github_json_url(self) -> str | None:
        return self.source_json_url()

    def gitlab_json_url(self) -> str | None:
        return self.source_json_url()

    def date_last(self, date_field: str, absolute: bool = False) -> str | None:
        try:
            de_date = pendulum.instance(getattr(self, date_field))
            return f"{de_date.diff_for_humans(absolute=absolute)}"
        except Exception as error:
            current_app.logger.warning(f"returning None {error = }")
            return None


class Tag(db.Model, TimestampMixin):
    __tablename__ = "limelight_tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    title: Mapped[str] = mapped_column(db.String(128), nullable=False)
    description: Mapped[str] = mapped_column(db.String(2048), nullable=True)
    icon: Mapped[str] = mapped_column(db.String(128), nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    feature_in_home: Mapped[bool] = mapped_column(default=False, nullable=False)
    order_in_home: Mapped[int] = mapped_column(nullable=True)

    projects: Mapped[list["Project"]] = relationship(secondary="limelight_project_tags", back_populates="tags")

    def __str__(self):
        return self.slug


class ProjectStats(db.Model, TimestampMixin):
    __tablename__ = "limelight_project_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("limelight_project.id"))
    project: Mapped["Project"] = relationship("Project")

    source: Mapped[str] = mapped_column(db.String(16), nullable=False)

    date_creation: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    date_modification: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    date_pushed: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    issues_open: Mapped[int] = mapped_column(nullable=True, default=None)
    issues_closed: Mapped[int] = mapped_column(nullable=True, default=None)

    stars: Mapped[int] = mapped_column(nullable=True, default=None)
    forks: Mapped[int] = mapped_column(nullable=True, default=None)
    network: Mapped[int] = mapped_column(nullable=True, default=None)
    watchers: Mapped[int] = mapped_column(nullable=True, default=None)
    subscribers: Mapped[int] = mapped_column(nullable=True, default=None)

    downloads: Mapped[int] = mapped_column(nullable=True, default=None)

    def __str__(self):
        return f"{self.source}:{self.id}"


@dataclass
class Queue(db.Model, TimestampMixin):
    __tablename__ = "limelight_project_queue"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(ForeignKey("limelight_project.id"))
    project: Mapped["Project"] = relationship("Project")

    processed: Mapped[bool] = mapped_column(default=False, nullable=False)
    origin: Mapped[int] = mapped_column(default=1, nullable=False, doc="1-pypi,2-source,3-conda,4-pepy,5-bigquery")

    data: Mapped[JSON] = mapped_column(type_=JSON, nullable=True)

    def __str__(self):
        return f"Queue: {self.id} - {self.processed} - {self.project}"
