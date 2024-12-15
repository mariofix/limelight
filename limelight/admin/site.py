from flask_admin import Admin
from flask_admin.consts import ICON_TYPE_FONT_AWESOME
from flask_babel import lazy_gettext as _

# from redis import Redis

from ..database import db
from ..models import GithubRepo, Lineup, PypiRepo, Role, Star, StarQueue, Style, User
from .views import GithubRepoAdmin, LineupAdmin, PypiRepoAdmin, QueueAdmin, RoleAdmin, StarAdmin, StyleAdmin, UserAdmin

admin_site = Admin(
    name="limelight",
    url="/admin",
)

admin_site.add_view(UserAdmin(User, db.session, category=_("System")))
admin_site.add_view(RoleAdmin(Role, db.session, category=_("System")))

admin_site.add_view(QueueAdmin(StarQueue, db.session, category=_("System")))


admin_site.add_view(PypiRepoAdmin(PypiRepo, db.session, category=_("System")))


admin_site.add_view(GithubRepoAdmin(GithubRepo, db.session, category=_("System")))

admin_site.add_view(StyleAdmin(Style, db.session, category=_("Concerts")))

admin_site.add_view(StarAdmin(Star, db.session, category=_("Concerts")))

admin_site.add_view(LineupAdmin(Lineup, db.session, category=_("Concerts")))
