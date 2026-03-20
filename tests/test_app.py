"""Tests for app factory and configuration."""


def test_app_created(app):
    assert app is not None
    assert app.name == "limelight"


def test_testing_flag(app):
    assert app.config["TESTING"] is True


def test_database_uri_is_set(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"] != ""


def test_limiter_registered(app):
    assert "limiter" in app.extensions


def test_blueprints_registered(app):
    blueprint_names = list(app.blueprints.keys())
    assert "website" in blueprint_names
    assert "api" in blueprint_names
