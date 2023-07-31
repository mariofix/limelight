from flask_babel import lazy_gettext as _
from redis import Redis

from flask_admin import Admin
from flask_admin.consts import ICON_TYPE_BI, ICON_TYPE_FONT_AWESOME
from flask_admin.contrib import rediscli

from ..database import db
from ..models import Lineup, PypiRepo, Role, Star, StarQueue, Style, User
from .views import LineupAdmin, PypiRepoAdmin, QueueAdmin, RoleAdmin, StarAdmin, StyleAdmin, UserAdmin

redis = Redis(db=9, host="172.16.17.2", port=6379)
admin_site = Admin(
    name="limelight",
    # base_template="adminlte4/master.html",
    template_mode="bootstrap5",
    url="/admin.site",
)

admin_site.add_view(
    rediscli.RedisCli(
        redis,
        name="Redis CLI",
    ),
)

admin_site.add_view(
    UserAdmin(
        User,
        db.session,
        category=_("System"),
        menu_icon_type=ICON_TYPE_BI,
        menu_icon_value="bi-person",
    )
)
admin_site.add_view(
    RoleAdmin(
        Role,
        db.session,
        category=_("System"),
        menu_icon_type=ICON_TYPE_BI,
        menu_icon_value="bi-key",
    )
)

admin_site.add_view(
    QueueAdmin(
        StarQueue,
        db.session,
        category=_("System"),
        menu_icon_type=ICON_TYPE_BI,
        menu_icon_value="bi-cpu",
    )
)


admin_site.add_view(
    PypiRepoAdmin(
        PypiRepo,
        db.session,
        category=_("System"),
        menu_icon_type=ICON_TYPE_BI,
        menu_icon_value="bi-box-seam",
    )
)

admin_site.add_view(
    StyleAdmin(
        Style,
        db.session,
        category=_("Concerts"),
        menu_icon_type=ICON_TYPE_BI,
        menu_icon_value="bi-bookshelf",
    )
)

admin_site.add_view(
    StarAdmin(
        Star,
        db.session,
        category=_("Concerts"),
        menu_icon_type=ICON_TYPE_BI,
        menu_icon_value="bi-star",
    )
)

admin_site.add_view(
    LineupAdmin(
        Lineup,
        db.session,
        category=_("Concerts"),
        menu_icon_type=ICON_TYPE_BI,
        menu_icon_value="bi-boxes",
    )
)
