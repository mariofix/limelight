from flask import current_app
from redis import Redis


def get_redis() -> Redis:
    with current_app.app_context():
        redis = Redis(host=current_app.config["CELERY"]["broker_url"])
    return redis
