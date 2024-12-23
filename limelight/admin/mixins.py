from flask import abort, redirect, request, url_for  # noqa
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm

# from flask_security.core import current_user


class AdminModelView(ModelView):
    """
    For Admin related views
    """

    # We want the form token
    form_base_class = SecureForm

    def is_accessible(self):
        # return (
        #     current_user.is_active
        #     and current_user.is_authenticated
        #     and (current_user.has_role("admin") or current_user.has_role("staff"))
        # )
        return True

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a
        view is not accessible.
        """
        if not self.is_accessible():
            # if current_user.is_authenticated:
            #     # permission denied
            #     abort(403)
            # else:
            #     # login
            #     return redirect(url_for("security.login", next=request.url))
            pass
