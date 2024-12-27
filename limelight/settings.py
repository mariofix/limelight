from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = ""
DEBUG = False
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
TRUSTED_HOSTS = ["tardis.local", "flaskpackages.pythonanywhere.com"]
SESSION_COOKIE_NAME = "limelight"
ADMIN_BASE_URL = "admin"

SQLALCHEMY_DATABASE_URI = ""
SQLALCHEMY_RECORD_QUERIES = DEBUG
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 1800}

SECURITY_EMAIL_SENDER = ""
SECURITY_PASSWORD_SALT = ""
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_POST_LOGIN_VIEW = "/"
SECURITY_POST_LOGOUT_VIEW = "/"
SECURITY_AUTO_LOGIN_AFTER_CONFIRM = True
SECURITY_ANONYMOUS_USER_DISABLED = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_USERNAME_ENABLE = True
SECURITY_USERNAME_REQUIRED = True
SECURITY_REGISTERABLE = False
SECURITY_CONFIRMABLE = False
SECURITY_RECOVERABLE = False
SECURITY_OAUTH_ENABLE = False
SECURITY_OAUTH_BUILTIN_PROVIDERS = ["google", "github"]


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
DEBUG_TB_ENABLED = DEBUG
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
EXPLAIN_TEMPLATE_LOADING = DEBUG


# Flask-Mailman
MAIL_SERVER = ""
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_TIMEOUT = 5
MAIL_USE_LOCALTIME = True

SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS = True
SITEMAP_URL_SCHEME = "https"
SITEMAP_IGNORE_ENDPOINTS = [
    "admin.index",
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
    "project.index_view",
    "project.ajax_lookup",
    "project.create_view",
    "project.edit_view",
    "project.details_view",
    "debugtoolbar.sql_select",
    "robots",
]
