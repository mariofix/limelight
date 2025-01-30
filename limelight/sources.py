import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import requests

from .version import __version__


@dataclass
class SourcesConfig:
    project_slug: str
    """Project slug"""
    owner_name: str | None = None
    """user/org"""
    token: str | None = None
    """Required for pepy, github, and gitlab"""
    bq_credentials: Path | None = None
    """BigQuery Credentials path (json format)"""
    git_origin: Literal["github", "gitlab"] | None = None


class BaseApiClient(ABC):
    def __init__(self):
        self._session = requests.Session()
        self.setup_client()

    @abstractmethod
    def setup_client(self) -> None:
        """Configure client-specific setup"""
        pass

    @abstractmethod
    def get(self) -> dict[str, Any]:
        """Make API request and return response data"""
        pass

    def serialize_headers(self, headers: Any) -> dict[str, Any]:
        try:
            return json.dumps(headers)
        except Exception as e:
            print(f"{ e = }")
            print(f"{ headers = }")

        data = []
        for k, d in headers.items():
            try:
                data.append((f"{k}", f"{d}"))
            except Exception as e:
                print(f"{ e = }")

        return data

    def _make_request(self, url: str, headers: dict | None = None, auth: tuple | None = None) -> dict[str, Any]:
        try:
            response = self._session.get(url, headers=headers, auth=auth)
            response.raise_for_status()
            return {
                "request_url": url,
                "request_headers": headers,
                "response_code": response.status_code,
                "response_headers": self.serialize_headers(response.headers),
                "response_data": response.json(),
            }
        except requests.exceptions.RequestException as e:
            return {
                "request_url": url,
                "request_headers": headers,
                "response_code": response.status_code,
                "response_headers": self.serialize_headers(response.headers),
                "response_data": f"{e}",
            }


class PyPiClient(BaseApiClient):
    def __init__(self, config: SourcesConfig):
        self.config = config
        super().__init__()

    def setup_client(self) -> None:
        self.url = f"https://pypi.org/pypi/{self.config.project_slug}/json"

    def get(self) -> dict[str, Any]:
        return self._make_request(self.url)


class GitRepoClient(BaseApiClient):
    def __init__(self, config: SourcesConfig):
        if not config.git_origin:
            raise ValueError("git_origin is required (github, gitlab)")
        if not config.token:
            raise ValueError("Auth token is required")
        if not config.owner_name:
            raise ValueError("Owner name is required")

        self.config = config
        super().__init__()

    def setup_client(self) -> None:
        if self.config.git_origin == "github":
            self.url = f"https://api.github.com/repos/{self.config.owner_name}/{self.config.project_slug}"
            self.headers = {
                "User-Agent": f"limelight/{__version__}",
                "Authorization": f"Bearer {self.config.token}",
                "Accept": "application/vnd.github+json",
            }
        elif self.config.git_origin == "gitlab":
            self.url = f"https://gitlab.com/api/v4/projects/{self.config.owner_name}%2F{self.config.project_slug}"
            self.headers = {
                "Authorization": f"Bearer {self.config.token}",
                "User-Agent": f"limelight/{__version__}",
            }
        else:
            raise NotImplementedError(f"{self.config.git_origin=} not supported yet")

    def get(self) -> dict[str, Any]:
        return self._make_request(self.url, headers=self.headers)

    def get_closed_issues(self) -> int:
        self.url = f"{self.url}/issues?state=closed&per_page=1"
        return self._make_request(self.url, headers=self.headers)


class PepyClient(BaseApiClient):
    def __init__(self, config: SourcesConfig):
        self.config = config
        super().__init__()

    def setup_client(self) -> None:
        self.url = f"https://api.pepy.tech/api/v2/projects/{self.config.project_slug}"
        self.headers = {"X-API-Key": self.config.token}

    def get(self) -> dict[str, Any]:
        return self._make_request(self.url, headers=self.headers)


class BigQueryClient(BaseApiClient):
    def __init__(self, config: SourcesConfig):
        if not config.bq_credentials:
            raise ValueError("BigQuery credentials path is required")

        self.config = config
        super().__init__()

    def setup_client(self) -> None:
        from google.cloud import bigquery

        self.client = bigquery.Client.from_service_account_json(str(self.config.bq_credentials))
        self.project = self.config.project_slug

    def get(self) -> dict[str, Any]:
        try:
            query = f"""
                SELECT *
                FROM `{self.project}.{self.config.dataset}.{self.config.table}`
                LIMIT {self.config.limit}
            """
            return {"data": [dict(row) for row in self.client.query(query)]}
        except Exception as e:
            raise e
