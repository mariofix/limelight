import os
from pathlib import Path
from flask_admin.babel import lazy_gettext as _

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = ""
DEBUG = True
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
ALLOWED_DOMAINS = ["tardis.local", "127.0.0.1"]
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_RECORD_QUERIES = DEBUG
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 1800}

FLASK_ADMIN_SWATCH = "default"
# TODO: AGREGAR DOCS
FLASK_ADMIN_UI_MODE = "dark"  # dark
FLASK_ADMIN_FLUID_LAYOUT = True
LIMELIGHT_APP_NAME = "limelight"
LIMELIGHT_APP_SLOGAN = "Flask's brightest stars"
LIMELIGHT_FETCH_AUTOSTART = True

# Flask-Security config
SECURITY_PASSWORD_SALT = ""

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_LOGIN_USER_TEMPLATE = "accounts/login.html"

SECURITY_POST_LOGIN_VIEW = "/admin.site/"
SECURITY_POST_LOGOUT_VIEW = "/"

# Flask-Security features
SECURITY_REGISTERABLE = False
SECURITY_CONFIRMABLE = False
SECURITY_CHANGEABLE = False
SECURITY_RECOVERABLE = False
SECURITY_TRACKABLE = True
SECURITY_USERNAME_ENABLE = True
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

# Flask-RestX/SwaggerUI
SWAGGER_UI_OPERATION_ID = True
SWAGGER_UI_REQUEST_DURATION = True

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
EXPLAIN_TEMPLATE_LOADING = False


# Flask-Mailman
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_TIMEOUT = 5
MAIL_USE_LOCALTIME = False


# CELERY
CELERY = {
    "broker_url": "redis://172.16.17.2/9",
    "result_backend": "redis://172.16.17.2/9",
    "task_ignore_result": False,
    "timezone": "UTC",
    "worker_concurrency": 1,
    "worker_max_tasks_per_child": 1,
    "worker_send_task_events": True,
    "task_send_sent_event": True,
    "broker_connection_retry_on_startup": True,
}
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

APP_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname}:\t  {message}",
            "style": "{",
        },
        "verbose": {
            "format": "{asctime} {name}.{levelname} {filename}({lineno}) {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG" if DEBUG else LOG_LEVEL,
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/limelight-web.log",
            "formatter": "verbose",
            "when": "midnight",
            "interval": 1,
        },
        "console": {
            "level": "DEBUG" if DEBUG else LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["file", "console"],
        },
    },
}
