import datetime

import requests
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from .version import __version__


def expand_requires_python(requires_python, max_python_version="3.13"):
    if not requires_python:
        raise ValueError("requires_python specifier cannot be empty.")

    specifier = SpecifierSet(requires_python)

    max_major, max_minor = map(int, max_python_version.split("."))
    versions = []

    for major in range(2, max_major + 1):
        for minor in range(0, max_minor + 1):
            version = Version(f"{major}.{minor}")
            if version in specifier:
                versions.append(str(version))

    return versions


def fetch_project_data(url):
    return requests.get(url, headers={"x-user-agent": f"limelight/{__version__}"})


def process_pypi_data(project):
    if project.pypi_data:
        project_info = project.pypi_data.get("info", None)

    from .database import db

    if project_info:
        project.title = project_info.get("name", None)
        project.description = project_info.get("summary", None)
        project.project_url = project_info.get("project_url", None)
        project.supported_python = expand_requires_python(project_info.get("requires_python"))

    project.fetch_date_next = project.created_at + datetime.timedelta(days=7)
    db.session.commit()
    return project


def project_exists(db, slug: str):
    from .models import Project

    p = db.session.execute(db.select(Project).where(Project.slug == slug)).first()
    return True if p else False


def create_project(db, project_info: dict):
    from .models import Project

    new_project = Project(slug=project_info["slug"])
    if project_info["origen"] == "pypi":
        new_project.pypi_slug = new_project.slug
        pypi_data = fetch_project_data(new_project.pypi_json_url())
        new_project.pypi_data = pypi_data.json()
        new_project.pypi_data_date = datetime.datetime.now()
    elif project_info["origen"] == "anaconda":
        new_project.conda_slug = new_project.slug
        conda_data = fetch_project_data(new_project.conda_json_url())
        new_project.pypi_data = conda_data.json()
        new_project.pypi_data_date = datetime.datetime.now()
    else:
        new_project.source_url = new_project.slug

    db.session.add(new_project)
    db.session.commit()

    return new_project
