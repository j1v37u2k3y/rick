"""NVD CVE lookup tool with file-based caching."""

import hashlib
import json
import time
from pathlib import Path

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import CVEInput

CACHE_DIR = Path.home() / ".rick_mcp" / "cve_cache"
CACHE_TTL = 86400  # 24 hours


def _cache_key(url: str) -> str:
    """Generate a deterministic cache key from a URL."""
    return hashlib.sha256(url.encode()).hexdigest()


def _cache_get(key: str) -> dict | None:
    """Retrieve cached response if fresh."""
    path = CACHE_DIR / f"{key}.json"
    if path.exists() and (time.time() - path.stat().st_mtime) < CACHE_TTL:
        try:
            result: dict = json.loads(path.read_text(encoding="utf-8"))
            return result
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _cache_set(key: str, data: dict) -> None:
    """Store API response in cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(data), encoding="utf-8")


async def rick_cve(params: CVEInput) -> str:
    """Query the NVD API for CVE details. Lookup by CVE ID or search by keyword. Results cached 24h."""
    import urllib.parse
    import urllib.request

    query = _sanitize(params.query) or ""
    max_results = params.max_results or 5
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    # Determine if this is a CVE ID lookup or keyword search
    if query.upper().startswith("CVE-"):
        url = f"{base_url}?cveId={urllib.parse.quote(query.upper())}"
    else:
        url = f"{base_url}?keywordSearch={urllib.parse.quote(query)}&resultsPerPage={max_results}"

    # Validate scheme before opening
    if not url.startswith("https://"):
        return "Error: URL scheme must be HTTPS."

    # Check cache first
    cache_k = _cache_key(url)
    data = _cache_get(cache_k)

    if data is None:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rick_mcp/1.0"})  # noqa: S310
            with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
                data = json.loads(resp.read().decode("utf-8"))
            _cache_set(cache_k, data)
        except urllib.error.HTTPError as e:
            return f"Error: NVD API returned HTTP {e.code}. Rate limit is 5 requests/30s without API key."
        except urllib.error.URLError as e:
            return f"Error: Could not reach NVD API: {e.reason}"
        except TimeoutError:
            return "Error: NVD API request timed out (15s limit)."

    vulns = data.get("vulnerabilities", [])
    if not vulns:
        return f"No CVEs found for query: {query}"

    results: list[dict] = []
    for item in vulns[:max_results]:
        cve = item.get("cve", {})
        cve_id = cve.get("id", "Unknown")
        descriptions = cve.get("descriptions", [])
        desc = next((d["value"] for d in descriptions if d.get("lang") == "en"), "No description available.")

        # Extract CVSS score
        metrics = cve.get("metrics", {})
        cvss_score = "N/A"
        severity = "N/A"
        for version_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            if version_key in metrics and metrics[version_key]:
                cvss_data = metrics[version_key][0].get("cvssData", {})
                cvss_score = str(cvss_data.get("baseScore", "N/A"))
                severity = cvss_data.get("baseSeverity", "N/A")
                break

        # Extract CWEs
        weaknesses = cve.get("weaknesses", [])
        cwes = []
        for w in weaknesses:
            for desc_item in w.get("description", []):
                if desc_item.get("value", "").startswith("CWE-"):
                    cwes.append(desc_item["value"])

        # Extract references (first 3)
        refs = cve.get("references", [])
        ref_urls = [r.get("url", "") for r in refs[:3]]

        results.append(
            {
                "cve_id": cve_id,
                "description": desc[:300] + ("..." if len(desc) > 300 else ""),
                "cvss_score": cvss_score,
                "severity": severity,
                "cwes": cwes or ["None listed"],
                "references": ref_urls or ["None listed"],
            }
        )

    output = {
        "query": query,
        "total_results": data.get("totalResults", len(results)),
        "showing": len(results),
        "results": results,
        "rate_limit_note": "NVD API: 5 requests/30s without API key. 50 requests/30s with key.",
        "authorization": "AUTHORIZED RESEARCH ONLY",
    }
    return _fmt(output, params.response_format, title=f"{CALLSIGN} CVE Lookup")


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_cve",
        annotations={
            "title": "NVD CVE Lookup",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )(_safe_tool(rick_cve))
