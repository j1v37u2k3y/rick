"""Identity loading system. Reads operator identity from ~/.rick_mcp/identity.yaml at import time.

This module has ZERO internal rick_mcp imports to avoid circular dependencies.
All personal identity lives outside the codebase in ~/.rick_mcp/.
"""

import logging
from pathlib import Path

logger = logging.getLogger("rick_mcp")

IDENTITY_PATH = Path.home() / ".rick_mcp" / "identity.yaml"

DEFAULTS: dict = {
    "callsign": "operator",
    "name": "Operator",
    "title": "Security Engineer",
    "years_experience": 0,
    "military": {},
    "education": {},
    "certifications": [],
    "languages": ["Python"],
    "primary_tools": ["Burp Suite", "Nmap", "Metasploit"],
    "specializations": ["Security Testing"],
    "location": "",
    "website": "",
    "family": "",
    "motto": "",
    "tagline": "Security through craftsmanship.",
    "aliases": [],
    "background_story": "",
    "highlights": {},
}


def _load_identity() -> dict:
    """Load identity from YAML file, falling back to defaults."""
    if not IDENTITY_PATH.exists():
        logger.info("No identity.yaml found — using generic defaults.")
        return dict(DEFAULTS)

    try:
        import yaml  # type: ignore[import-untyped]

        raw = yaml.safe_load(IDENTITY_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            logger.warning("identity.yaml is not a dict — using defaults.")
            return dict(DEFAULTS)

        merged = dict(DEFAULTS)
        merged.update(raw)
        logger.info(f"Identity loaded: {merged.get('callsign', 'operator')}")
        return merged

    except ImportError:
        logger.warning("pyyaml not installed — using generic defaults.")
        return dict(DEFAULTS)
    except Exception as e:
        logger.warning(f"Error loading identity.yaml: {e} — using defaults.")
        return dict(DEFAULTS)


# Load once at import time
_identity = _load_identity()

# Module-level exports — these are what the rest of the codebase imports
CALLSIGN: str = _identity["callsign"]
NAME: str = _identity["name"]
TITLE: str = _identity["title"]
YEARS_EXPERIENCE: int = _identity.get("years_experience", 0)
MILITARY: dict = _identity.get("military", {})
EDUCATION: dict = _identity.get("education", {})
CERTIFICATIONS: list[str] = _identity.get("certifications", [])
LANGUAGES: list[str] = _identity.get("languages", ["Python"])
PRIMARY_TOOLS: list[str] = _identity.get("primary_tools", ["Burp Suite", "Nmap", "Metasploit"])
SPECIALIZATIONS: list[str] = _identity.get("specializations", ["Security Testing"])
LOCATION: str = _identity.get("location", "")
WEBSITE: str = _identity.get("website", "")
FAMILY: str = _identity.get("family", "")
MOTTO: str = _identity.get("motto", "")
TAGLINE: str = _identity.get("tagline", "Security through craftsmanship.")
ALIASES: list[str] = _identity.get("aliases", [])
BACKGROUND_STORY: str = _identity.get("background_story", "")
HIGHLIGHTS: dict = _identity.get("highlights", {})


def is_configured() -> bool:
    """Check if a custom identity is loaded (not generic defaults)."""
    return CALLSIGN != "operator"


def signature_line() -> str:
    """Build a signature line from identity config."""
    parts = [NAME]
    if CALLSIGN != "operator":
        parts[0] = f"{NAME} — {CALLSIGN}"
    if CERTIFICATIONS:
        parts.append(" | ".join(CERTIFICATIONS[:3]))
    if WEBSITE:
        parts.append(WEBSITE)
    return "\n".join(parts)


def bio_summary() -> str:
    """Build a one-paragraph bio from identity config."""
    if not is_configured():
        return "Security professional using the Rick MCP platform."

    parts = [f"{NAME} ({CALLSIGN})"]
    if TITLE:
        parts.append(f"— {TITLE}")
    if YEARS_EXPERIENCE:
        parts.append(f"with {YEARS_EXPERIENCE}+ years of experience.")
    if CERTIFICATIONS:
        parts.append(f"Certifications: {', '.join(CERTIFICATIONS)}.")
    if MILITARY:
        branch = MILITARY.get("branch", "")
        role = MILITARY.get("role", "")
        if branch:
            parts.append(f"{branch} veteran" + (f" ({role})" if role else "") + ".")
    if SPECIALIZATIONS:
        parts.append(f"Specializing in: {', '.join(SPECIALIZATIONS[:4])}.")
    return " ".join(parts)
