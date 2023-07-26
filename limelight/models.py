import datetime

from flask_security.core import RoleMixin, UserMixin
from sqlalchemy.orm import Mapped, backref, declarative_mixin, mapped_column, relationship

from flask_admin.babel import lazy_gettext as _

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

    # __hash__ is required to avoid the exception
    # TypeError: unhashable type: 'Role' when saving a User
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


class Comuna(db.Model, TimestampMixin):
    __tablename__ = "ferias_comuna"

    id = db.Column(db.Integer(), primary_key=True)  # noqa: A003
    slug = db.Column(db.String(64), unique=True)
    nombre = db.Column(db.String(64))
    cut = db.Column(db.Integer())
    provincia = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255), nullable=False)
    ubicacion = db.Column(db.JSON(), nullable=True)

    ferias = relationship("Feria", back_populates="comuna")

    def __str__(self):
        return self.nombre

    def __repr__(self):
        id = self.id  # noqa: A001
        slug = self.slug
        nombre = self.nombre
        return f"<Comuna {id=}, {slug=}, {nombre=}>"


class Feria(db.Model, TimestampMixin):
    __tablename__ = "ferias_feria"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    slug: Mapped[str] = mapped_column(db.String(128), unique=True)
    nombre: Mapped[str] = mapped_column(db.String(128))
    dias: Mapped[str] = mapped_column(db.JSON(), nullable=False)
    ubicacion: Mapped[str] = mapped_column(db.JSON(), nullable=False)

    comuna_id: Mapped[int] = mapped_column(db.ForeignKey("ferias_comuna.id"), nullable=True)
    comuna: Mapped[Comuna] = relationship(back_populates="ferias")

    @property
    def dias_str(self) -> str:
        semana_arr = []
        for dia, activo in self.dias.items():  # type: ignore
            if activo:
                semana_arr.append(dia.capitalize())
        return ", ".join(semana_arr)

    @property
    def comuna_str(self) -> str:
        return self.comuna.nombre

    @property
    def funcionando(self) -> bool:
        return True if (datetime.time(8, 00) <= datetime.datetime.now().time() <= datetime.time(15, 00)) else False

    @property
    def color_icono(self) -> str:
        return "green" if self.funcionando else "red"

    @property
    def latlng(self) -> list:
        return [self.ubicacion[0]["latitude"], self.ubicacion[0]["longitude"]]  # type: ignore

    def __str__(self):
        return self.nombre

    def __repr__(self):
        id = self.id  # noqa: A001
        slug = self.slug
        nombre = self.nombre
        return f"<Feria {id=}, {slug=}, {nombre=}>"
