import datetime
from dataclasses import dataclass

import requests

from .database import db
from .models import QueueStatus, StarQueue


@dataclass
class Fetch:
    def fetch(url: str = None) -> dict:
        print(f"{url=}")
        data = requests.get(url)
        data.raise_for_status()
        json_data = data.json()
        print(f"{json_data=}")
        return json_data


@dataclass
class Kleine(Fetch):
    @classmethod
    def pypi(cls, url: str, queue: StarQueue) -> dict:
        print(f"{url=}")
        data = cls.fetch(url)
        queue.response_data = data
        queue.status = QueueStatus.COMPLETED
        db.session.commit()
        repo_info = data["info"]
        queue.pypi_repo.pypi_json_url = queue.request_url
        queue.pypi_repo.author = repo_info["author"]
        queue.pypi_repo.author_email = repo_info["author_email"]
        queue.pypi_repo.bugtrack_url = repo_info["bugtrack_url"]
        queue.pypi_repo.classifiers = repo_info["classifiers"]
        queue.pypi_repo.description = repo_info["description"]
        queue.pypi_repo.description_content_type = repo_info["description_content_type"]
        queue.pypi_repo.docs_url = repo_info["docs_url"]
        queue.pypi_repo.download_url = repo_info["download_url"]
        queue.pypi_repo.downloads = repo_info["downloads"]
        queue.pypi_repo.home_page = repo_info["home_page"]
        queue.pypi_repo.keywords = repo_info["keywords"]
        queue.pypi_repo.platform = repo_info["platform"]
        queue.pypi_repo.license = repo_info["license"]
        queue.pypi_repo.maintainer = repo_info["maintainer"]
        queue.pypi_repo.maintainer_email = repo_info["maintainer_email"]
        queue.pypi_repo.name = repo_info["name"]
        queue.pypi_repo.project_url = repo_info["project_url"]
        queue.pypi_repo.project_urls = repo_info["project_urls"]
        queue.pypi_repo.release_url = repo_info["release_url"]
        queue.pypi_repo.requires_dist = repo_info["requires_dist"]
        queue.pypi_repo.requires_python = repo_info["requires_python"]
        queue.pypi_repo.summary = repo_info["summary"]
        queue.pypi_repo.version = repo_info["version"]
        queue.pypi_repo.yanked = repo_info["yanked"]
        queue.pypi_repo.yanked_reason = repo_info["yanked_reason"]
        queue.pypi_repo.last_serial = data["last_serial"]
        db.session.commit()
        return data


@dataclass
class Ron(Fetch):
    @classmethod
    def github(cls, url: str, queue: StarQueue) -> dict:
        print(f"{url=}")
        data = cls.fetch(url)
        queue.response_data = data
        queue.status = QueueStatus.COMPLETED
        db.session.commit()
        repo_info = data
        queue.github_repo.github_json_url = queue.request_url
        queue.github_repo.name = repo_info["name"]
        queue.github_repo.full_name = repo_info["full_name"]
        queue.github_repo.html_url = repo_info["html_url"]
        queue.github_repo.description = repo_info["description"]
        queue.github_repo.license = str(repo_info["license"]["spdx_id"])
        queue.github_repo.default_branch = repo_info["default_branch"]
        queue.github_repo.fork = repo_info["fork"]
        queue.github_repo.template = repo_info["is_template"]
        queue.github_repo.archived = repo_info["archived"]
        queue.github_repo.creation_date = repo_info["created_at"]
        queue.github_repo.last_push_date = repo_info["pushed_at"]
        queue.github_repo.stargazers_count = repo_info["stargazers_count"]
        queue.github_repo.watchers_count = repo_info["watchers_count"]
        queue.github_repo.forks_count = repo_info["forks_count"]
        queue.github_repo.open_issues_count = repo_info["open_issues_count"]
        queue.github_repo.network_count = repo_info["network_count"]
        queue.github_repo.subscribers_count = repo_info["subscribers_count"]
        db.session.commit()

        return data


@dataclass
class Nala(Fetch):
    @classmethod
    def gitlab(cls, slug: str) -> str:
        return slug


@dataclass
class Nicky(Fetch):
    @classmethod
    def conda(cls, slug: str) -> str:
        return slug


def lets_play(queue_id: int) -> dict:
    queue = db.get_or_404(StarQueue, queue_id)
    print(f"db.get_or_404(StarQueue, {queue_id})")
    print(f"{queue}")
    queue.status = QueueStatus.PROCESSING
    db.session.commit()
    if queue.post_process == "pypi_repo":
        print(f"Kleine().pypi({queue.request_url}, {queue})")
        return Kleine().pypi(queue.request_url, queue)
    if queue.post_process == "github_repo":
        print(f"Ron().github({queue.request_url}, {queue})")
        return Ron().github(queue.request_url, queue)
