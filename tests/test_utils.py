"""Tests for utility functions."""

import pytest

from limelight.utils import find_source_slug, get_package_details, parse_requirement


class TestParseRequirement:
    def test_simple(self):
        result = parse_requirement("flask>=2.0")
        assert result["name"] == "flask"
        assert ">=2.0" in result["specifier"]
        assert result["extras"] == []

    def test_with_extras(self):
        result = parse_requirement("flask[async]>=2.0")
        assert result["name"] == "flask"
        assert "async" in result["extras"]

    def test_no_version(self):
        result = parse_requirement("flask")
        assert result["name"] == "flask"
        assert result["specifier"] is None

    def test_invalid_falls_back(self):
        result = parse_requirement("!!!invalid!!!")
        assert result["specifier"] is None
        assert result["version_specs"] == []

    def test_strips_whitespace(self):
        result = parse_requirement("  flask>=2.0  ")
        assert result["name"] == "flask"


class TestGetPackageDetails:
    def test_found(self):
        result = get_package_details("flask", ["flask>=2.0", "requests>=2.0"])
        assert result["name"] == "flask"
        assert ">=2.0" in result["version"]

    def test_case_insensitive(self):
        result = get_package_details("Flask", ["flask>=2.0"])
        assert result["name"] == "flask"

    def test_not_found_returns_default(self):
        result = get_package_details("nonexistent", ["flask>=2.0"])
        assert result["name"] == "Flask"
        assert result["version"] == ">=3.0"

    def test_empty_requires_dist(self):
        result = get_package_details("flask", [])
        assert result["name"] == "Flask"

    def test_none_requires_dist(self):
        result = get_package_details("flask", None)
        assert result["name"] == "Flask"


class TestFindSourceSlug:
    def test_github(self):
        assert find_source_slug("https://github.com/pallets/flask") == "github:pallets/flask"

    def test_github_with_git_suffix(self):
        assert find_source_slug("https://github.com/pallets/flask.git") == "github:pallets/flask"

    def test_gitlab(self):
        assert find_source_slug("https://gitlab.com/user/repo") == "gitlab:user/repo"

    def test_not_a_git_url(self):
        assert find_source_slug("https://example.com/not-git") is None

    def test_none(self):
        assert find_source_slug(None) is None

    def test_empty_string(self):
        assert find_source_slug("") is None
