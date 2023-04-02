from flask_admin import Admin
from flask_admin.consts import ICON_TYPE_FONT_AWESOME
from flask_admin.contrib.sqla import ModelView
from cthulhu.models import User, Role
from cthulhu.database import db
from limelight.models import Recipe
from cthulhu.admin.views import UserAdmin, RoleAdmin, RecipeAdmin
from flask_babel import lazy_gettext as _

admin_site = Admin(
    name="Flask Admin",
    template_mode="bootstrap4",
    url="/boss",
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

admin_site.add_view(
    RecipeAdmin(
        Recipe,
        db.session,
        category=_("Fresquito"),
        menu_icon_type=ICON_TYPE_FONT_AWESOME,
        menu_icon_value="fa-solid fa-list",
    )
)
