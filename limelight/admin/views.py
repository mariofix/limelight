import datetime

from flask import flash
from flask_admin.actions import action
from flask_admin.babel import lazy_gettext as _
from flask_security.utils import hash_password
from wtforms import fields

from .. import utils
from ..database import db
from ..models import Project, User
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
    page_size = 100
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
    column_list = ["username", "email", "active", "roles"]

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.password2 = fields.PasswordField("New Password")
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = hash_password(model.password2)


class RoleAdmin(AppAdmin, AdminModelView):
    name = _("Role")
    name_plural = _("Roles")
    icon = "fa-solid fa-list"


class TagAdmin(AppAdmin, AdminModelView):
    name = _("Tag")
    name_plural = _("Tags")
    icon = "fa-solid fa-list"
    column_list = ["title", "description", "projects"]


class ProjectAdmin(AppAdmin, AdminModelView):
    name = _("Project")
    name_plural = _("Projects")
    icon = "bi-star"
    column_list = ["slug", "tags", "category", "supported_python"]

    @action(
        "fetch_data",
        _("Fetch Project Data"),
        _("Fetch the latest data from their repositories. \nNote: no post-data processing in this stage."),
    )
    def action_fetch_data(self, ids):

        projects = Project.query.filter(Project.id.in_(ids))
        for project in projects.all():
            utils.fetch_project_info(project)
            flash(f"Data Retrieved: {project}", "info")

    @action(
        "update_data",
        _("Update Project Data"),
        _("Update project metadada from all available sources."),
    )
    def action_update_data(self, ids):

        projects = Project.query.filter(Project.id.in_(ids))
        for project in projects.all():
            utils.update_project_metadata(project)
            flash(f"Data Processed: {project}", "info")


class ProjectStatsAdmin(AppAdmin, AdminModelView):
    name = _("Project Stats")
    icon = "fa-solid fa-list"
    column_list = ["source", "project", "date_pushed", "downloads_m"]
