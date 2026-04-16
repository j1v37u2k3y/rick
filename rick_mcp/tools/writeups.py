"""Writeups tool — browse, read, search, and cite operator write-ups in ~/.rick_mcp/writeups/.

Markdown files nested by category. Tool stays quiet until called (no per-file resources).

Also exposes `cite_writeups()` — a citation helper other tools import to surface
"seen in your writeups" sections alongside theoretical guidance.
"""

import json
import re
import shutil
import subprocess
import time
from pathlib import Path

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import WriteupInput

WRITEUPS_DIR = Path.home() / ".rick_mcp" / "writeups"
INDEX_CACHE_TTL = 24 * 60 * 60  # 24 hours

# Curated canonical tool list for index scanning. Keep in sync with the MCP's stack.
_INDEX_TOOLS = [
    "nmap",
    "burp",
    "ffuf",
    "gobuster",
    "nuclei",
    "sqlmap",
    "hashcat",
    "john",
    "bloodhound",
    "sharphound",
    "responder",
    "impacket",
    "crackmapexec",
    "chisel",
    "ligolo",
    "linpeas",
    "winpeas",
    "metasploit",
    "msfvenom",
    "mimikatz",
    "rubeus",
    "certify",
    "certipy",
    "powerview",
    "kerbrute",
    "evil-winrm",
    "netexec",
    "smbclient",
    "hydra",
    "medusa",
    "wireshark",
    "tcpdump",
    "amass",
    "subfinder",
    "theharvester",
    "whatweb",
    "wfuzz",
    "wpscan",
    "enum4linux",
    "cewl",
    "scoutsuite",
    "prowler",
    "pacu",
    "roadtools",
    "kubectl",
    "kube-hunter",
    "trivy",
    "grype",
    "terraform",
    "nikto",
    "sslscan",
    "testssl",
]
_CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
_MITRE_RE = re.compile(r"\bT\d{4}(?:\.\d{3})?\b")


def _base_dir() -> Path:
    """Return the writeups base directory. Indirected so tests can patch."""
    return WRITEUPS_DIR


def _resolve_safe(base: Path, relative: str) -> Path | None:
    """Resolve a user-supplied relative path against base, rejecting traversal.

    Returns None if the resolved path escapes base or does not exist.
    """
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError:
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


def _first_heading(md_text: str) -> str:
    """Extract the first H1 or H2 from a markdown document."""
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if stripped.startswith("## "):
            return stripped[3:].strip()
    return ""


def _walk_markdown(base: Path, category: str | None = None) -> list[Path]:
    """Walk base directory (optionally filtered to a top-level category). Return .md files sorted."""
    root = base / category if category else base
    if not root.exists() or not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


async def rick_writeups(params: WriteupInput) -> str:
    """Browse and search operator write-ups. Actions: list, read, search."""
    action = (_sanitize(params.action) or "").lower()
    fmt = params.response_format
    base = _base_dir()

    if not base.exists():
        return _fmt(
            {
                "error": f"No writeups directory at {base}",
                "suggestion": f"Create {base} and drop markdown files in. Nest by category, e.g. htb/lame.md.",
            },
            fmt,
            title=f"{CALLSIGN} Writeups",
        )

    if action == "list":
        return _list_writeups(base, params, fmt)
    if action == "read":
        return _read_writeup(base, params, fmt)
    if action == "search":
        return _search_writeups(base, params, fmt)
    if action == "index":
        return _index_writeups(base, params, fmt)

    return _fmt(
        {"error": f"Unknown action '{action}'", "valid": ["list", "read", "search", "index"]},
        fmt,
        title=f"{CALLSIGN} Writeups",
    )


