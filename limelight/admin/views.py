from flask import flash
from flask_admin.actions import action
from flask_admin.babel import lazy_gettext as _
from flask_security.utils import hash_password
from wtforms import fields

from .. import utils
from ..crud import process_queue_item
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
    page_size = 20
    can_create = True
    can_edit = True
    can_delete = False
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
    column_list = ["slug", "name", "active", "projects"]


origin_tuple = [
    (1, "pypi"),
    (2, "git-repo"),
    (3, "conda"),
    (4, "pepy-tech"),
    (5, "google-big-query"),
]


class QueueAdmin(AppAdmin, AdminModelView):
    name = _("Queue")
    icon = "fa-solid fa-list"
    column_list = ["project", "processed", "origin"]
    form_choices = {"origin": origin_tuple}
    column_choices = {"origin": origin_tuple}
    can_delete = True

    @action(
        "process",
        _("Process Item"),
        _("u sure?"),
    )
    def action_process(self, ids):
        for id in ids:
            try:
                item = process_queue_item(id, True)
            except Exception as e:
                flash(f"Error: {e}", "error")
            else:
                flash(f"Processed {item.project}", "success")


class ProjectAdmin(AppAdmin, AdminModelView):
    name = _("Project")
    name_plural = _("Projects")
    icon = "bi-star"
    column_list = ["slug", "tags", "category", "supported_python", "supported_flask"]

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
        _("Update project metadada from all available cached-sources."),
    )
    def action_update_data(self, ids):

        projects = Project.query.filter(Project.id.in_(ids))
        for project in projects.all():
            utils.full_update_project_metadata(project)
            flash(f"Data Processed: {project}", "info")
