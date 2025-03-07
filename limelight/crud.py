import re
from typing import Any

import pendulum
from flask import current_app
from sqlalchemy import func

from .core import LimelightError
from .database import db
from .models import Project, Queue
from .sources import GitRepoClient, PepyClient, PyPiClient, SourcesConfig
from .utils import create_git_project, create_pypi_project, update_github_metadata, update_pypi_metadata
from .version import __version__


def get_context_data() -> dict:
    data = {
        "app_version": __version__,
    }
    return data


def find_project(slug: str) -> Project:
    p = db.session.execute(db.select(Project).where(Project.slug == slug)).first()
    return p[0] if p else False


def create_project(project_info: dict, fill_data: bool = False) -> Project:

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
    if project.conda_slug:
        # update conda
        pass
    if project.source_slug:
        # update git
        project = update_github_metadata(project=project, update_cache=True)
        db.session.commit()

    return project


def get_old_data(days: int = 7, queue_type: int = 1) -> Any:
    """Fetch projects with outdated data based on queue type."""
    last_week = pendulum.now().subtract(days=days)

    field_map = {
        1: Project.pypi_data_date,
        2: Project.source_data_date,
        4: Project.downloads_data_date,
    }

    if field := field_map.get(queue_type):
        return db.session.execute(db.select(Project).where(field <= last_week).order_by(func.random())).first()

    return None


def get_new_data(queue_type: int = 2) -> Any:
    """Fetch projects with no existing data based on queue type."""
    field_map = {
        1: Project.pypi_data_date,
        2: Project.source_data_date,
        4: Project.downloads_data_date,
    }

    if field := field_map.get(queue_type):
        return db.session.execute(db.select(Project).where(field.is_(None)).order_by(func.random())).first()

    return None


def get_queue(days: int = 7, queue_type: int = 1) -> str:
    if queue_type == 1:
        last_week = pendulum.now().subtract(days=days)
        pypi = db.session.execute(
            db.select(Project).where(Project.pypi_data_date <= last_week).order_by(func.random())
        ).first()
        if pypi:
            return pypi[0].slug


def add_queue(project, project_type: int) -> Queue:
    if db.session.execute(
        db.select(Queue)
        .where(Queue.project_id == project[0].id)
        .where(Queue.origin == project_type)
        .where(Queue.processed.is_(False))
    ).one_or_none():
        return

    new_queue = Queue()
    new_queue.project_id = project[0].id
    new_queue.processed = False
    new_queue.origin = project_type
    db.session.add(new_queue)
    db.session.commit()

    return new_queue


def fetch_queue_item(id=None) -> Any:
    """Fetch a queue item from the database."""
    query = db.select(Queue)

    if id:
        query = query.where(Queue.id == id)
    else:
        query = query.where(Queue.processed.is_(False)).order_by(Queue.id).limit(1)

    return db.session.execute(query).first()


def handle_pypi(queue_item):
    """Handler for origin 1: PyPI Client."""
    client = PyPiClient(SourcesConfig(project_slug=queue_item.project.pypi_slug))
    return client, "pypi_data"


def handle_git_repo(queue_item):
    """Handler for origin 3: Git Repository Client."""
    match = re.match(r"([^:]+):([^/]+)/([^/]+)$", queue_item.project.source_slug)
    if not match:
        raise ValueError("Invalid source slug format.")
    org, owner, repo = match.groups()
    client = GitRepoClient(
        SourcesConfig(
            project_slug=repo,
            owner_name=owner,
            token=current_app.config.get(f"{org.upper()}_TOKEN"),
            git_origin=org,
        )
    )
    return client, "source_data"


def handle_pepy(queue_item):
    """Handler for origin 4: Pepy Client."""
    client = PepyClient(
        SourcesConfig(
            project_slug=queue_item.project.pypi_slug,
            token=current_app.config.get("PEPY_TOKEN"),
        )
    )
    return client, "downloads_data"


ORIGIN_HANDLERS = {
    1: handle_pypi,
    2: handle_git_repo,
    4: handle_pepy,
}


def process_data(client, queue_item, destination):
    """Fetch data from the client and update the project."""
    data = client.get()
    if data.get("response_code") != 200:
        raise ValueError("Invalid response code from client")

    # Handle special case for origin 2 (closed issues)
    if queue_item.origin == 2:
        data["closed_issues"] = client.get_closed_issues()

    # Update project with fetched data
    queue_item.data = data
    setattr(queue_item.project, destination, data)
    setattr(queue_item.project, f"{destination}_date", pendulum.now())


def process_queue_item(id=None, overwrite=False):
    """
    Process a queue item by fetching it, determining its origin,
    and updating the project data accordingly.

    Args:
        id (int): The ID of the queue item to process (optional).
        overwrite (bool): If True, reprocess an already processed item.

    Raises:
        LimelightError: If the queue item is already processed and overwrite is False.

    Returns:
        The processed queue item, or None if no item was found.
    """
    queue_item = fetch_queue_item(id)
    if not queue_item:
        return None

    # Anoying .first() from fetch_queue_item(id)
    queue_item = queue_item[0]

    if queue_item.processed and not overwrite:
        raise LimelightError(f"Queue Item {queue_item.id} already processed.")

    # Use the appropriate handler for the origin
    handler = ORIGIN_HANDLERS.get(queue_item.origin)
    if not handler:
        raise ValueError(f"Unsupported queue origin: {queue_item.origin}")

    try:
        client, destination = handler(queue_item)
        process_data(client, queue_item, destination)
    except Exception as e:
        current_app.logger.error(f"Error processing queue item {queue_item.id}: {e}")
        return None

    # Mark the queue item as processed
    queue_item.processed = True
    db.session.commit()

    return queue_item
