from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme  # type: ignore
from flask_babel import lazy_gettext as _

from ..database import db
from ..models import Project, Role, User
from .views import ProjectAdmin, RoleAdmin, UserAdmin

admin_site = Admin(name="limelight", url="/roadie", theme=Bootstrap4Theme(swatch="pulse", fluid=False))

admin_site.add_view(UserAdmin(User, db.session, category=_("System")))
admin_site.add_view(RoleAdmin(Role, db.session, category=_("System")))
admin_site.add_view(ProjectAdmin(Project, db.session, category=_("Projects")))
