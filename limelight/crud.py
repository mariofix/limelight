import pendulum
from sqlalchemy import func

from .database import db
from .models import Project
from .utils import (
    create_conda_project,
    create_git_project,
    create_pypi_project,
    update_github_metadata,
    update_pypi_metadata,
)
from .version import __version_info_str__ as __version__


def get_context_data() -> dict:
    data = {
        "app_version": __version__,
    }
    return data


def find_project(slug: str):
    p = db.session.execute(db.select(Project).where(Project.slug == slug)).first()
    return True if p else False


def create_project(project_info: dict, fill_data: bool = False):

    creators = {
        "pypi": create_pypi_project,
        "conda": create_conda_project,
        "git": create_git_project,
    }

    new_project = creators[project_info["origen"]](project_info["slug"], fill_data)
    db.session.add(new_project)
    db.session.commit()

    if fill_data:
        new_project = update_project(project=new_project)
        db.session.refresh(new_project)
    return new_project


def update_project(project):
    if project.pypi_slug:
        # update pypi
        project = update_pypi_metadata(project=project, update_cache=True)
        db.session.commit()
        db.session.refresh(project)
    if project.conda_slug:
        # update conda
        pass
    if project.source_slug:
        # update git
        project = update_github_metadata(project=project, update_cache=True)
        db.session.commit()
        db.session.refresh(project)

    return project


def get_queue(days: int = 7):
    last_week = pendulum.now().subtract(days=days)
    pypi = db.session.execute(
        db.select(Project).where(Project.pypi_data_date <= last_week).order_by(func.random())
    ).first()
    if pypi:
        return pypi[0].slug

    source = db.session.execute(
        db.select(Project).where(Project.source_data_date <= last_week).order_by(func.random())
    ).first()
    if source:
        return source[0].slug


def process_queue(limit: int = 1):
    for _ in range(limit):
        project = get_queue(days=7)
        print(f"{project = }")
