from flask import Flask, request, session
from flask_babel import Babel
from flask_debugtoolbar import DebugToolbarExtension
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from flask_sitemap import Sitemap
from werkzeug.middleware.proxy_fix import ProxyFix

from .admin.site import admin_site
from .crud import get_context_data
from .database import db, migrations
from .mail import mail
from .models import Role, User
from .version import __version_info_str__
from .website import blueprint as website


def create_app(settings_file: str | None = None) -> Flask:
    app = Flask("limelight")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Configure App
    if settings_file:
        app.config.from_object(settings_file)
    app.config.from_prefixed_env()

    DebugToolbarExtension(app)

    # Mailer
    mail.init_app(app)

    # SQLAlchemy
    db.init_app(app)
    migrations.init_app(app, db, directory="limelight/migrations")

    # FLask-Admin
    admin_site.init_app(app)

    # Flask-Security
    # oauth = OAuth(app)
    # oauth.register(
    #     name="github",
    #     access_token_url="https://github.com/login/oauth/access_token",
    #     access_token_params=None,
    #     authorize_url="https://github.com/login/oauth/authorize",
    #     authorize_params=None,
    #     api_base_url="https://api.github.com/",
    #     client_kwargs={"scope": "user:email"},
    # )
    # app.extensions["oauth"] = oauth

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

    @app.context_processor
    def default_data():
        return get_context_data()

    app.register_blueprint(website, url_prefix="/")

    return app
