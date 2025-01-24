import re

import pendulum
from sqlalchemy import func

from .core import LimelightError
from .database import db
from .models import Project, Queue
from .sources import GithubClient, GitlabClient, PepyClient, PyPiClient, SourcesConfig
from .utils import create_git_project, create_pypi_project, update_github_metadata, update_pypi_metadata
from .version import __version__


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
        "conda": create_pypi_project,
        "git": create_git_project,
    }

    new_project = creators[project_info["origen"]](project_info["slug"], fill_data)
    db.session.add(new_project)
    db.session.commit()

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


def get_old_data(days: int = 7, queue_type: int = 1):
    last_week = pendulum.now().subtract(days=days)
    if queue_type == 1:
        return db.session.execute(
            db.select(Project).where(Project.pypi_data_date <= last_week).order_by(func.random())
        ).first()
    if queue_type == 2:
        return db.session.execute(
            db.select(Project).where(Project.source_data_date <= last_week).order_by(func.random())
        ).first()
    if queue_type == 4:
        return db.session.execute(
            db.select(Project).where(Project.downloads_data_date <= last_week).order_by(func.random())
        ).first()


def get_new_data(queue_type: int = 2):
    if queue_type == 1:
        return db.session.execute(
            db.select(Project).where(Project.pypi_data_date is None).order_by(func.random())
        ).first()
    if queue_type == 2:
        return db.session.execute(
            db.select(Project).where(Project.source_data_date is None).order_by(func.random())
        ).first()
    if queue_type == 4:
        return db.session.execute(
            db.select(Project).where(Project.downloads_data_date is None).order_by(func.random())
        ).first()


def get_queue(days: int = 7, queue_type: int = 1):
    if queue_type == 1:
        last_week = pendulum.now().subtract(days=days)
        pypi = db.session.execute(
            db.select(Project).where(Project.pypi_data_date <= last_week).order_by(func.random())
        ).first()
        if pypi:
            return pypi[0].slug

    # source = db.session.execute(
    #     db.select(Project).where(Project.source_data_date <= last_week).order_by(func.random())
    # ).first()
    # if source:
    #     return source[0].slug


def add_queue(project, project_type: int):
    new_queue = Queue()
    new_queue.project_id = project[0].id
    new_queue.processed = False
    new_queue.origin = project_type
    db.session.add(new_queue)
    db.session.commit()

    return new_queue


def process_queue_item(id: int = None, admin: bool = False):
    if id:
        query = db.select(Queue).where(Queue.id == id)
    else:
        query = db.select(Queue).where(Queue.processed == False).limit(1).order_by(Queue.id)

    if item := db.session.execute(query).first():
        from flask import current_app

        q = item[0]
        if q.processed and not admin:
            raise LimelightError(f"Queue Item {q.id} already processed.")

        if q.origin == 1:
            client = PyPiClient(SourcesConfig(project_slug=q.project.pypi_slug))
            dest = "pypi_data"

        elif q.origin == 2:
            try:
                match = re.match(r"([^:]+):([^/]+)/([^/]+)$", q.project.source_slug)
                if match:
                    org, owner, repo = match.groups()
                    if org == "github":
                        client = GithubClient(
                            SourcesConfig(
                                project_slug=repo, owner_name=owner, token=current_app.config["GITHUB_TOKEN"]
                            )
                        )
                    if org == "gitlab":
                        client = GitlabClient(
                            SourcesConfig(
                                project_slug=repo, owner_name=owner, token=current_app.config["GITLAB_TOKEN"]
                            )
                        )
                    dest = "source_data"
            except Exception:
                pass
        elif q.origin == 4:
            client = PepyClient(
                SourcesConfig(project_slug=q.project.pypi_slug, token=current_app.config["PEPY_TOKEN"])
            )
            dest = "downloads_data"

        try:
            q.data = client.get()

            if q.data["response_code"] == 200:
                setattr(q.project, dest, q.data)
                setattr(q.project, f"{dest}_date", pendulum.now())
        except Exception:
            pass

        q.processed = True
        db.session.commit()
        db.session.refresh(q)
        return q
    return None
