from flask_babel import lazy_gettext as _

from flask_admin import Admin
from flask_admin.consts import ICON_TYPE_FONT_AWESOME

from ..database import db
from ..models import Role, User
from .views import RoleAdmin, UserAdmin

admin_site = Admin(
    name="limelight",
    template_mode="bootstrap4",
    url="/admin.site",
)


admin_site.add_view(
    UserAdmin(
        User,
        db.session,
        category=_("System"),
        menu_icon_type=ICON_TYPE_FONT_AWESOME,
        menu_icon_value="fa-solid fa-user",
    )
)
admin_site.add_view(
    RoleAdmin(
        Role,
        db.session,
        category=_("System"),
        menu_icon_type=ICON_TYPE_FONT_AWESOME,
        menu_icon_value="fa-solid fa-list",
    )
)
