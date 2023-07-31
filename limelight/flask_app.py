import logging.config

from authlib.integrations.flask_client import OAuth
from celery import Celery, Task
from flask import Flask, request, session, url_for
from flask_babel import Babel
from flask_debugtoolbar import DebugToolbarExtension
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
from .tasks import *  # noqa: ignore
from .the_pack import blueprint as the_pack
from .version import __version_info_str__
from .website import blueprint as website


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
    DebugToolbarExtension(app)

    # Celery
    celery_init_app(app)

    # SQLAlchemy
    db.init_app(app)
    migrations.init_app(app, db, directory="limelight/migrations")

    # FLask-Admin
    admin_site.init_app(app)

    # Flask-Security
    oauth = OAuth(app)
    oauth.register(
        name="github",
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )
    app.extensions["oauth"] = oauth

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

    @app.context_processor
    def default_data():
        return {"app_version": __version_info_str__}

    app.register_blueprint(website)
    app.register_blueprint(the_pack)

    return app


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
