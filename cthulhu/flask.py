# cthulhu/flask_app.py
"""
Flask Application

Factory Pattern Flask Application for Cthulhu, this file is the main entry for all
web related inputs

Main Factory has two endpoints:
    / : example home, should be later replaced with expose
    /cthulhu.status/: special page to check for the project overall status

"""
from flask import (
    Flask,
    session,
    request,
    url_for,
    jsonify,
    request_started,
    abort,
)
from cthulhu.database import db, migrations
from cthulhu.admin.site import admin_site
from cthulhu.models import User, Role
from flask_debugtoolbar import DebugToolbarExtension
from flask_security import Security, SQLAlchemyUserDatastore
from flask_admin import helpers as admin_helpers
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_http_middleware import MiddlewareManager
from cthulhu.middleware import AllowedDomainsMiddleware
from limelight import limelight_blueprint
from flask_babel import Babel
import logging.config


def create_app(settings_file: str = None) -> Flask:
    """Main Factory

    Args:
        settings_file (str): String with the full python object. ex: `app.settings.prod`
    """
    app = Flask(__name__)
    app.wsgi_app = MiddlewareManager(app)
    app.wsgi_app.add_middleware(AllowedDomainsMiddleware)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # Configure App
    if settings_file:
        app.config.from_object(settings_file)
    app.config.from_prefixed_env()

    # Configure Loggers
    logging.config.dictConfig(app.config.get("APP_LOGGING_CONFIG"))
    toolbar = DebugToolbarExtension(app)
    # Sentry Here

    # SQLAlchemy
    db.init_app(app)
    migrations.init_app(app, db, directory="cthulhu/migrations")

    # FLask-Admin
    admin_site.init_app(app)

    # Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Flask-Babel
    babel = Babel()

    def get_locale():
        if request.args.get("lang"):
            session["lang"] = request.args.get("lang")
        return session.get("lang", app.config.get("BABEL_DEFAULT_LOCALE"))

    def get_timezone():
        user = getattr(g, "user", None)
        return user.timezone or app.config.get("BABEL_DEFAULT_TIMEZONE")

    babel.init_app(app, locale_selector=get_locale, timezone_selector=get_timezone)

    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin_site.base_template,
            admin_view=admin_site.index_view,
            h=admin_helpers,
            get_url=url_for,
            app=app,
        )

    app.register_blueprint(limelight_blueprint)

    @app.get("/")
    def home():
        return "/</body>"

    @app.get("/cthulhu.status/")
    def status():
        return "status"

    return app
