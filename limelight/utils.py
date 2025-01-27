import datetime
import re
from typing import Any

import requests
from packaging.requirements import Requirement

from .core import LimelightError
from .database import db
from .version import __version__


def parse_requirement(req_string):
    """
    Parse a requirement string and extract package name, version constraints, and extras.

    Args:
        req_string (str): Requirement string to parse

    Returns:
        dict: Parsed requirement details
    """
    try:
        # Normalize the requirement string
        req = Requirement(req_string.strip())

        return {
            "name": req.name,
            "specifier": str(req.specifier) if req.specifier else None,
            "version_specs": [str(spec) for spec in req.specifier] if req.specifier else [],
            "extras": list(req.extras),
        }
    except Exception:
        return {"name": req_string.strip(), "specifier": None, "version_specs": [], "extras": []}


def get_package_details(package_name, requires_dist):
    """
    Find the version specification and extras for a specific package from requires_dist.

    Args:
        package_name (str): Name of the package to find
        requires_dist (list): List of requirement strings

    Returns:
        dict: Package details including name, version, and extras
    """
    if requires_dist:
        for req_string in requires_dist:
            parsed_req = parse_requirement(req_string)
            if parsed_req["name"].lower() == package_name.lower():
                return {"name": parsed_req["name"], "version": parsed_req["specifier"], "extras": parsed_req["extras"]}

    return {"name": "Flask", "version": ">=3.0", "extras": []}


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


def get_downloads(package: str):

    return None


def full_update_project_metadata(project):
    from flask import current_app

    """Updates Project info based on all available information."""
    if project.pypi_data:
        try:
            pypi_info = project.pypi_data["response_data"]["info"]
        except KeyError:
            raise LimelightError("Project.pypi_data does not have a correct structure.")

        project.title = pypi_info.get("name", None)
        project.description = pypi_info.get("summary", None)
        project.project_url = pypi_info.get("project_url", None)
        project.supported_python = pypi_info.get("requires_python", ">=3.9")
        project.docs_url = pypi_info.get("docs_url", None)
        project.readme = pypi_info.get("description", None)
        project.readme_type = pypi_info.get("description_content_type", None)
        project.license = pypi_info.get("license", None)
        project.last_release = pypi_info.get("version", None)
        if version_data := get_package_details("Flask", pypi_info.get("requires_dist")):
            project.supported_flask = version_data["version"]

        try:
            project.last_release_date = datetime.datetime.fromisoformat(
                project.pypi_data["response_data"]["releases"][pypi_info.get("version")][0]["upload_time"]
            )
        except (KeyError, IndexError):
            current_app.logger.info(f"last_release_date - {pypi_info.get('version') = }")
            current_app.logger.info(f"last_release_date - {project.pypi_data['response_data']['releases'] = }")

        try:

            project.first_release_date = datetime.datetime.fromisoformat(
                project.pypi_data["response_data"]["releases"][
                    next(
                        iter(project.pypi_data["response_data"]["releases"]),
                    )
                ][0]["upload_time"]
            )
        except (KeyError, IndexError):
            current_app.logger.info(f"first_release_date - {project.pypi_data['response_data']['releases'] = }")

        db.session.commit()

    if project.source_data:
        try:
            repo_info = project.source_data["response_data"]
        except KeyError:
            raise LimelightError("Project.source_data does not have a correct structure.")

        # Fill Missing Data
        if not project.title:
            project.title = repo_info.get("name", None)
        if not project.description:
            project.description = repo_info.get("description", None)
        if not project.project_url:
            project.project_url = repo_info.get("homepage", None)
        if not project.license or len(project.license) > 20:
            try:
                project.license = repo_info.get("license").get("spdx_id", None)
            except Exception:
                project.license = None
        if not project.source_url:
            project.source_url = repo_info.get("html_url", None)

        project.issues_open = repo_info.get("open_issues_count", 0)
        try:
            link_header = project.source_data["closed_issues"]["response_headers"].get("Link", None)
            if match := re.search(r'page=(\d+)>; rel="last"', link_header):
                project.issues_closed = int(match.group(1))

        except Exception:
            current_app.logger.info(f"{project.source_data = }")

        project.stars = repo_info.get("stargazers_count", 0)
        project.forks = repo_info.get("forks_count", 0)
        project.network = repo_info.get("network_count", 0)
        project.subscribers = repo_info.get("subscribers_count", 0)
        project.watchers = repo_info.get("watchers_count", 0)
        db.session.commit()

    if project.downloads_data:
        try:
            dload_info = project.downloads_data["response_data"]
        except KeyError:
            raise LimelightError("Project.pypi_data does not have a correct structure.")

        project.downloads = dload_info.get("total_downloads", 0)
        db.session.commit()

    return project


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
        from .sources import PyPiClient, SourcesConfig

        data_client = PyPiClient(SourcesConfig(project_slug=project.pypi_slug))
        data = data_client.get()
        if data["response_code"] == 200:
            project.pypi_data = data
            project.pypi_data_date = datetime.datetime.now()

    try:
        pypi_info = project.pypi_data["response_data"]["info"]
    except KeyError:
        raise LimelightError("project.pypi_data has the wrong structure")

    project.title = pypi_info.get("name", None)
    project.description = pypi_info.get("summary", None)
    project.project_url = pypi_info.get("project_url", None)
    project.supported_python = pypi_info.get("requires_python", ">=3.9")
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
    from .sources import PyPiClient, SourcesConfig

    new_project = Project(slug=slug, pypi_slug=slug)
    if fill_data:
        data_client = PyPiClient(SourcesConfig(project_slug=slug))
        new_project.pypi_data = data_client.get()
        new_project.pypi_data_date = datetime.datetime.now()
        new_project = update_pypi_metadata(new_project)
    return new_project


def create_git_project(url, fill_data: bool):
    from flask import current_app

    from .models import Project
    from .sources import GitRepoClient, SourcesConfig

    if match := re.match(
        r"^https://(github|gitlab)\.com/([^/]+/[^/]+?)(?:\.git|/)?$",
        url,
    ):
        platform, repo_path = match.groups()

    new_project = Project(source_url=url, source_slug=f"{platform}:{repo_path}")

    if fill_data:
        data_client = GitRepoClient(
            SourcesConfig(
                project_slug=repo_path.split("/")[1],
                owner_name=repo_path.split("/")[0],
                token=current_app.config[f"{platform.upper()}_TOKEN"],
                git_origin=platform,
            )
        )
        new_project.source_data = data_client.get()
        new_project.source_data_date = datetime.datetime.now()
    return new_project
