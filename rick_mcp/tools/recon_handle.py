"""Handle OSINT — profile a hacker handle from public sources.

Soul-bounded: public data only, graceful degrade, no doxxing, no paid brokers.
GitHub is the load-bearing wall; CTFTime/HTB return URLs unless IDs/tokens provided.
"""

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import ReconHandleInput

CACHE_DIR = Path.home() / ".rick_mcp" / "handle_cache"
CACHE_TTL = 86400  # 24 hours
HTTP_TIMEOUT = 15


def _cache_key(url: str) -> str:
    """Deterministic cache key from a URL."""
    return hashlib.sha256(url.encode()).hexdigest()


def _cache_get(key: str) -> Any:
    """Return cached value if fresh, else None."""
    path = CACHE_DIR / f"{key}.json"
    if path.exists() and (time.time() - path.stat().st_mtime) < CACHE_TTL:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _cache_set(key: str, data: Any) -> None:
    """Persist value to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(data), encoding="utf-8")


def _fetch_json(url: str, token: str | None = None) -> tuple[Any, bool]:
    """Fetch a JSON URL. Returns (data, cache_hit). Raises on network/HTTP errors."""
    if not url.startswith("https://"):
        raise ValueError("URL scheme must be HTTPS")

    cache_k = _cache_key(url)
    cached = _cache_get(cache_k)
    if cached is not None:
        return cached, True

    headers: dict[str, str] = {
        "User-Agent": "rick_mcp/1.0",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)  # noqa: S310
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:  # noqa: S310
        data = json.loads(resp.read().decode("utf-8"))
    _cache_set(cache_k, data)
    return data, False


def _fetch_github(handle: str, token: str | None) -> dict[str, Any]:
    """Fetch GitHub profile, repos, and recent events. Best-effort on the latter two."""
    h = urllib.parse.quote(handle, safe="")
    base = f"https://api.github.com/users/{h}"
    user_url = base
    repos_url = f"{base}/repos?sort=updated&per_page=10"
    events_url = f"{base}/events/public"

    try:
        user, c_user = _fetch_json(user_url, token)
    except urllib.error.HTTPError as e:
        return {
            "found": False,
            "error": f"GitHub HTTP {e.code}" + (" — not found" if e.code == 404 else ""),
        }
    except (urllib.error.URLError, TimeoutError) as e:
        return {"found": False, "error": f"GitHub unreachable: {getattr(e, 'reason', e)}"}
    except (ValueError, json.JSONDecodeError) as e:
        return {"found": False, "error": f"GitHub error: {e}"}

    repos: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    c_repos = False
    c_events = False
    try:
        repos, c_repos = _fetch_json(repos_url, token)
    except Exception:  # noqa: BLE001 — best-effort enrichment
        repos = []
    try:
        events, c_events = _fetch_json(events_url, token)
    except Exception:  # noqa: BLE001 — best-effort enrichment
        events = []

    # Aggregate non-fork repo languages
    lang_counts: dict[str, int] = {}
    for r in repos or []:
        if isinstance(r, dict) and r.get("language") and not r.get("fork"):
            lang_counts[r["language"]] = lang_counts.get(r["language"], 0) + 1
    top_languages = sorted(lang_counts.keys(), key=lambda k: -lang_counts[k])[:5]

    top_repos: list[dict[str, Any]] = []
    sorted_repos = sorted(
        [r for r in (repos or []) if isinstance(r, dict)],
        key=lambda x: -(x.get("stargazers_count") or 0),
    )[:5]
    for r in sorted_repos:
        top_repos.append(
            {
                "name": r.get("name"),
                "stars": r.get("stargazers_count", 0),
                "description": r.get("description"),
                "url": r.get("html_url"),
                "language": r.get("language"),
            }
        )

    return {
        "found": True,
        "profile_url": user.get("html_url"),
        "name": user.get("name"),
        "bio": user.get("bio"),
        "location": user.get("location"),
        "company": user.get("company"),
        "blog": user.get("blog"),
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "created_at": user.get("created_at"),
        "top_languages": top_languages,
        "top_repos": top_repos,
        "recent_activity_count": len(events or []),
        "_cached": bool(c_user and c_repos and c_events),
    }


def _build_ctftime(handle: str, ctftime_id: int | None) -> dict[str, Any]:
    """Direct API enrichment if ID provided; otherwise a search URL."""
    if ctftime_id:
        url = f"https://ctftime.org/api/v1/users/{ctftime_id}/"
        try:
            data, _ = _fetch_json(url)
            return {
                "id": ctftime_id,
                "profile_url": f"https://ctftime.org/user/{ctftime_id}",
                "team": data.get("team_name"),
                "ranking": data.get("ranking"),
            }
        except Exception as e:  # noqa: BLE001
            return {
                "id": ctftime_id,
                "profile_url": f"https://ctftime.org/user/{ctftime_id}",
                "error": f"CTFTime enrichment failed: {e}",
            }
    h = urllib.parse.quote(handle, safe="")
    return {
        "search_url": f"https://ctftime.org/team/list/?q={h}",
        "note": "CTFTime requires numeric user ID — pass ctftime_id for direct enrichment",
    }


def _build_hackthebox(handle: str) -> dict[str, str]:
    """HTB profile URL — programmatic enrichment requires API token."""
    h = urllib.parse.quote(handle, safe="")
    return {
        "profile_url": f"https://app.hackthebox.com/profile/{h}",
        "note": "HTB profiles require API token to enrich programmatically",
    }


def _build_search_pivots(handle: str) -> dict[str, str]:
    """URLs only — no scraping. Operator follows the threads they care about."""
    h = urllib.parse.quote(handle, safe="")
    return {
        "hackerone": f"https://hackerone.com/{h}",
        "bugcrowd": f"https://bugcrowd.com/{h}",
        "mastodon_infosec": f"https://infosec.exchange/@{h}",
        "google_blogs": f"https://www.google.com/search?q=%22{h}%22+(blog+OR+writeup)",
        "google_conf_talks": f"https://www.google.com/search?q=%22{h}%22+(defcon+OR+blackhat+OR+derbycon)",
        "linkedin_search": f"https://www.linkedin.com/search/results/people/?keywords={h}",
    }


async def rick_recon_handle(params: ReconHandleInput) -> str:
    """OSINT against a hacker handle. GitHub fetch + pivot URLs to other infosec sources."""
    handle = _sanitize(params.handle) or ""

    github = _fetch_github(handle, params.github_token)
    cached = bool(github.pop("_cached", False))
    ctftime = _build_ctftime(handle, params.ctftime_id)
    hackthebox = _build_hackthebox(handle)
    pivots = _build_search_pivots(handle)

    output = {
        "handle": handle,
        "authorization": "AUTHORIZED OSINT ONLY — public data, do no harm",
        "github": github,
        "ctftime": ctftime,
        "hackthebox": hackthebox,
        "search_pivots": pivots,
        "rick_note": (
            "GitHub is the load-bearing wall — public profile, repos, activity. "
            "CTFTime/HTB return links unless you supply IDs or tokens. "
            "Pivots are doors, not crowbars. Public sources only. The bloodline doesn't stop."
        ),
        "cached": cached,
    }
    return _fmt(output, params.response_format, title=f"{CALLSIGN} Handle Recon — {handle}")


def register(mcp):
    """Register tool on the MCP server."""
    mcp.tool(
        name="rick_recon_handle",
        annotations={
            "title": "Handle OSINT",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )(_safe_tool(rick_recon_handle))
