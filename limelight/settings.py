import os
from pathlib import Path

from flask_admin.babel import lazy_gettext as _

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = ""
DEBUG = True
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
TRUSTED_HOSTS = ["web-shrv13ytjbyw.up-de-fra1-k8s-1.apps.run-on-seenode.com", "tardis.local"]
SQLALCHEMY_DATABASE_URI = ""
SQLALCHEMY_RECORD_QUERIES = DEBUG
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 1800}

SECURITY_PASSWORD_SALT = ""
# Flask-Babel
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_TIMEZONE = "UTC"
BABEL_DEFAULT_FOLDER = "limelight/translations"
BABEL_DOMAIN = "limelight"
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "es": {"flag": "cl", "name": "Español"},
}

# Flask Debugtoolbar
DEBUG_TB_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = DEBUG
DEBUG_TB_PANELS = (
    "flask_debugtoolbar.panels.versions.VersionDebugPanel",
    "flask_debugtoolbar.panels.timer.TimerDebugPanel",
    "flask_debugtoolbar.panels.headers.HeaderDebugPanel",
    "flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel",
    "flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel",
    "flask_debugtoolbar.panels.template.TemplateDebugPanel",
    "flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel",
    "flask_debugtoolbar.panels.logger.LoggingPanel",
    "flask_debugtoolbar.panels.route_list.RouteListDebugPanel",
    "flask_debugtoolbar.panels.profiler.ProfilerDebugPanel",
    "flask_debugtoolbar.panels.g.GDebugPanel",
)
TEMPLATES_AUTO_RELOAD = True
EXPLAIN_TEMPLATE_LOADING = False


# Flask-Mailman
MAIL_SERVER = ""
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_TIMEOUT = 5
MAIL_USE_LOCALTIME = False

SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS = True
SITEMAP_IGNORE_ENDPOINTS = [
    "admin.index",
    "admin.static",
    "security.logout",
    "security.login",
    "security.verify",
    "user.action_view",
    "user.ajax_lookup",
    "user.ajax_update",
    "user.create_view",
    "user.delete_view",
    "user.details_view",
    "user.edit_view",
    "user.export",
    "user.index_view",
    "role.index_view",
    "role.ajax_lookup",
    "role.create_view",
    "role.edit_view",
    "role.details_view",
]
