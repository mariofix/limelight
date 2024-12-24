import datetime

from flask import flash
from flask_admin.actions import action
from flask_admin.babel import lazy_gettext as _
from flask_security.utils import hash_password
from wtforms import fields

from .. import utils
from ..database import db
from ..models import Project, ProjectDatalog, User
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


class DatalogAdmin(AppAdmin, AdminModelView):
    name = _("Log")
    name_plural = _("Logs")
    icon = "bi-list-ul"
    column_list = ["id", "created_at", "project_id", "origen"]

    @action("process_datalog", "Process Datalog", "The project's data will be updated.")
    def action_process_datalog(self, ids):
        data_list = ProjectDatalog.query.filter(ProjectDatalog.id.in_(ids))
        for data in data_list.all():
            try:
                utils.process_datalog(data)
            except Exception as e:
                flash(f"{e = }", "error")
            else:
                flash(f"Data Processed {data.id}", "info")


class ProjectAdmin(AppAdmin, AdminModelView):
    name = _("Project")
    name_plural = _("Projects")
    icon = "bi-star"
    column_list = ["slug", "title", "description"]

    @action(
        "fetch_data",
        _("Fetch Project Data"),
        _("Fetch the latest data from their repositories. Note: no post-data processing in this stage."),
    )
    def action_fetch_data(self, ids):

        projects = Project.query.filter(Project.id.in_(ids))
        for project in projects.all():
            if project.pypi_slug:
                data = utils.fetch_pypi_data(project.pypi_json_url())
                project.pypi_data = data.json()
                project.pypi_data_date = datetime.datetime.now()
                db.session.commit()
            flash(f"Data Retrieved: {project}", "info")

    @action(
        "update_data",
        _("Update Project Data"),
        _("Update project info from pypi_data and conda_data."),
    )
    def action_update_data(self, ids):

        projects = Project.query.filter(Project.id.in_(ids))
        for project in projects.all():
            utils.process_pypi_data(project)
            flash(f"Data Processed: {project}", "info")
