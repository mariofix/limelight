from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Boolean,
    ForeignKey,
    text,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import relationship, declarative_mixin, registry, backref
from sqlalchemy.dialects import mysql
from sqlalchemy import event
from cthulhu.database import db
import datetime
from flask_security import UserMixin, RoleMixin
from flask_admin.babel import lazy_gettext as _


@declarative_mixin
class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.datetime.now,
        server_default=func.now(),
        nullable=False,
        name=_("created_at"),
    )
    modified_at = Column(
        DateTime(timezone=True),
        default=None,
        onupdate=datetime.datetime.now,
        nullable=True,
        name=_("modified_at"),
    )


class RolesUsers(db.Model):
    __tablename__ = "security_roles_users"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("cthulhu_user.id"))
    role_id = db.Column("role_id", db.Integer(), db.ForeignKey("security_role.id"))


class Role(db.Model, RoleMixin, TimestampMixin):
    __tablename__ = "security_role"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(mysql.LONGTEXT, nullable=True)
    permissions = db.Column(mysql.JSON, nullable=True)

    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception
    # TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = "cthulhu_user"

    id = Column(Integer(), primary_key=True)
    username = Column(String(64), unique=True, nullable=True)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Boolean(), default=True)
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True))
    current_login_at = Column(DateTime(timezone=True))
    last_login_ip = Column(String(64))
    current_login_ip = Column(String(64))
    login_count = Column(Integer())

    roles = relationship(
        "Role",
        secondary="security_roles_users",
        backref=backref("users", lazy="dynamic"),
    )

    def __str__(self):
        return self.username


# class Event(db.Model, TimestampMixin):
#     __tablename__ = "firenze_event"

#     id = Column(Integer(), primary_key=True)
#     name = Column(String(255), nullable=False)
#     ip = Column(String(16), nullable=True)
#     port = Column(Integer(), nullable=True)
#     verb = Column(String(10), nullable=False)
#     url = Column(String(255), nullable=False)
#     data = Column(Text(), nullable=True)

#     def __str__(self):
#         return self.name


@event.listens_for(Role, "after_insert")
def user_after_insert(mapper, connection, target):
    print(f"{mapper=}")
    print(f"{connection=}")
    print(f"{target=}")
