"""Vault integration — bridges rick_mcp with the operator's Obsidian Second Brain at ~/.rick_mcp/vault/.

Mirrors the identity.py pattern: zero internal rick_mcp imports, loads path config at import
time, exposes module-level constants. Fork-friendly — every behavior gated by is_configured().

The vault is for future-Claude retrieval, not human reading. Notes written here follow the
AI-first vault rule: "## For future Claude" preamble, rich frontmatter, recency markers,
[[wikilinks]] for cross-refs, sources verbatim. Canonical spec lives in the vault itself at
~/.rick_mcp/vault/_CLAUDE.md and ~/.claude/skills/obsidian-second-brain/references/ai-first-rules.md.

Per the vault's _CLAUDE.md § Voice & Tone — Rick voice is canonical when identity.is_configured()
is true (since the MCP IS Rick). Voice rules: first person, builder metaphors, USMC precision,
honesty above all. AI-first structural rules apply regardless of voice.

Architectural rule: vault references bedrock; bedrock is never duplicated. The bedrock
(soul/, profiles/, resume/, identity.yaml) is canonical. Vault writes wikilink TO it, not
overwrite FROM it.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("rick_mcp")

# ── Path config (loaded once at import) ─────────────────────────────────────────────────────

VAULT_PATH = Path.home() / ".rick_mcp" / "vault"
ENGAGEMENTS_DIR = VAULT_PATH / "Engagements"
IDENTITY_DIR = VAULT_PATH / "Identity"
TEMPLATES_DIR = VAULT_PATH / "Templates"
DAILY_DIR = VAULT_PATH / "Daily"
DEV_LOGS_DIR = VAULT_PATH / "Dev Logs"
PROJECTS_DIR = VAULT_PATH / "Projects"

CLAUDE_MD = VAULT_PATH / "_CLAUDE.md"
INDEX_MD = VAULT_PATH / "index.md"
LOG_MD = VAULT_PATH / "log.md"


def is_configured() -> bool:
    """Vault is considered configured if VAULT_PATH exists and has _CLAUDE.md (proper bootstrap)."""
    return VAULT_PATH.is_dir() and CLAUDE_MD.is_file()


# ── Path helpers (testable, pure functions) ─────────────────────────────────────────────────


def _vault_path() -> Path:
    """Indirected accessor so tests can patch via Path.home()."""
    return Path.home() / ".rick_mcp" / "vault"


def _engagements_dir() -> Path:
    return _vault_path() / "Engagements"


def _claude_md() -> Path:
    return _vault_path() / "_CLAUDE.md"


def _log_md() -> Path:
    return _vault_path() / "log.md"


def _templates_dir() -> Path:
    return _vault_path() / "Templates"


def _is_configured() -> bool:
    """Re-check at call time (for tests that patch Path.home after import)."""
    vp = _vault_path()
    return vp.is_dir() and (vp / "_CLAUDE.md").is_file()


def slugify(name: str) -> str:
    """Lowercase, hyphenate, ASCII-safe slug for filenames."""
    s = name.lower().replace("@", "at")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "untitled"


def codename_for(client: str, engagement_type: str, date: str | None = None) -> str:
    """Build a vault-safe, human-readable codename for an engagement note.

    Format: '<Client> - <Engagement Type Title> (<YYYY-MM-DD>)'
    """
    d = date or datetime.now().strftime("%Y-%m-%d")
    type_title = engagement_type.replace("_", " ").title()
    safe_client = (client or "Client").replace("/", "-").replace("\\", "-").strip()
    return f"{safe_client} - {type_title} ({d})"


def codename_to_filename(codename: str) -> str:
    """Strip filesystem-unsafe characters from a codename."""
    return codename.replace("/", "-").replace("\\", "-").strip() or "Untitled Engagement"


# ── AI-first frontmatter + preamble builders ─────────────────────────────────────────────────


def _yaml_scalar(v: Any) -> str:
    """Render a YAML scalar — quote when special chars or whitespace require it."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v).lower()
    s = str(v)
    if not s:
        return '""'
    needs_quote = (
        s.strip() != s
        or any(c in s for c in ":#'\"&*?{}[],|>!%@`")
        or s.lower() in ("yes", "no", "true", "false", "null")
    )
    if needs_quote:
        return '"' + s.replace('"', '\\"') + '"'
    return s


