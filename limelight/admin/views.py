from flask import flash  # noqa
from flask_admin.actions import action  # noqa
from flask_admin.babel import lazy_gettext as _
from flask_security.utils import hash_password
from wtforms import fields

# from ..models import Role, Star, StarQueue, User
from ..models import Role, User  # noqa
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
    form_excluded_columns = ["password"]
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
    # column_list = ["name", "description", "permissions"]


# class StyleAdmin(AppAdmin, AdminModelView):
#     name = _("Style")
#     name_plural = _("Styles")
#     icon = "bi-list-ul"
#     column_list = ["slug", "title", "moderated"]


# class StarAdmin(AppAdmin, AdminModelView):
#     name = _("Star")
#     name_plural = _("Stars")
#     icon = "bi-star"
#     column_list = ["slug", "title", "description", "pypi_repo", "github_repo", "star_url", "booklet_url"]

#     @action("metadata", _("Update Metadata"), _("u sure?"))
#     def action_metadata(self, ids):
#         # members = Star.query.filter(Star.id.in_(ids))
#         # for member in members.all():
#         #     if member.pypi_id:
#         #         flash(f"{member.pypi_repo=}")
#         #     if member.github_id:
#         #         flash(f"{member.github_repo=}")
#         pass


# class LineupAdmin(AppAdmin, AdminModelView):
#     name = _("Lineup")
#     name_plural = _("Lineups")
#     icon = "bi-star"
#     column_list = ["slug", "title"]


# class QueueAdmin(AppAdmin, AdminModelView):
#     name = _("Queue")
#     name_plural = _("Queue")
#     icon = "bi-cpu"
#     column_list = ["request_url", "status", "post_process"]

#     @action("process", _("Process Queue Items"), _("u sure?"))
#     def action_process(self, ids):
#         # from ..tasks import process_queue_item

#         # members = StarQueue.query.filter(StarQueue.id.in_(ids))
#         # for member in members.all():
#         #     process_queue_item.apply_async(kwargs={"queue_id": member.id}, countdown=member.start_delay)
#         pass


# class PypiRepoAdmin(AppAdmin, AdminModelView):
#     name = _("PyPi Repo")
#     name_plural = _("PyPi Repos")
#     icon = "bi-list-ul"
#     column_list = ["slug", "name", "star", "version", "project_url"]


# class GithubRepoAdmin(AppAdmin, AdminModelView):
#     name = _("Github Repo")
#     name_plural = _("Github Repos")
#     icon = "bi-github"
#     column_list = ["namespace", "name", "star", "html_url"]
