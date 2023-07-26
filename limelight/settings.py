from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = ""
DEBUG = True
LOG_LEVEL = "INFO"
ALLOWED_DOMAINS = ["tardis.local", "127.0.0.1"]
SQLALCHEMY_DATABASE_URI = "sqlite:///app.sqlite3"
SQLALCHEMY_RECORD_QUERIES = DEBUG
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 1800}

FLASK_ADMIN_SWATCH = "yeti"
FLASK_ADMIN_FLUID_LAYOUT = True

# Flask-Security config
SECURITY_URL_PREFIX = "/security/"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = ""

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"

SECURITY_POST_LOGIN_VIEW = "/admin.site/"
SECURITY_POST_LOGOUT_VIEW = "/login/"

# Flask-Security features
SECURITY_REGISTERABLE = False
SECURITY_TRACKABLE = True
SECURITY_USERNAME_ENABLE = True

# Flask-Babel
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_TIMEZONE = "UTC"
BABEL_DEFAULT_FOLDER = "limelight/translations"
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "es": {"flag": "cl", "name": "Español"},
}

# Flask-RestX/SwaggerUI
SWAGGER_UI_OPERATION_ID = True
SWAGGER_UI_REQUEST_DURATION = True

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
            "filename": "logs/api.log",
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
