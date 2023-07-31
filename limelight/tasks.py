from celery import shared_task

from .database import db
from .models import StarQueue
from .the_pack import yuko


@shared_task(ignore_result=False, serializer="json", name="fetch-pypi-project")
def fetch_pypi_project(slug: str) -> dict:
    queue_item = db.session.query(StarQueue).filter(StarQueue.pypi_slug == slug).first()
    if not queue_item:
        raise Exception(f"{slug} not found")
    if queue_item.status not in ["created"]:
        raise Exception(f"Can't process {slug}: {queue_item.status=}")
    else:
        queue_item.status = "processing"
        db.session.commit()

    info = yuko.fetch(slug)
    queue_item.status = "processed"
    queue_item.response_data = info
    queue_item.request_url = info["pypi_json_url"]
    db.session.commit()

    return {
        "url": info["pypi_json_url"],
    }
