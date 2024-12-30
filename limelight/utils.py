import datetime
from typing import Any

import requests
from packaging.specifiers import SpecifierSet
from packaging.version import Version

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
    from .database import db

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
    from click.testing import CliRunner
    from pypinfo.cli import pypinfo

    def run_pypinfo_with_output(args):
        runner = CliRunner()
        result = runner.invoke(pypinfo, ["--auth", "instance/bigquery-auth.json"])

        result = runner.invoke(pypinfo, args)

        if result.exit_code != 0:
            raise RuntimeError(f"Error running pypinfo: {result.output}")

        return result.output

    download_data = run_pypinfo_with_output(["--all", "--json", package, "ci"])
    # import json

    # download_data = json.loads({
    #     "last_update": "2024-12-30 04:25:10",
    #     "query": {
    #         "bytes_billed": 909115392,
    #         "bytes_processed": 908272767,
    #         "cached": false,
    #         "estimated_cost": "0.01"
    #     },
    #     "rows": [
    #         {
    #             "ci": "True",
    #             "download_count": 7954185
    #         },
    #         {
    #             "ci": "None",
    #             "download_count": 6344381
    #         }
    #     ]
    # })
    try:
        return download_data["rows"][1]["download_count"]
    except KeyError:
        return None


def update_project_metadata(project: Any):
    import re

    from .database import db

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


def project_exists(db, slug: str):
    from .models import Project

    p = db.session.execute(db.select(Project).where(Project.slug == slug)).first()
    return True if p else False


def create_project(db, project_info: dict):
    import re

    from .models import Project

    new_project = Project(slug=project_info["slug"])
    if project_info["origen"] == "pypi":
        new_project.pypi_slug = new_project.slug
    elif project_info["origen"] == "anaconda":
        new_project.conda_slug = new_project.slug
    elif project_info["origen"] == "git":
        if match := re.match(
            r"^https://(github|gitlab)\.com/([^/]+/[^/]+?)(?:\.git|/)?$",
            new_project.slug,
        ):
            platform, repo_path = match.groups()
            new_project.source_slug = f"{platform}:{repo_path}"

    db.session.add(new_project)
    db.session.commit()

    return new_project


def guess_git(project_info):
    urls = {
        "bugtrack": project_info.get("bugtrack_url", None),
        "docs": project_info.get("docs_url", None),
        "package": project_info.get("package_url", None),
        "project": project_info.get("project_url", None),
        "release": project_info.get("release_url", None),
    }
    for k, link in project_info.get("project_urls", {}).items():
        urls.update({k: link})

    for k, l in urls.items():
        if k.find("ource") >= 0:
            link = l
            break

    if link.endswith("/"):
        return f"{link[:-1]}.git", link, f"{link[:-1]}.git".replace("https://github.com/", "").replace(".git", "")
    else:
        return f"{link}.git", link, f"{link}.git".replace("https://github.com/", "").replace(".git", "")


def process_pypi_data(project):
    if project.pypi_data:
        project_info = project.pypi_data.get("info", None)

    from .database import db

    if project_info:
        git_repo, repo_url, github_slug = guess_git(project_info)
        project.title = project_info.get("name", None)
        project.description = project_info.get("summary", None)
        project.project_url = project_info.get("project_url", None)
        project.supported_python = expand_requires_python(project_info.get("requires_python"))
        project.source_url = repo_url
        project.git_url = git_repo
        project.docs_url = project_info.get("docs_url", None)

    project.fetch_date_next = project.created_at + datetime.timedelta(days=7)
    github_data = fetch_github_api(github_slug).json()
    project.git_data = github_data
    project.git_data_date = datetime.datetime.now()
    db.session.commit()
    return project
