"""Operator philosophy as machine-readable structures.

Decision-tree framework distilled from SOUL.md, the values profile, and the
JARVIS prompt. Tool outputs read from this module instead of re-parsing prose
at call time.

Two layers of content, two storage strategies:

1. **Operator philosophy (data, not code)** — `core_principles`,
   `decision_filters`, `validation_rules`. These are the operator's voice
   and policy. They live in YAML so they can be overridden without code
   changes. Loaded from `~/.rick_mcp/philosophy.yaml` first, falling back
   to the bundled `rick_mcp/data/philosophy.yaml`.

2. **Structural dispatch tables (code)** — `METHODOLOGY_GATE_KEYWORDS`,
   `ARSENAL_CHAIN`, `STRIDE_PRINCIPLE_ANCHORS`, `STRIDE_FILTER_MAP`,
   `chain_validation` notes. These map STRIDE / scenario keywords to
   slugs and tools. They're framework code-shape, not operator philosophy,
   so they stay in Python where they can evolve with tool refactors.

Helpers:
- `apply_filters(text)` — keyword-based filter matcher
- `infer_methodology_gate(text)` — scenario → mission phase
- `chain_for(text)` — situation → next-tool chain
- `principle_anchors(stride_category)` — STRIDE → principle slugs
- `chain_validation(stride_category)` — STRIDE → chain-framing prose
- `filters_for_stride(stride_category)` — STRIDE → curated filter dicts
"""

import logging
from pathlib import Path

from rick_mcp.constants import MISSION_PHASES

logger = logging.getLogger("rick_mcp")

PHILOSOPHY_OVERRIDE_PATH = Path.home() / ".rick_mcp" / "philosophy.yaml"
PHILOSOPHY_BUNDLED_PATH = Path(__file__).parent / "data" / "philosophy.yaml"


# Last-resort baseline if both YAML files are missing or unparseable.
# Keeps the module importable in pathological environments.
_MINIMAL_DEFAULTS: dict = {
    "core_principles": {
        "do_no_harm": "Authorized scope only. No malicious harm.",
    },
    "decision_filters": [
        {
            "slug": "honesty_above_all",
            "name": "Honesty above all",
            "rule": "No inflated severity. Realistic exploitation viability.",
            "triggers": ["finding", "severity", "report"],
        },
    ],
    "validation_rules": [
        "Authorized targets only — non-negotiable.",
    ],
}


def _load_philosophy() -> dict:
    """Load philosophy YAML with override → bundled → minimal-baseline fallback."""
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("pyyaml not installed — using minimal philosophy defaults.")
        return dict(_MINIMAL_DEFAULTS)

    for path in (PHILOSOPHY_OVERRIDE_PATH, PHILOSOPHY_BUNDLED_PATH):
        if not path.exists():
            continue
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and raw.get("core_principles"):
                logger.info(f"Philosophy loaded from {path}")
                return raw
            logger.warning(f"{path} is malformed — trying next source.")
        except Exception as e:
            logger.warning(f"Error loading {path}: {e} — trying next source.")

    logger.warning("No philosophy YAML found — using minimal defaults.")
    return dict(_MINIMAL_DEFAULTS)


_philosophy = _load_philosophy()

CORE_PRINCIPLES: dict[str, str] = _philosophy["core_principles"]
DECISION_FILTERS: list[dict] = _philosophy["decision_filters"]
VALIDATION_RULES: list[str] = _philosophy["validation_rules"]


# ─── Structural dispatch tables (code, not data) ─────────────────────────────
# These map keywords/categories to slugs and tools. They evolve with tool
# refactors and are the code-shape of the decision tree, not operator voice.

# Scenario keyword → MISSION_PHASES name. First match wins.
METHODOLOGY_GATE_KEYWORDS: list[tuple[tuple[str, ...], str]] = [
    (("recon", "osint", "enum", "discovery", "intelligence", "scout"), "Reconnaissance"),
    (("vuln", "scan", "assess", "audit", "review"), "Vulnerability Assessment"),
    (("exploit", "rce", "injection", "xss", "ssrf", "deserialize"), "Exploitation"),
    (("privesc", "escalation", "suid", "sudo", "kernel", "potato"), "Privilege Escalation"),
    (("lateral", "pivot", "movement", "psexec", "wmiexec", "tunnel"), "Lateral Movement"),
    (("report", "writeup", "document", "evidence"), "Documentation"),
    (("hardening", "remediation", "fix", "harden", "defense", "detect"), "Remediation Strategy"),
]


# Situation keyword groups → chain target tool names. Mirrors prompts.py:686-700.
ARSENAL_CHAIN: list[tuple[tuple[str, ...], list[str]]] = [
    (
        ("web", "http", "api", "application", "xss", "sqli", "injection"),
        ["rick_vuln_assess", "rick_attack_chain"],
    ),
    (
        ("network", "infrastructure", "internal", "port", "smb"),
        ["rick_vuln_assess", "rick_pivot_plan"],
    ),
    (
        ("active directory", "ad ", "domain", "kerberos", "ldap"),
        ["rick_attack_chain", "rick_cheatsheet"],
    ),
    (
        ("cloud", "azure", "aws", "gcp", "kubernetes", "k8s", "container"),
        ["rick_cloud_attack_path", "rick_tool_recommend"],
    ),
    (
        ("password", "credential", "crack", "hash", "brute"),
        ["rick_cheatsheet", "rick_pivot_plan"],
    ),
    (
        ("osint", "recon", "intelligence", "phishing"),
        ["rick_recon", "rick_vuln_assess"],
    ),
    (
        ("wireless", "wifi", "bluetooth", "rfid"),
        ["rick_wireless", "rick_attack_chain"],
    ),
    (
        ("stealth", "evasion", "low-noise", "low noise"),
        ["rick_c2_compare", "rick_detection_rules"],
    ),
]


