import datetime
import enum
import json
from dataclasses import dataclass

from flask_admin.babel import lazy_gettext as _
from flask_security.models import fsqla_v3 as fsqla
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, backref, declarative_mixin, mapped_column, relationship

from .database import db

fsqla.FsModels.set_db_info(db)


@declarative_mixin
class TimestampMixin:

    ___abstract__ = True

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class Role(db.Model, fsqla.FsRoleMixin):
    def __str__(self):
        return self.name


class User(db.Model, fsqla.FsUserMixin):
    def __str__(self):
        return self.username


# class Style(db.Model, TimestampMixin):
#     __tablename__ = "limelight_style"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     slug: Mapped[str] = mapped_column(db.String(128), unique=True)
#     title: Mapped[str] = mapped_column(db.String(128))
#     description: Mapped[str] = mapped_column(db.String(2048))
#     moderated: Mapped[bool] = mapped_column(db.Boolean(), default=False)

#     def __str__(self):
#         return self.slug


# @dataclass
# class Star(db.Model, TimestampMixin):
#     __tablename__ = "limelight_star"

#     id: Mapped[int] = mapped_column(primary_key=True)

#     slug: Mapped[str] = mapped_column(db.String(128), unique=True)
#     title: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
#     description: Mapped[str] = mapped_column(db.String(2048), nullable=True, default=None)

#     star_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
#     booklet_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
#     demo_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

#     pypi_id: Mapped[int] = mapped_column(db.ForeignKey("limelight_repo_pypi.id"), nullable=True, default=None)
#     pypi_repo = db.relationship("PypiRepo", back_populates="star", cascade="all,delete")

#     github_id: Mapped[int] = mapped_column(db.ForeignKey("limelight_repo_github.id"), nullable=True, default=None)
#     github_repo = db.relationship("GithubRepo", back_populates="star", cascade="all,delete")

#     freeze: Mapped[bool] = mapped_column(default=False)
#     # conda_id: Mapped[int] = mapped_column(db.ForeignKey("limelight_pypi.id"), nullable=True, default=None)
#     # git_id: Mapped[int] = mapped_column(db.ForeignKey("limelight_pypi.id"), nullable=True, default=None)

#     def __str__(self):
#         return self.slug

#     @property
#     def get_license(self) -> str:
#         return self.pypi_repo.license

#     @property
#     def get_version(self) -> str:
#         return self.pypi_repo.version


# class Lineup(db.Model, TimestampMixin):
#     __tablename__ = "limelight_lineup"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     slug: Mapped[str] = mapped_column(db.String(128), unique=True)
#     title: Mapped[str] = mapped_column(db.String(128))
#     description: Mapped[str] = mapped_column(db.String(2048))

#     def __str__(self):
#         return self.slug


# class QueueStatus(enum.Enum):
#     CREATED = _("Created")
#     PROCESSING = _("Processing")
#     ERROR = _("Error")
#     COMPLETED = _("Completed")


# class StarQueue(db.Model, TimestampMixin):
#     __tablename__ = "limelight_star_queue"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     status: Mapped[QueueStatus] = mapped_column(db.Enum(QueueStatus), nullable=False, default=QueueStatus.CREATED)
#     request_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     request_data: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     response_data: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
#     start_delay: Mapped[int] = mapped_column(db.Integer(), default=5)
#     post_process: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)

#     pypi_repo_id = db.Column(db.Integer(), db.ForeignKey("limelight_repo_pypi.id"), nullable=True, default=None)
#     pypi_repo = db.relationship("PypiRepo", back_populates="queues", cascade="all,delete")

#     github_repo_id = db.Column(db.Integer(), db.ForeignKey("limelight_repo_github.id"), nullable=True, default=None)
#     github_repo = db.relationship("GithubRepo", back_populates="queues", cascade="all,delete")

#     def __str__(self) -> str:
#         return str(self.id)


# @dataclass
# class PypiRepo(db.Model, TimestampMixin):
#     __tablename__ = "limelight_repo_pypi"

#     id: Mapped[int] = mapped_column(primary_key=True)

#     slug: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
#     pypi_json_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

#     author: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     author_email: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     bugtrack_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
#     classifiers: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
#     description: Mapped[str] = mapped_column(db.Text(), nullable=True, default=None)
#     description_content_type: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
#     docs_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     download_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     downloads: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=False, default=-1)
#     home_page: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     keywords: Mapped[str] = mapped_column(db.String(2048), nullable=True, default=None)
#     platform: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
#     license: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
#     maintainer: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     maintainer_email: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     name: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     project_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     package_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     project_urls: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
#     release_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     requires_dist: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
#     requires_python: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
#     summary: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     version: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
#     yanked: Mapped[bool] = mapped_column(db.Boolean(), default=False)
#     yanked_reason: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)

#     last_serial: Mapped[int] = mapped_column(db.Integer(), nullable=True, default=None)

#     queues = db.relationship("StarQueue", back_populates="pypi_repo", cascade="all,delete")
#     star = db.relationship("Star", back_populates="pypi_repo", cascade="all,delete")

#     def __str__(self) -> str:
#         return self.slug

#     def json_url(self) -> str:
#         return f"https://pypi.org/pypi/{self.slug}/json"


# @dataclass
# class GithubRepo(db.Model, TimestampMixin):
#     __tablename__ = "limelight_repo_github"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     namespace: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
#     github_json_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

#     name: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     full_name: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     html_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     description: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     license: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
#     default_branch: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
#     fork: Mapped[bool] = mapped_column(db.Boolean(), nullable=False, default=False)
#     template: Mapped[bool] = mapped_column(db.Boolean(), nullable=False, default=False)
#     archived: Mapped[bool] = mapped_column(db.Boolean(), nullable=False, default=False)
#     creation_date: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
#     last_push_date: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
#     stargazers_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
#     watchers_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
#     forks_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
#     open_issues_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
#     network_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
#     subscribers_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)

#     queues = db.relationship("StarQueue", back_populates="github_repo", cascade="all,delete")
#     star = db.relationship("Star", back_populates="github_repo", cascade="all,delete")

#     def json_url(self) -> str:
#         return f"https://api.github.com/repos/{self.namespace}"

#     def __str__(self) -> str:
#         return self.namespace


# class GitlabRepo(db.Model, TimestampMixin):
#     __tablename__ = "limelight_repo_gitlab"

#     id: Mapped[int] = mapped_column(primary_key=True)
