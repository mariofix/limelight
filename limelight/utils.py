import datetime
import re
from typing import Any

import requests
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from .database import db
from .version import __version__


def expand_requires_python(requires_python, max_python_version="3.13"):
    if not requires_python:
        return []

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
    if not url:
        return None
    return requests.get(url, headers={"user-agent": f"limelight/{__version__}"})


def fetch_github_api(url):
    if not url:
        return None
    from flask import current_app

    with current_app.app_context():
        return requests.get(
            url,
            headers={
                "user-agent": f"limelight/{__version__}",
                "Authorization": f"Bearer {current_app.config['GITHUB_TOKEN']}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )


def fetch_project_info(project):
    pypi_data = fetch_project_data(project.pypi_json_url())
    if pypi_data:
        project.pypi_data = pypi_data.json() if pypi_data else None
        project.pypi_data_date = datetime.datetime.now()

    conda_data = fetch_project_data(project.conda_json_url())
    if conda_data:
        project.conda_data = conda_data.json() if conda_data else None
        project.conda_data_date = datetime.datetime.now()

    github_data = fetch_github_api(project.github_json_url())
    if github_data:
        project.source_data = github_data.json() if github_data else None
        project.source_data_date = datetime.datetime.now()

    db.session.commit()
    return project


def get_downloads(package):
    import json
    import secrets

    download_data = json.loads(
        {
            "last_update": "2024-12-30 04:25:10",
            "query": {
                "bytes_billed": 909115392,
                "bytes_processed": 908272767,
                "cached": False,
                "estimated_cost": "0.01",
            },
            "rows": [
                {"ci": "True", "download_count": secrets.randbelow(9999999)},
                {"ci": "None", "download_count": secrets.randbelow(99999999)},
            ],
        }
    )
    try:
        return download_data["rows"][1]["download_count"]
    except KeyError:
        return None


def update_project_metadata(project: Any):
    # Pypi takes precedence, since conda-forge is not up-to-date
    # Only use anaconda to provide instructions on installation
    if project.pypi_data:
        pypi_info = project.pypi_data.get("info", None)

    if pypi_info:
        project.downloads = get_downloads(project.pypi_slug)
        project.title = pypi_info.get("name", None)
        project.description = pypi_info.get("summary", None)
        project.project_url = pypi_info.get("project_url", None)
        project.supported_python = pypi_info.get("requires_python")
        project.docs_url = pypi_info.get("docs_url", None)
        project.readme = pypi_info.get("description", None)
        project.readme_type = pypi_info.get("description_content_type", None)
        project.license = pypi_info.get("license", None)
        project.last_release = pypi_info.get("version", None)
        try:
            project.last_release_date = datetime.datetime.fromisoformat(
                project.pypi_data["releases"][pypi_info.get("version")][0]["upload_time"]
            )
        except (KeyError, IndexError):
            project.last_release_date = None

        try:

            project.first_release_date = datetime.datetime.fromisoformat(
                project.pypi_data["releases"][next(iter(project.pypi_data["releases"]))][0]["upload_time"]
            )
        except (KeyError, IndexError):
            project.first_release_date = None

        git_slug = None
        for _, link in pypi_info.get("project_urls").items():

            if match := re.match(r"^https://(github|gitlab)\.com/([^/]+/[^/]+?)(?:\.git|/)?$", link):
                platform, repo_path = match.groups()
                git_slug = f"{platform}:{repo_path}"
                break
        project.source_slug = git_slug
        if not project.source_url:
            project.source_url = link

        github_data = fetch_github_api(project.github_json_url())
        if github_data:
            project.source_data = github_data.json() if github_data else None
            project.source_data_date = datetime.datetime.now()

    # Not needed, left here for future-proofing
    # if project.conda_data:
    #     conda_info = project.conda_data
    # if conda_info:
    #     pass

    # TODO: Update Stats from here
    repo_info = False
    if project.source_data:
        repo_info = project.source_data
    if repo_info:
        if not project.title:
            project.title = repo_info.get("name", None)
        if not project.description:
            project.description = repo_info.get("description", None)
        if not project.project_url:
            project.project_url = repo_info.get("homepage", None)
        if not project.license:
            project.license = repo_info.get("license").get("spdx_id", None)
        if not project.source_url:
            project.source_url = repo_info.get("html_url", None)

        project.issues_open = repo_info.get("open_issues_count")
        try:
            url = f"{project.github_json_url()}/issues?state=closed&per_page=1"
            github_data = fetch_github_api(url)
            link_header = github_data.headers.get("Link")
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if match:
                total_closed_issues = int(match.group(1))
            else:
                total_closed_issues = 0
            project.issues_closed = total_closed_issues
        except Exception:
            project.issues_closed = None

        project.stars = repo_info.get("stargazers_count")
        project.forks = repo_info.get("forks_count")
        project.network = repo_info.get("network_count")
        project.subscribers = repo_info.get("subscribers_count")
        project.watchers = repo_info.get("watchers_count")

    db.session.commit()
    return project


def find_source_slug(url):
    if not url:
        return None
    if match := re.match(
        r"^(?:https?://)?(github|gitlab)\.com/([^/]+/[^/]+?)(?:\.git|/)?$",
        url,
    ):
        platform, repo_path = match.groups()
        return f"{platform}:{repo_path}"
    return None


def update_github_metadata(project, update_cache: bool = False, overwrite_data: bool = False):
    if update_cache:
        github_data = fetch_github_api(project.github_json_url())
        if github_data.status_code == 200:
            project.source_data = github_data.json()
            project.source_data_date = datetime.datetime.now()

    repo_info = project.source_data

    fields = {
        "title": repo_info.get("name"),
        "description": repo_info.get("description"),
        "project_url": repo_info.get("homepage"),
        "license": repo_info.get("license", {}).get("spdx_id"),
    }

    for attr, value in fields.items():
        if overwrite_data or not getattr(project, attr):
            setattr(project, attr, value)

    project.issues_open = repo_info.get("open_issues_count")
    try:
        url = f"{project.github_json_url()}/issues?state=closed&per_page=1"
        github_data = fetch_github_api(url)
        link_header = github_data.headers.get("Link")
        match = re.search(r'page=(\d+)>; rel="last"', link_header)
        if match:
            total_closed_issues = int(match.group(1))
        else:
            total_closed_issues = 0
        project.issues_closed = total_closed_issues
    except Exception:
        project.issues_closed = None

    project.stars = repo_info.get("stargazers_count")
    project.forks = repo_info.get("forks_count")
    project.network = repo_info.get("network_count")
    project.subscribers = repo_info.get("subscribers_count")
    project.watchers = repo_info.get("watchers_count")
    return project


def update_pypi_metadata(project, update_cache: bool = False):
    if update_cache:
        pypi_data = fetch_project_data(project.pypi_json_url())
        if pypi_data.status_code == 200:
            project.pypi_data = pypi_data.json()
            project.pypi_data_date = datetime.datetime.now()

    pypi_info = project.pypi_data.get("info", None)

    project.title = pypi_info.get("name", None)
    project.description = pypi_info.get("summary", None)
    project.project_url = pypi_info.get("project_url", None)
    project.supported_python = pypi_info.get("requires_python", None)
    project.documentation_url = pypi_info.get("docs_url", None)
    project.readme = pypi_info.get("description", None)
    project.readme_type = pypi_info.get("description_content_type", None)
    project.license = pypi_info.get("license", None)
    project.last_release = pypi_info.get("version", None)

    try:
        project.last_release_date = datetime.datetime.fromisoformat(
            project.pypi_data["releases"][project.last_release][0]["upload_time"]
        )
    except (KeyError, IndexError):
        # not needed
        pass

    try:
        project.first_release_date = datetime.datetime.fromisoformat(
            project.pypi_data["releases"][next(iter(project.pypi_data["releases"]))][0]["upload_time"]
        )
    except (KeyError, IndexError):
        # not needed
        pass

    possible = [
        project.project_url,
        project.documentation_url,
        project.source_url,
        pypi_info.get("home_page", None),
        pypi_info.get("download_url", None),
    ]
    if pypi_info.get("project_urls"):
        possible = possible + [url for _, url in pypi_info.get("project_urls").items()]
    for link in possible:
        if source_slug := find_source_slug(link):
            project.source_slug = source_slug
            project.source_url = link
            break

    return project


def create_pypi_project(slug, fill_data: bool):
    from .models import Project

    new_project = Project(slug=slug, pypi_slug=slug)
    if fill_data:
        pypi_data = fetch_project_data(new_project.pypi_json_url())
        if pypi_data.status_code == 200:
            new_project.pypi_data = pypi_data.json()
            new_project.pypi_data_date = datetime.datetime.now()
    return new_project


def create_conda_project(slug, fill_data: bool):
    from .models import Project

    new_project = Project(slug=slug, conda_slug=slug)
    if fill_data:
        conda_data = fetch_project_data(new_project.conda_json_url())
        if conda_data.status_code == 200:
            new_project.conda_data = conda_data.json() if conda_data else None
            new_project.conda_data_date = datetime.datetime.now()
    return new_project


def create_git_project(url, fill_data: bool):
    from .models import Project

    if match := re.match(
        r"^https://(github|gitlab)\.com/([^/]+/[^/]+?)(?:\.git|/)?$",
        url,
    ):
        platform, repo_path = match.groups()

    new_project = Project(source_url=url, source_slug=f"{platform}:{repo_path}")
    if fill_data:
        github_data = fetch_github_api(new_project.github_json_url())
        if github_data.staus_code == 200:
            new_project.source_data = github_data.json()
            new_project.source_data_date = datetime.datetime.now()
    return new_project
