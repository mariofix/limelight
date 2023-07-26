import logging.config

from flask import Flask, render_template, request, session, url_for
from flask_babel import Babel
from flask_http_middleware import MiddlewareManager
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_sitemap import Sitemap
from werkzeug.middleware.proxy_fix import ProxyFix

from flask_admin import helpers as admin_helpers

from .admin.site import admin_site
from .database import db, migrations
from .middleware import AllowedDomainsMiddleware
from .models import Role, User


def create_app(settings_file: str | None = None) -> Flask:
    app = Flask(__name__)
    app.wsgi_app = MiddlewareManager(app)
    app.wsgi_app.add_middleware(AllowedDomainsMiddleware)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Configure App
    if settings_file:
        app.config.from_object(settings_file)
    app.config.from_prefixed_env()

    # Configure Loggers
    logging.config.dictConfig(app.config.get("APP_LOGGING_CONFIG", {"disable_existing_loggers": False}))
    # toolbar = DebugToolbarExtension(app)
    # Sentry Here

    # SQLAlchemy
    db.init_app(app)
    migrations.init_app(app, db, directory="limelight/migrations")

    # FLask-Admin
    admin_site.init_app(app)

    # Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Sitemap
    sitemap = Sitemap()
    sitemap.init_app(app)

    # Flask-Babel
    babel = Babel()

    def get_locale():
        if request.args.get("lang"):
            session["lang"] = request.args.get("lang")
        return session.get("lang", app.config.get("BABEL_DEFAULT_LOCALE"))

    def get_timezone():
        return app.config.get("BABEL_DEFAULT_TIMEZONE")

    babel.init_app(app, locale_selector=get_locale, timezone_selector=get_timezone)

    @security.context_processor
    def security_context_processor():
        return {
            "admin_base_template": admin_site.base_template,  # type: ignore
            "admin_view": admin_site.index_view,
            "h": admin_helpers,  # type: ignore
            "get_url": url_for,
            "app": app,
        }

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/robots.txt")
    def robots_txt():
        return "# robots.txt\n\nUser-agent: *\n\n"

    return app
