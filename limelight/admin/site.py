from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme  # type: ignore
from flask_babel import lazy_gettext as _

from ..database import db
from ..models import Role, User
from .views import RoleAdmin, UserAdmin

admin_site = Admin(name="limelight", url="/admin", theme=Bootstrap4Theme(swatch="pulse", fluid=False))

admin_site.add_view(UserAdmin(User, db.session, category=_("System")))
admin_site.add_view(RoleAdmin(Role, db.session, category=_("System")))

# admin_site.add_view(QueueAdmin(StarQueue, db.session, category=_("System")))
# admin_site.add_view(PypiRepoAdmin(PypiRepo, db.session, category=_("System")))
# admin_site.add_view(GithubRepoAdmin(GithubRepo, db.session, category=_("System")))
# admin_site.add_view(StyleAdmin(Style, db.session, category=_("Concerts")))
# admin_site.add_view(StarAdmin(Star, db.session, category=_("Concerts")))
# admin_site.add_view(LineupAdmin(Lineup, db.session, category=_("Concerts")))