def _list_writeups(base: Path, params: WriteupInput, fmt) -> str:
    category = _sanitize(params.category) if params.category else None
    files = _walk_markdown(base, category)
    if not files:
        return _fmt(
            {
                "base": str(base),
                "category": category or "(all)",
                "writeups": "None found.",
            },
            fmt,
            title=f"{CALLSIGN} Writeups",
        )

    grouped: dict[str, list[dict[str, str]]] = {}
    base_resolved = base.resolve()
    for f in files[: params.limit]:
        try:
            rel = f.resolve().relative_to(base_resolved)
        except ValueError:
            continue
        parts = rel.parts
        top = parts[0] if len(parts) > 1 else "(root)"
        title = _first_heading(f.read_text(encoding="utf-8", errors="replace")[:2000]) or f.stem
        grouped.setdefault(top, []).append(
            {
                "path": str(rel),
                "title": title,
                "size_kb": f"{f.stat().st_size / 1024:.1f}",
            }
        )

    total = sum(len(v) for v in grouped.values())
    truncated = len(files) > params.limit
    return _fmt(
        {
            "base": str(base),
            "total_shown": total,
            "total_available": len(files),
            **({"truncated": f"Showing {params.limit} of {len(files)}"} if truncated else {}),
            "by_category": grouped,
            "rick_note": "Call rick_writeups(action='read', path='<path>') to open one.",
        },
        fmt,
        title=f"{CALLSIGN} Writeups",
    )


def _read_writeup(base: Path, params: WriteupInput, fmt) -> str:
    rel = _sanitize(params.path) if params.path else None
    if not rel:
        return _fmt(
            {"error": "path= is required for read action", "hint": "Use list to find available paths"},
            fmt,
            title=f"{CALLSIGN} Writeups",
        )
    resolved = _resolve_safe(base, rel)
    if resolved is None:
        return _fmt(
            {"error": f"File not found or path escapes writeups directory: {rel}"},
            fmt,
            title=f"{CALLSIGN} Writeups",
        )
    content = resolved.read_text(encoding="utf-8", errors="replace")
    return content


def _search_writeups(base: Path, params: WriteupInput, fmt) -> str:
    query = _sanitize(params.query) if params.query else None
    if not query:
        return _fmt(
            {"error": "query= is required for search action"},
            fmt,
            title=f"{CALLSIGN} Writeups",
        )

    category = _sanitize(params.category) if params.category else None
    search_root = base / category if category else base
    if not search_root.exists():
        return _fmt(
            {"error": f"Category not found: {category}"},
            fmt,
            title=f"{CALLSIGN} Writeups",
        )

    matches = _ripgrep_search(search_root, query, params.limit)
    if matches is None:
        matches = _python_search(search_root, query, params.limit)

    if not matches:
        return _fmt(
            {"query": query, "category": category or "(all)", "matches": "No matches found."},
            fmt,
            title=f"{CALLSIGN} Writeups Search",
        )

    base_resolved = base.resolve()
    formatted: list[dict[str, str]] = []
    for path, line_num, snippet in matches[: params.limit]:
        try:
            rel = Path(path).resolve().relative_to(base_resolved)
        except ValueError:
            rel = Path(path)
        formatted.append(
            {
                "file": str(rel),
                "line": str(line_num),
                "match": snippet.strip()[:300],
            }
        )

    return _fmt(
        {
            "query": query,
            "category": category or "(all)",
            "total": str(len(matches)),
            "results": formatted,
        },
        fmt,
        title=f"{CALLSIGN} Writeups Search",
    )


