"""Tests for public website routes."""


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_help(client):
    response = client.get("/help/")
    assert response.status_code == 200


def test_robots_txt(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "text/plain" in response.content_type


def test_sitemap_xml(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200


def test_project_list_extension(client):
    response = client.get("/extension/")
    assert response.status_code == 200


def test_project_list_framework(client):
    response = client.get("/framework/")
    assert response.status_code == 200


def test_project_list_fulllist(client):
    response = client.get("/fulllist/")
    assert response.status_code == 200


def test_new_project_form(client):
    response = client.get("/new-project/")
    assert response.status_code == 200


def test_unknown_project_returns_404(client):
    response = client.get("/project/this-package-does-not-exist-xyz")
    assert response.status_code == 404


def test_api_new_project_post_missing_data(client):
    response = client.post("/api/new-project/", json={})
    assert response.status_code == 400


def test_api_new_project_get_not_allowed(client):
    response = client.get("/api/new-project/")
    assert response.status_code == 405
