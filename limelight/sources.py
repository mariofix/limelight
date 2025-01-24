from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .version import __version__


@dataclass
class SourcesConfig:
    project_slug: str
    """Project slug"""
    owner_name: Optional[str] = None
    """user/org"""
    token: Optional[str] = None
    """Required for pepy, github, and gitlab"""
    bq_credentials: Optional[Path] = None
    """BigQuery Credentials path (json format)"""


class BaseApiClient(ABC):
    def __init__(self):
        self._session = requests.Session()
        self.setup_client()

    @abstractmethod
    def setup_client(self) -> None:
        """Configure client-specific setup"""
        pass

    @abstractmethod
    def get(self) -> Dict[str, Any]:
        """Make API request and return response data"""
        pass

    def _make_request(self, url: str, headers: Optional[Dict] = None, auth: Optional[tuple] = None) -> Dict[str, Any]:
        try:
            response = self._session.get(url, headers=headers, auth=auth)
            response.raise_for_status()
            return {
                "request_url": url,
                "request_headers": headers,
                "response_code": response.status_code,
                "response_headers": None,
                "response_data": response.json(),
            }
        except requests.exceptions.RequestException as e:
            return {
                "request_url": url,
                "request_headers": headers,
                "response_code": response.status_code,
                "response_headers": None,
                "response_data": f"{e}",
            }


class PyPiClient(BaseApiClient):
    def __init__(self, config: SourcesConfig):
        self.config = config
        super().__init__()

    def setup_client(self) -> None:
        self.url = f"https://pypi.org/pypi/{self.config.project_slug}/json"

    def get(self) -> Dict[str, Any]:
        return self._make_request(self.url)


class GithubClient(BaseApiClient):
    def __init__(self, config: SourcesConfig):
        if not config.token:
            raise ValueError("GitHub token is required")
        if not config.owner_name:
            raise ValueError("Owner name is required for GitHub")

        self.config = config
        super().__init__()

    def setup_client(self) -> None:
        self.url = f"https://api.github.com/repos/{self.config.owner_name}/{self.config.project_slug}"
        self.headers = {
            "User-Agent": f"limelight/{__version__}",
            "Authorization": f"Bearer {self.config.token}",
            "Accept": "application/vnd.github+json",
        }

    def get(self) -> Dict[str, Any]:
        return self._make_request(self.url, headers=self.headers)


class GitlabClient(BaseApiClient):
    def __init__(self, config: SourcesConfig):
        if not config.token:
            raise ValueError("GitLab token is required")
        if not config.owner_name:
            raise ValueError("Owner name is required for GitLab")

        self.config = config
        super().__init__()

    def setup_client(self) -> None:
        self.url = f"https://gitlab.com/api/v4/projects/{self.config.owner_name}%2F{self.config.project_slug}"
        self.headers = {"Authorization": f"Bearer {self.config.token}"}

    def get(self) -> Dict[str, Any]:
        return self._make_request(self.url, headers=self.headers)


class PepyClient(BaseApiClient):
    def __init__(self, config: SourcesConfig):
        self.config = config
        super().__init__()

    def setup_client(self) -> None:
        self.url = f"https://api.pepy.tech/api/v2/projects/{self.config.project_slug}"
        self.headers = {"X-API-Key": self.config.token}

    def get(self) -> Dict[str, Any]:
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

    def get(self) -> Dict[str, Any]:
        try:
            query = f"""
                SELECT *
                FROM `{self.project}.{self.config.dataset}.{self.config.table}`
                LIMIT {self.config.limit}
            """
            return {"data": [dict(row) for row in self.client.query(query)]}
        except Exception as e:
            raise e