# STRIDE category → governing CORE_PRINCIPLES slugs. The slugs reference
# operator-defined principles, but the mapping itself is framework taxonomy.
STRIDE_PRINCIPLE_ANCHORS: dict[str, list[str]] = {
    "spoofing": ["integrity_first", "do_no_harm"],
    "tampering": ["integrity_first", "the_craft"],
    "repudiation": ["accountability", "integrity_first"],
    "information_disclosure": ["integrity_first", "do_no_harm"],
    "denial_of_service": ["do_no_harm", "accountability"],
    "elevation_of_privilege": ["do_no_harm", "the_craft", "measure_twice_hack_once"],
}


# STRIDE category → DECISION_FILTERS slugs that govern its branches. Curated
# rather than text-matched: STRIDE vocabulary doesn't always trigger the
# keyword-based apply_filters, but every category still has a deliberate set.
STRIDE_FILTER_MAP: dict[str, list[str]] = {
    "spoofing": ["honesty_above_all", "no_checkbox_compliance"],
    "tampering": ["chain_over_isolation", "builders_eye_first"],
    "repudiation": ["honesty_above_all", "no_checkbox_compliance"],
    "information_disclosure": ["honesty_above_all", "no_checkbox_compliance"],
    "denial_of_service": ["thorough_over_fast", "no_checkbox_compliance"],
    "elevation_of_privilege": ["chain_over_isolation", "thorough_over_fast"],
}


# ─── Helpers ─────────────────────────────────────────────────────────────────


def apply_filters(text: str) -> list[dict]:
    """Return decision filters whose triggers fire on the given text."""
    if not text:
        return []
    haystack = text.lower()
    matched: list[dict] = []
    for f in DECISION_FILTERS:
        if any(trig in haystack for trig in f.get("triggers", [])):
            matched.append({"slug": f["slug"], "name": f["name"], "rule": f["rule"]})
    return matched


def infer_methodology_gate(text: str) -> str:
    """Map a scenario / finding string to a MISSION_PHASES name.

    Falls back to 'Reconnaissance' (the default starting phase) when nothing
    matches.
    """
    default_phase: str = str(MISSION_PHASES[0]["name"])
    if not text:
        return default_phase
    haystack = text.lower()
    for keywords, phase_name in METHODOLOGY_GATE_KEYWORDS:
        if any(k in haystack for k in keywords):
            return phase_name
    return default_phase


def chain_for(text: str) -> list[str]:
    """Return next-step tool names for a situation string, de-duplicated."""
    if not text:
        return []
    haystack = text.lower()
    chain: list[str] = []
    for keywords, targets in ARSENAL_CHAIN:
        if any(k in haystack for k in keywords):
            for t in targets:
                if t not in chain:
                    chain.append(t)
    return chain


def principle_anchors(stride_category: str) -> list[str]:
    """Return the CORE_PRINCIPLES slugs governing a STRIDE category."""
    return STRIDE_PRINCIPLE_ANCHORS.get(stride_category.lower().strip(), [])


def filters_for_stride(stride_category: str) -> list[dict]:
    """Return the curated DECISION_FILTERS dicts that govern a STRIDE category."""
    slugs = STRIDE_FILTER_MAP.get(stride_category.lower().strip(), [])
    by_slug = {f["slug"]: f for f in DECISION_FILTERS}
    return [{"slug": s, "name": by_slug[s]["name"], "rule": by_slug[s]["rule"]} for s in slugs if s in by_slug]


def chain_validation(stride_category: str) -> str:
    """Per-STRIDE chain-framing note — how a category combines into criticals."""
    notes = {
        "spoofing": "Identity compromise alone is a foothold. Chained with Elevation of Privilege or Tampering, it becomes domain-wide compromise.",
        "tampering": "Tampering on its own may be low-impact; combined with Spoofing or Repudiation it covers the attacker's tracks while changing state.",
        "repudiation": "Standalone repudiation rarely breaches data, but combined with any other STRIDE category it removes the audit trail of what happened.",
        "information_disclosure": "Data leak medium-on-its-own; chained with Spoofing (stolen creds in the leak) or Elevation (IAM keys exposed) it becomes critical.",
        "denial_of_service": "DoS is often dismissed as low-yield; chained as a cover for Tampering or Spoofing operations, it becomes a tactic, not just an outcome.",
        "elevation_of_privilege": "Almost never standalone in a real attack — always chains with Spoofing (initial access) and Tampering (persistence). Treat as a chain anchor.",
    }
    return notes.get(stride_category.lower().strip(), "")