def frontmatter(fields: dict[str, Any]) -> str:
    """Build space-padded YAML frontmatter per vault formatting preferences.

    Lists render as inline arrays with internal spacing: ` [ a, b, c ] ` (or `[]` when empty).
    Dicts render as nested mappings. Booleans lowercase. None becomes empty value.
    """
    lines = ["---"]
    for key, value in fields.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                items = ", ".join(_yaml_scalar(v) for v in value)
                lines.append(f"{key}: [ {items} ]")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {_yaml_scalar(v)}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        elif value is None:
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def preamble(text: str) -> str:
    """Build the AI-first '## For future Claude' preamble block.

    The text should be 2-3 sentences in plain English — enough for future-Claude to decide
    relevance in 10 seconds before parsing the rest of the note.
    """
    return f"## For future Claude\n\n{text.strip()}\n"


# ── Engagement-type → vault wikilink mappings ────────────────────────────────────────────────

_TYPE_TO_SPECIALIZATION: dict[str, str | None] = {
    "web_app_pentest": "Web Application Security",
    "network_pentest": "Network Infrastructure Pentesting",
    "ad_review": "Active Directory Attacks",
    "cloud_audit": "Cloud Security",
    "red_team": "Red Team Operations",
    "api_security": "API Security Testing",
    "full_scope": None,  # multi-spec — list several
}

_TYPE_TO_TOOLS: dict[str, list[str]] = {
    "web_app_pentest": ["Burp Suite", "SQLMap", "ffuf", "Gobuster", "Nuclei"],
    "network_pentest": ["Nmap", "Metasploit", "Nuclei", "LinPEAS", "WinPEAS", "Chisel"],
    "ad_review": ["BloodHound", "Impacket", "CrackMapExec", "Responder", "Hashcat", "WinPEAS"],
    "cloud_audit": ["Nmap"],
    "red_team": ["Chisel", "Ligolo-ng", "Impacket", "BloodHound", "CrackMapExec"],
    "api_security": ["Burp Suite", "ffuf", "Nuclei"],
    "full_scope": ["Nmap", "Burp Suite", "Metasploit", "BloodHound", "Impacket", "Hashcat"],
}


def specialization_wikilink(engagement_type: str) -> str:
    """Return a vault wikilink for the engagement type's primary specialization, or '' if unmapped."""
    spec = _TYPE_TO_SPECIALIZATION.get(engagement_type)
    if not spec:
        return ""
    return f"[[Identity/Specializations/{spec}]]"


def tools_wikilinks(engagement_type: str) -> list[str]:
    """Return wikilinks for the engagement type's default toolset."""
    tools = _TYPE_TO_TOOLS.get(engagement_type, [])
    return [f"[[Identity/Tools/{t}]]" for t in tools]


# ── Write helpers ────────────────────────────────────────────────────────────────────────────