def _ripgrep_search(root: Path, query: str, limit: int) -> list[tuple[str, int, str]] | None:
    """Run ripgrep. Returns None if rg is not available."""
    rg = shutil.which("rg")
    if not rg:
        return None
    try:
        result = subprocess.run(  # noqa: S603 — rg resolved from PATH via shutil.which
            [
                rg,
                "--no-heading",
                "--line-number",
                "--smart-case",
                "--fixed-strings",
                "--glob",
                "*.md",
                "--max-count",
                str(max(1, limit)),
                query,
                str(root),
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    out: list[tuple[str, int, str]] = []
    for line in result.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        path, line_num_s, snippet = parts
        try:
            line_num = int(line_num_s)
        except ValueError:
            continue
        out.append((path, line_num, snippet))
        if len(out) >= limit:
            break
    return out


def _python_search(root: Path, query: str, limit: int) -> list[tuple[str, int, str]]:
    """Pure-Python fallback search. Substring (case-insensitive)."""
    needle = query.lower()
    out: list[tuple[str, int, str]] = []
    for path in root.rglob("*.md"):
        if not path.is_file():
            continue
        try:
            for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
                if needle in line.lower():
                    out.append((str(path), i, line))
                    if len(out) >= limit:
                        return out
        except OSError:
            continue
    return out


def cite_writeups(term: str, limit: int = 5, base: Path | None = None) -> list[str]:
    """Find writeups that mention `term`. Returns a deduplicated list of relative paths.

    Used by other tools to surface "seen in your writeups" sections alongside theoretical
    guidance. Silent (returns empty list) if no writeups exist or no matches found.
    """
    if not term or not term.strip():
        return []
    root = base if base is not None else _base_dir()
    if not root.exists() or not root.is_dir():
        return []

    matches = _ripgrep_search(root, term.strip(), limit * 4)
    if matches is None:
        matches = _python_search(root, term.strip(), limit * 4)

    base_resolved = root.resolve()
    seen: list[str] = []
    for path, _line, _snippet in matches:
        try:
            rel = str(Path(path).resolve().relative_to(base_resolved))
        except ValueError:
            continue
        if rel not in seen:
            seen.append(rel)
        if len(seen) >= limit:
            break
    return seen


def _index_writeups(base: Path, params: WriteupInput, fmt) -> str:
    """Build or load the corpus index — top tools, CVEs, MITRE IDs, OS breakdown."""
    index = _build_index(base)
    if "error" in index:
        return _fmt(index, fmt, title=f"{CALLSIGN} Writeups Index")
    return _fmt(index, fmt, title=f"{CALLSIGN} Writeups Index")


def _build_index(base: Path) -> dict:
    """Scan all writeups, extract tool/CVE/MITRE mentions. Cached to .index.json (24h TTL)."""
    cache_path = base / ".index.json"
    if cache_path.exists():
        try:
            age = time.time() - cache_path.stat().st_mtime
            if age < INDEX_CACHE_TTL:
                cached: dict = json.loads(cache_path.read_text(encoding="utf-8"))
                return cached
        except (OSError, json.JSONDecodeError):
            pass  # rebuild

    tool_counts: dict[str, int] = {t: 0 for t in _INDEX_TOOLS}
    cve_counts: dict[str, int] = {}
    mitre_counts: dict[str, int] = {}
    os_linux = 0
    os_windows = 0
    total_files = 0
    total_bytes = 0

    for path in base.rglob("*.md"):
        if not path.is_file():
            continue
        total_files += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        total_bytes += len(text.encode("utf-8"))
        lower = text.lower()
        for tool in _INDEX_TOOLS:
            if tool in lower:
                tool_counts[tool] += 1
        for match in _CVE_RE.findall(text):
            key = match.upper()
            cve_counts[key] = cve_counts.get(key, 0) + 1
        for match in _MITRE_RE.findall(text):
            mitre_counts[match] = mitre_counts.get(match, 0) + 1
        if "linux" in lower or "ubuntu" in lower or "debian" in lower or "kali" in lower:
            os_linux += 1
        if "windows" in lower or "active directory" in lower or " ad " in lower:
            os_windows += 1

    top_tools = sorted(((t, c) for t, c in tool_counts.items() if c > 0), key=lambda kv: kv[1], reverse=True)[:20]
    top_cves = sorted(cve_counts.items(), key=lambda kv: kv[1], reverse=True)[:15]
    top_mitre = sorted(mitre_counts.items(), key=lambda kv: kv[1], reverse=True)[:15]

    result = {
        "total_writeups": total_files,
        "total_size_kb": f"{total_bytes / 1024:.1f}",
        "os_breakdown": {
            "linux_mentions": os_linux,
            "windows_mentions": os_windows,
        },
        "top_tools": [{"tool": t, "writeups": str(c)} for t, c in top_tools] or [{"status": "None found"}],
        "cves_referenced": [{"id": cve, "count": str(c)} for cve, c in top_cves] or [{"status": "None found"}],
        "mitre_techniques": [{"id": mid, "count": str(c)} for mid, c in top_mitre] or [{"status": "None found"}],
        "rick_note": "This is your corpus at a glance. The tools you've actually used, the CVEs you've actually exploited.",
    }

    try:
        cache_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except OSError:
        pass  # cache is best-effort

    return result


def register(mcp):
    """Register writeups tool on the MCP server."""
    mcp.tool(
        name="rick_writeups",
        annotations={
            "title": "Operator Writeups",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_writeups))
