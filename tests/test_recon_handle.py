"""
Tests for rick_recon_handle — OSINT against a hacker handle.
Mirrors the rick_cve test pattern: mocked urlopen, cache patches, format coverage.
Reference handle throughout: j1v37u2k3y (the operator).
"""

import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from rick_mcp import ReconHandleInput, ResponseFormat, rick_recon_handle

REF_HANDLE = "j1v37u2k3y"


def _opener(payload):
    """Build a context-manager mock that returns the given JSON payload from .read()."""
    m = MagicMock()
    m.__enter__ = lambda s: s
    m.__exit__ = lambda s, *a: None
    m.read.return_value = json.dumps(payload).encode()
    return m


def _github_user_payload(handle=REF_HANDLE):
    return {
        "login": handle,
        "name": "Tom",
        "bio": "Offensive Security Engineer | OSCP | USMC",
        "location": "Maryland",
        "company": "@offsec",
        "blog": "https://example.com",
        "html_url": f"https://github.com/{handle}",
        "public_repos": 42,
        "followers": 100,
        "created_at": "2010-01-01T00:00:00Z",
    }


def _github_repos_payload():
    return [
        {
            "name": "rick_mcp",
            "stargazers_count": 5,
            "description": "MCP server",
            "html_url": "https://github.com/x/rick_mcp",
            "language": "Python",
            "fork": False,
        },
        {
            "name": "go_tool",
            "stargazers_count": 2,
            "description": "tool",
            "html_url": "https://github.com/x/go_tool",
            "language": "Go",
            "fork": False,
        },
    ]


def _github_events_payload():
    return [
        {"type": "PushEvent"},
        {"type": "PushEvent"},
        {"type": "CreateEvent"},
    ]


def _make_dispatcher(*, user_404=False, user_timeout=False, ctftime_payload=None):
    """side_effect dispatcher for urllib.request.urlopen patches."""

    def dispatch(req, *args, **kwargs):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "ctftime.org" in url:
            if ctftime_payload is not None:
                return _opener(ctftime_payload)
            raise urllib.error.URLError("ctftime not expected in this test")
        if "api.github.com/users/" in url:
            if user_timeout:
                raise TimeoutError()
            if "/repos" in url:
                return _opener(_github_repos_payload())
            if "/events/public" in url:
                return _opener(_github_events_payload())
            if user_404:
                raise urllib.error.HTTPError(url=url, code=404, msg="Not Found", hdrs=None, fp=None)
            return _opener(_github_user_payload())
        raise urllib.error.URLError(f"unexpected URL: {url}")

    return dispatch


# ═══════════════════════════════════════════════════════════════
#  Input model validation
# ═══════════════════════════════════════════════════════════════


class TestReconHandleInput:
    def test_validation_empty_handle(self):
        with pytest.raises(ValidationError):
            ReconHandleInput(handle="")

    def test_validation_handle_too_long(self):
        with pytest.raises(ValidationError):
            ReconHandleInput(handle="a" * 101)

    def test_validation_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            ReconHandleInput(handle=REF_HANDLE, unexpected="nope")

    def test_validation_ctftime_id_must_be_positive(self):
        with pytest.raises(ValidationError):
            ReconHandleInput(handle=REF_HANDLE, ctftime_id=0)

    def test_default_format_is_json(self):
        m = ReconHandleInput(handle=REF_HANDLE)
        assert m.response_format == ResponseFormat.JSON


# ═══════════════════════════════════════════════════════════════
#  Tool behavior — happy path, error paths, cache
# ═══════════════════════════════════════════════════════════════