def write_engagement(
    codename: str,
    *,
    client: str,
    engagement_type: str,
    body: str,
    status: str = "scoping",
    overwrite: bool = False,
) -> tuple[Path, bool] | None:
    """Write a vault/Engagements/<codename>.md note.

    Returns (path, created) where created=True if a new file was written, False if it already
    existed (and was preserved). Returns None if the vault is not configured.

    Default behavior is non-destructive: if the file exists, returns (path, False) without
    overwriting. Pass overwrite=True to refresh the canonical note.
    """
    if not _is_configured():
        return None

    eng_dir = _engagements_dir()
    eng_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{codename_to_filename(codename)}.md"
    target = eng_dir / filename

    if target.exists() and not overwrite:
        logger.info(f"Vault engagement exists — preserved: {target}")
        return target, False

    today = datetime.now().strftime("%Y-%m-%d")
    fm_fields: dict[str, Any] = {
        "date": today,
        "updated": today,
        "type": "engagement",
        "tags": ["engagement", engagement_type.replace("_", "-")],
        "client": client,
        "codename": codename,
        "engagement-type": engagement_type,
        "status": status,
        "ai-first": True,
    }

    pre_text = (
        f"Engagement note for {codename}. Created {today} by `rick_engagement_proposal`. "
        f"Status: {status}. Captures scope, methodology, timeline, deliverables, and terms. "
        f"Methodology grounded in [[Identity/Methodology]] (Rick's 7-phase: PTES + OWASP + "
        f"MITRE ATT&CK). Updated by subsequent rick_mcp engagement tool calls (debrief, "
        f"tracker, scoping)."
    )

    content = frontmatter(fm_fields) + "\n\n" + preamble(pre_text) + "\n" + body.rstrip() + "\n"
    target.write_text(content, encoding="utf-8")
    logger.info(f"Vault engagement created: {target}")
    return target, True


def append_engagement_section(
    codename: str,
    *,
    section_heading: str,
    section_body: str,
) -> Path | None:
    """Append a section to an existing vault/Engagements/<codename>.md note.

    Used by debrief, scoping refresh, ROE updates. Returns the target path on success, or None
    if the vault is not configured / file doesn't exist.
    """
    if not _is_configured():
        return None

    filename = f"{codename_to_filename(codename)}.md"
    target = _engagements_dir() / filename
    if not target.exists():
        logger.info(f"Vault engagement note not found for append: {target}")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    existing = target.read_text(encoding="utf-8")
    addition = f"\n\n## {section_heading}\n\n_Updated {today}._\n\n{section_body.rstrip()}\n"
    target.write_text(existing.rstrip() + addition + "\n", encoding="utf-8")
    logger.info(f"Vault engagement appended: {target} § {section_heading}")
    return target


def append_log_entry(action: str, description: str) -> bool:
    """Append a dated entry to vault/log.md. Returns True on success, False if vault not configured."""
    if not _is_configured():
        return False
    log_path = _log_md()
    if not log_path.exists():
        return False
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n## [{today}] {action} | {description}\n\n---\n"
    existing = log_path.read_text(encoding="utf-8")
    log_path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
    return True


def relative_path(p: Path) -> str:
    """Return a vault-relative path string, or absolute if outside the vault."""
    try:
        return str(p.relative_to(_vault_path()))
    except ValueError:
        return str(p)


def list_engagements() -> list[Path]:
    """List vault engagement note paths (sorted). Empty list if vault not configured."""
    if not _is_configured():
        return []
    eng_dir = _engagements_dir()
    if not eng_dir.exists():
        return []
    return sorted(p for p in eng_dir.glob("*.md") if p.is_file())


def read_template(name: str) -> str | None:
    """Read a vault template by name (e.g. 'Engagement'). None if vault unconfigured / missing."""
    if not _is_configured():
        return None
    target = _templates_dir() / f"{name}.md"
    if not target.exists():
        return None
    return target.read_text(encoding="utf-8")


def status() -> dict[str, Any]:
    """Return a vault status dict — used by rick_capabilities, rick_health.

    Always safe to call; degrades to {configured: False, ...} if vault missing.
    """
    configured = _is_configured()
    if not configured:
        return {
            "configured": False,
            "path": str(_vault_path()),
            "engagements_count": 0,
            "templates_present": [],
        }
    eng_count = len(list_engagements())
    tdir = _templates_dir()
    templates = sorted(p.stem for p in tdir.glob("*.md")) if tdir.exists() else []
    identity_dir = _vault_path() / "Identity"
    identity_present = identity_dir.is_dir()
    return {
        "configured": True,
        "path": str(_vault_path()),
        "engagements_count": eng_count,
        "templates_present": templates,
        "identity_layer_present": identity_present,
    }
