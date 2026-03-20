import os

import pytest

# Must be set before importing the app so extensions pick them up at init time.
os.environ.setdefault("FLASK_SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("FLASK_SECURITY_PASSWORD_SALT", "test-salt-not-for-production")
os.environ.setdefault("FLASK_SECURITY_EMAIL_SENDER", "test@example.com")
os.environ.setdefault("FLASK_GITHUB_TOKEN", "fake-github-token")
os.environ.setdefault("FLASK_GITLAB_TOKEN", "fake-gitlab-token")

from limelight import create_app  # noqa: E402
from limelight.database import db as _db  # noqa: E402


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()




@pytest.fixture()
def client(app):
    return app.test_client()
