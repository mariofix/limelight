import re

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
    if project.conda_slug:
        # update conda
        pass
    if project.source_slug:
        # update git
        project = update_github_metadata(project=project, update_cache=True)
        db.session.commit()

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


# def process_queue_item(id: int = None, overwrite: bool = False):
#     if id:
#         query = db.select(Queue).where(Queue.id == id)
#     else:
#         query = db.select(Queue).where(Queue.processed == False).limit(1).order_by(Queue.id)

#     if item := db.session.execute(query).first():
#         from flask import current_app

#         q = item[0]
#         if q.processed and not overwrite:
#             raise LimelightError(f"Queue Item {q.id} already processed.")

#         if q.origin == 1:
#             client = PyPiClient(SourcesConfig(project_slug=q.project.pypi_slug))
#             dest = "pypi_data"

#         elif q.origin == 2:
#             if match := re.match(r"([^:]+):([^/]+)/([^/]+)$", q.project.source_slug):
#                 org, owner, repo = match.groups()
#                 client = GitRepoClient(
#                     SourcesConfig(
#                         project_slug=repo,
#                         owner_name=owner,
#                         token=current_app.config[f"{org.upper()}_TOKEN"],
#                         git_origin=org,
#                     )
#                 )
#                 dest = "source_data"

#         elif q.origin == 4:
#             client = PepyClient(
#                 SourcesConfig(project_slug=q.project.pypi_slug, token=current_app.config["PEPY_TOKEN"])
#             )
#             dest = "downloads_data"

#         try:
#             q.data = client.get()

#             if q.data["response_code"] == 200:
#                 # we also want the headers closed issues results
#                 if q.origin == 2:
#                     q.data["closed_issues"] = client.get_closed_issues()
#                 setattr(q.project, dest, q.data)
#                 setattr(q.project, f"{dest}_date", pendulum.now())
#         except Exception:
#             pass

#         q.processed = True
#         db.session.commit()
#         return q
#     return None


def fetch_queue_item(id=None):
    """Fetch a queue item from the database."""
    query = (
        db.select(Queue).where(Queue.id == id)
        if id
        else db.select(Queue).where(Queue.processed.is_(False)).limit(1).order_by(Queue.id)
    )
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
    3: handle_git_repo,
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
