import datetime
import enum

from flask_admin.babel import lazy_gettext as _
from flask_security.core import RoleMixin, UserMixin
from sqlalchemy.orm import Mapped, backref, declarative_mixin, mapped_column, relationship

from .database import db


@declarative_mixin
class TimestampMixin:
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.datetime.now,
        nullable=False,
        name=_("created_at"),
    )
    modified_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.datetime.now,
        nullable=False,
        name=_("modified_at"),
    )


class RolesUsers(db.Model):
    __tablename__ = "security_roles_users"

    id = db.Column(db.Integer(), primary_key=True)  # noqa: A003
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("firenze_user.id"))
    role_id = db.Column("role_id", db.Integer(), db.ForeignKey("security_role.id"))


class Role(db.Model, RoleMixin, TimestampMixin):
    __tablename__ = "security_role"

    id = db.Column(db.Integer(), primary_key=True)  # noqa: A003
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.Text(), nullable=True)
    permissions = db.Column(db.JSON(), nullable=True)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = "firenze_user"

    id = db.Column(db.Integer(), primary_key=True)  # noqa: A003
    username = db.Column(db.String(64), unique=True, nullable=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    last_login_at = db.Column(db.DateTime(timezone=True))
    current_login_at = db.Column(db.DateTime(timezone=True))
    last_login_ip = db.Column(db.String(64))
    current_login_ip = db.Column(db.String(64))
    login_count = db.Column(db.Integer())

    roles = relationship(
        "Role",
        secondary="security_roles_users",
        backref=backref("users", lazy="dynamic"),
    )

    def __str__(self):
        return self.username


class Style(db.Model, TimestampMixin):
    __tablename__ = "limelight_style"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    title: Mapped[str] = mapped_column(db.String(128))
    description: Mapped[str] = mapped_column(db.String(2048))
    moderated: Mapped[bool] = mapped_column(db.Boolean(), default=False)

    def __str__(self):
        return self.slug


class Star(db.Model, TimestampMixin):
    __tablename__ = "limelight_star"

    id: Mapped[int] = mapped_column(primary_key=True)

    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    title: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    description: Mapped[str] = mapped_column(db.String(2048), nullable=True, default=None)

    star_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    booklet_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    demo_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

    pypi_id: Mapped[int] = mapped_column(db.ForeignKey("limelight_repo_pypi.id"), nullable=True, default=None)
    pypi_repo = db.relationship("PypiRepo", back_populates="star")

    github_id: Mapped[int] = mapped_column(db.ForeignKey("limelight_repo_github.id"), nullable=True, default=None)
    github_repo = db.relationship("GithubRepo", back_populates="star")

    freeze: Mapped[bool] = mapped_column(default=False)
    # conda_id: Mapped[int] = mapped_column(db.ForeignKey("limelight_pypi.id"), nullable=True, default=None)
    # git_id: Mapped[int] = mapped_column(db.ForeignKey("limelight_pypi.id"), nullable=True, default=None)

    def __str__(self):
        return self.slug


class Lineup(db.Model, TimestampMixin):
    __tablename__ = "limelight_lineup"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    title: Mapped[str] = mapped_column(db.String(128))
    description: Mapped[str] = mapped_column(db.String(2048))

    def __str__(self):
        return self.slug


class QueueStatus(enum.Enum):
    CREATED = _("Created")
    PROCESSING = _("Processing")
    ERROR = _("Error")
    COMPLETED = _("Completed")


class StarQueue(db.Model, TimestampMixin):
    __tablename__ = "limelight_star_queue"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[QueueStatus] = mapped_column(db.Enum(QueueStatus), nullable=False, default=QueueStatus.CREATED)
    request_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    request_data: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    response_data: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
    start_delay: Mapped[int] = mapped_column(db.Integer(), default=5)
    post_process: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)

    pypi_repo_id = db.Column(db.Integer(), db.ForeignKey("limelight_repo_pypi.id"), nullable=True, default=None)
    pypi_repo = db.relationship("PypiRepo", back_populates="queues")

    github_repo_id = db.Column(db.Integer(), db.ForeignKey("limelight_repo_github.id"), nullable=True, default=None)
    github_repo = db.relationship("GithubRepo", back_populates="queues")

    def __str__(self) -> str:
        return str(self.id)


class PypiRepo(db.Model, TimestampMixin):
    __tablename__ = "limelight_repo_pypi"

    id: Mapped[int] = mapped_column(primary_key=True)

    slug: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    pypi_json_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

    author: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    author_email: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    bugtrack_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    classifiers: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
    description: Mapped[str] = mapped_column(db.Text(), nullable=True, default=None)
    description_content_type: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
    docs_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    download_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    downloads: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=False, default=-1)
    home_page: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    keywords: Mapped[str] = mapped_column(db.String(2048), nullable=True, default=None)
    platform: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
    license: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
    maintainer: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    maintainer_email: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    name: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    project_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    package_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    project_urls: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
    release_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    requires_dist: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
    requires_python: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
    summary: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    version: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
    yanked: Mapped[bool] = mapped_column(db.Boolean(), default=False)
    yanked_reason: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)

    last_serial: Mapped[int] = mapped_column(db.Integer(), nullable=True, default=None)

    queues = db.relationship("StarQueue", back_populates="pypi_repo")
    star = db.relationship("Star", back_populates="pypi_repo")

    def __str__(self) -> str:
        return self.slug

    def json_url(self) -> str:
        return f"https://pypi.org/pypi/{self.slug}/json"


class GithubRepo(db.Model, TimestampMixin):
    __tablename__ = "limelight_repo_github"

    id: Mapped[int] = mapped_column(primary_key=True)
    namespace: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)
    github_json_url: Mapped[str] = mapped_column(db.String(128), nullable=True, default=None)

    name: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    full_name: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    html_url: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    description: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    license: Mapped[None | dict | list] = mapped_column(db.JSON(), nullable=True, default=None)
    default_branch: Mapped[str] = mapped_column(db.String(255), nullable=True, default=None)
    fork: Mapped[bool] = mapped_column(db.Boolean(), nullable=False, default=False)
    template: Mapped[bool] = mapped_column(db.Boolean(), nullable=False, default=False)
    archived: Mapped[bool] = mapped_column(db.Boolean(), nullable=False, default=False)
    creation_date: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
    last_push_date: Mapped[str] = mapped_column(db.String(32), nullable=True, default=None)
    stargazers_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
    watchers_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
    forks_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
    open_issues_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
    network_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)
    subscribers_count: Mapped[int] = mapped_column(db.Integer(), nullable=False, default=0)

    queues = db.relationship("StarQueue", back_populates="github_repo")
    star = db.relationship("Star", back_populates="github_repo")

    def json_url(self) -> str:
        return f"https://api.github.com/repos/{self.namespace}"

    def __str__(self) -> str:
        return self.namespace


class GitlabRepo(db.Model, TimestampMixin):
    __tablename__ = "limelight_repo_gitlab"

    id: Mapped[int] = mapped_column(primary_key=True)
