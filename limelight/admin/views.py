from flask_security.utils import hash_password
from wtforms import fields

from flask_admin.actions import action
from flask_admin.babel import lazy_gettext as _

from ..models import Role, Star, StarQueue, User
from .mixins import AdminModelView


class AppAdmin:
    form_widget_args = {
        "created_at": {
            "readonly": True,
        },
        "modified_at": {
            "readonly": True,
        },
    }
    page_size = 5
    can_create = True
    can_edit = True
    can_delete = True
    column_display_pk = True
    save_as = True
    save_as_continue = True
    can_export = True
    can_view_details = True
    can_set_page_size = True


class UserAdmin(AppAdmin, AdminModelView):
    name = _("User")
    name_plural = _("Users")
    icon = "fa-solid fa-user"
    form_excluded_columns = [User.password]
    column_list = [User.username, User.email, User.active, "roles"]

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.password2 = fields.PasswordField(_("New Password"))
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = hash_password(model.password2)


class RoleAdmin(AppAdmin, AdminModelView):
    name = _("Role")
    name_plural = _("Roles")
    icon = "fa-solid fa-list"
    column_list = [Role.name, Role.description, Role.permissions]


class StyleAdmin(AppAdmin, AdminModelView):
    name = _("Style")
    name_plural = _("Styles")
    icon = "bi-list-ul"
    column_list = ["slug", "title", "moderated"]


class StarAdmin(AppAdmin, AdminModelView):
    name = _("Star")
    name_plural = _("Stars")
    icon = "bi-star"
    column_list = ["slug", "title", "freeze", "pypi_repo", "github_repo", "star_url", "booklet_url", "demo_url"]

    @action("unfreeze", _("Un-Freeze Star"), _("u sure?"))
    def action_unfreeze(self, ids):
        members = Star.query.filter(Star.id.in_(ids))
        for _member in members.all():
            pass


class LineupAdmin(AppAdmin, AdminModelView):
    name = _("Lineup")
    name_plural = _("Lineups")
    icon = "bi-star"
    column_list = ["slug", "title"]


class QueueAdmin(AppAdmin, AdminModelView):
    name = _("Queue")
    name_plural = _("Queue")
    icon = "bi-cpu"
    column_list = ["request_url", "status", "post_process", "pypi_repo"]

    @action("process", _("Process Queue Items"), _("u sure?"))
    def action_process(self, ids):
        from ..tasks import fetch_pypi_project

        members = StarQueue.query.filter(StarQueue.id.in_(ids))
        for member in members.all():
            fetch_pypi_project.apply_async(kwargs={"slug": member.pypi_slug}, countdown=member.start_delay)


class PypiRepoAdmin(AppAdmin, AdminModelView):
    name = _("PyPi Repo")
    name_plural = _("PyPi Repos")
    icon = "bi-list-ul"
    column_list = ["slug", "name", "star", "version", "project_url"]