class TestRickReconHandle:
    @pytest.mark.asyncio
    async def test_github_success(self):
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            mock_urlopen.side_effect = _make_dispatcher()
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE))
            parsed = json.loads(result)
            assert parsed["handle"] == REF_HANDLE
            assert parsed["github"]["found"] is True
            assert parsed["github"]["public_repos"] == 42
            assert isinstance(parsed["github"]["top_repos"], list)
            assert "Python" in parsed["github"]["top_languages"]
            assert parsed["authorization"].startswith("AUTHORIZED")
            assert "search_pivots" in parsed
            assert "hackerone" in parsed["search_pivots"]

    @pytest.mark.asyncio
    async def test_github_404_returns_pivots(self):
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            mock_urlopen.side_effect = _make_dispatcher(user_404=True)
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE))
            parsed = json.loads(result)
            assert parsed["github"]["found"] is False
            assert "search_pivots" in parsed
            assert REF_HANDLE in parsed["search_pivots"]["hackerone"]

    @pytest.mark.asyncio
    async def test_github_timeout_graceful(self):
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            mock_urlopen.side_effect = _make_dispatcher(user_timeout=True)
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE))
            parsed = json.loads(result)
            assert parsed["github"]["found"] is False
            assert "search_pivots" in parsed
            assert "hackthebox" in parsed

    @pytest.mark.asyncio
    async def test_url_error_graceful(self):
        def fail(*a, **kw):
            raise urllib.error.URLError("connection refused")

        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen", side_effect=fail),
        ):
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE))
            parsed = json.loads(result)
            assert parsed["github"]["found"] is False
            assert "search_pivots" in parsed

    @pytest.mark.asyncio
    async def test_cache_hit_skips_network(self):
        cached = [
            _github_user_payload(),
            _github_repos_payload(),
            _github_events_payload(),
        ]
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", side_effect=cached),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE))
            parsed = json.loads(result)
            assert parsed["github"]["found"] is True
            assert parsed.get("cached") is True
            mock_urlopen.assert_not_called()

    @pytest.mark.asyncio
    async def test_ctftime_id_provided(self):
        ctftime_data = {
            "id": 12345,
            "team_name": "infosec_legends",
            "ranking": 42,
        }
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            mock_urlopen.side_effect = _make_dispatcher(ctftime_payload=ctftime_data)
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE, ctftime_id=12345))
            parsed = json.loads(result)
            ct = parsed["ctftime"]
            assert ct.get("ranking") == 42 or ct.get("team") == "infosec_legends"

    @pytest.mark.asyncio
    async def test_ctftime_id_absent_returns_search_url(self):
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            mock_urlopen.side_effect = _make_dispatcher()
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE))
            parsed = json.loads(result)
            assert "ctftime" in parsed
            assert "ctftime.org" in str(parsed["ctftime"])

    @pytest.mark.asyncio
    async def test_search_pivots_complete(self):
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            mock_urlopen.side_effect = _make_dispatcher()
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE))
            parsed = json.loads(result)
            pivots = parsed["search_pivots"]
            for key in [
                "hackerone",
                "bugcrowd",
                "mastodon_infosec",
                "google_blogs",
                "google_conf_talks",
                "linkedin_search",
            ]:
                assert key in pivots
                assert REF_HANDLE in pivots[key]

    @pytest.mark.asyncio
    async def test_markdown_format(self):
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            mock_urlopen.side_effect = _make_dispatcher()
            result = await rick_recon_handle(
                ReconHandleInput(handle=REF_HANDLE, response_format=ResponseFormat.MARKDOWN)
            )
            assert REF_HANDLE in result
            assert "#" in result

    @pytest.mark.asyncio
    async def test_authorization_in_output(self):
        with (
            patch("rick_mcp.tools.recon_handle._cache_get", return_value=None),
            patch("rick_mcp.tools.recon_handle._cache_set"),
            patch("urllib.request.urlopen") as mock_urlopen,
        ):
            mock_urlopen.side_effect = _make_dispatcher()
            result = await rick_recon_handle(ReconHandleInput(handle=REF_HANDLE))
            parsed = json.loads(result)
            assert "authorization" in parsed
            assert "AUTHORIZED" in parsed["authorization"]
            assert "harm" in parsed["authorization"].lower()
