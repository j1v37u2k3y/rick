"""JARVIS state management — shared persistence layer for all JARVIS tools.

Handles engagement state storage, kill chain tracking, mission logging,
and state helpers used by both jarvis.py and jarvis_extended.py.
"""

import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ═══════════════════════════════════════════════════════════════
# Engagement state — persisted to ~/.rick_mcp/dick/
# ═══════════════════════════════════════════════════════════════

_STATE_DIR = Path.home() / ".rick_mcp" / "dick"

KILL_CHAIN_PHASES = [
    {"phase": 1, "name": "Reconnaissance", "status": "pending", "findings": []},
    {"phase": 2, "name": "Weaponization", "status": "pending", "findings": []},
    {"phase": 3, "name": "Delivery", "status": "pending", "findings": []},
    {"phase": 4, "name": "Exploitation", "status": "pending", "findings": []},
    {"phase": 5, "name": "Installation", "status": "pending", "findings": []},
    {"phase": 6, "name": "Command & Control", "status": "pending", "findings": []},
    {"phase": 7, "name": "Actions on Objectives", "status": "pending", "findings": []},
]

_MAX_SNAPSHOTS = 10
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".pdf", ".webp"}


def _state_file(engagement_id: str) -> Path:
    """Get the state file path for an engagement."""
    safe_id = "".join(c for c in engagement_id if c.isalnum() or c in "-_")[:50]
    return _STATE_DIR / f"{safe_id}.json"


def _load_state(engagement_id: str) -> dict[str, Any]:
    """Load engagement state from disk."""
    path = _state_file(engagement_id)
    if path.exists():
        result: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return result
    return {}


def _save_state(engagement_id: str, state: dict[str, Any], *, snapshot: bool = False) -> None:
    """Save engagement state to disk. Optionally snapshot current state before overwrite."""
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    if snapshot:
        existing = _load_state(engagement_id)
        if existing:
            _snapshot_state(existing, state)
    path = _state_file(engagement_id)
    path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def _snapshot_state(old_state: dict[str, Any], new_state: dict[str, Any]) -> None:
    """Push a snapshot of old_state into new_state's snapshots list."""
    snapshots = new_state.get("snapshots", [])
    snapshot_copy = copy.deepcopy(old_state)
    snapshot_copy.pop("snapshots", None)
    snapshots.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": snapshot_copy,
        }
    )
    new_state["snapshots"] = snapshots[-_MAX_SNAPSHOTS:]


def _add_mission_log(engagement_id: str, entry: str) -> None:
    """Append an entry to the mission log."""
    state = _load_state(engagement_id)
    if not state:
        return
    if "mission_log" not in state:
        state["mission_log"] = []
    state["mission_log"].append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entry": entry,
        }
    )
    state["mission_log"] = state["mission_log"][-100:]
    _save_state(engagement_id, state)


def _add_tool_history(engagement_id: str, tool: str, summary: str = "") -> None:
    """Log a tool call to the engagement history."""
    state = _load_state(engagement_id)
    if not state:
        return
    if "tool_history" not in state:
        state["tool_history"] = []
    state["tool_history"].append(
        {
            "tool": tool,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
        }
    )
    state["tool_history"] = state["tool_history"][-100:]
    _save_state(engagement_id, state)


def _add_note(engagement_id: str, note: str | dict[str, Any]) -> None:
    """Add an engagement note. Accepts plain string (legacy) or dict (new format)."""
    state = _load_state(engagement_id)
    if not state:
        return
    if "notes" not in state:
        state["notes"] = []
    state["notes"].append(note)
    _save_state(engagement_id, state)


def _phase_advice(phase: int) -> str:
    """Dick's advice for each kill chain phase."""
    advice = {
        1: "Recon is everything. Know your target better than they know themselves. OSINT, DNS, subdomains, tech stack, org chart. Don't touch anything yet.",
        2: "Build the weapon. Match exploits to what recon found. Custom payloads > off-the-shelf. Think about evasion NOW, not later.",
        3: "Delivery time. Phishing, exploit, or direct? Pick the path of least resistance. Test your payload before sending.",
        4: "Exploit. This is where prep pays off. First try should work if recon was thorough. If it doesn't — don't spray, think.",
        5: "Persistence. You're in. Now stay in. Web shells, scheduled tasks, registry keys, certs, golden tickets. Multiple persistence mechanisms.",
        6: "C2 established. Blend your traffic. DNS, HTTPS, domain fronting. Beacon intervals matter. Don't be noisy.",
        7: "Actions on objectives. Get what you came for. Document everything. Screenshots, hashes, proof of access. This is what goes in the report.",
    }
    return advice.get(phase, "Execute with precision.")


def _validate_image_path(path_str: str | None) -> str | None:
    """Validate an image path exists and has a recognized extension.

    Returns the resolved absolute path string, or None if path_str is None.
    Raises ValueError if validation fails.
    """
    if not path_str:
        return None
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"Image not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    if path.suffix.lower() not in _IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported image type '{path.suffix}'. Supported: {', '.join(sorted(_IMAGE_EXTENSIONS))}")
    return str(path)


def _get_checklist_template(target_type: str, phase: int) -> list[dict[str, Any]]:
    """Return default checklist items for a target type + phase combination."""
    common: dict[int, list[str]] = {
        1: [
            "OSINT / open-source intelligence gathering",
            "DNS enumeration (subdomains, records)",
            "Port scanning and service enumeration",
            "Technology stack fingerprinting",
            "Employee / org chart reconnaissance",
        ],
        2: [
            "Match discovered services to known CVEs",
            "Identify exploit candidates for each service",
            "Prepare custom payloads for target environment",
            "Test payloads in lab environment",
        ],
        3: [
            "Select delivery mechanism (phish, exploit, credential)",
            "Validate payload delivery path",
            "Confirm evasion against known defenses",
        ],
        4: [
            "Execute primary exploit",
            "Confirm code execution / access",
            "Capture initial proof (screenshot, whoami)",
            "Check for immediate privilege escalation",
        ],
        5: [
            "Deploy primary persistence mechanism",
            "Deploy backup persistence mechanism",
            "Verify persistence survives reboot",
            "Document all persistence artifacts for cleanup",
        ],
        6: [
            "Establish C2 channel",
            "Verify C2 stability and beacon interval",
            "Test data exfil path",
            "Confirm traffic blends with normal baseline",
        ],
        7: [
            "Achieve stated objective",
            "Capture proof of access / impact",
            "Document all findings with evidence",
            "Plan and execute cleanup",
            "Draft engagement report",
        ],
    }

    target_extras: dict[str, dict[int, list[str]]] = {
        "web_app": {
            1: ["Spider / crawl the application", "Identify authentication mechanisms", "Map API endpoints"],
            4: ["Test OWASP Top 10 vulnerabilities", "Check for default credentials"],
        },
        "active_directory": {
            1: ["Enumerate domain controllers", "Identify trust relationships", "BloodHound collection"],
            4: ["Test Kerberoasting", "Test AS-REP roasting", "Check for unconstrained delegation"],
            5: ["Golden ticket", "Silver ticket", "DCSync persistence check"],
        },
        "network": {
            1: ["Full port scan (TCP + UDP top 100)", "SNMP enumeration", "SMB enumeration"],
            4: ["Test default credentials on discovered services", "Check for EternalBlue / known vulns"],
        },
        "cloud_aws": {
            1: ["Enumerate S3 buckets", "Check IAM policies", "Review CloudTrail configuration"],
            4: ["Test for SSRF / metadata access", "Check for overprivileged roles"],
        },
        "cloud_azure": {
            1: ["Enumerate Azure AD", "Check for exposed storage accounts", "Review conditional access"],
            4: ["Test for token theft vectors", "Check for overprivileged service principals"],
        },
        "api": {
            1: ["Map all endpoints and methods", "Identify authentication scheme", "Check rate limiting"],
            4: ["Test BOLA / IDOR", "Test injection in parameters", "Check for mass assignment"],
        },
        "container": {
            1: ["Enumerate container orchestration", "Check exposed registries", "Map network policies"],
            4: ["Test container escape vectors", "Check for privileged containers", "Test service mesh bypasses"],
        },
        "mobile": {
            1: ["Decompile / reverse-engineer application", "Identify API endpoints", "Check certificate pinning"],
            4: ["Test local storage for secrets", "Check for insecure communication", "Test authentication bypass"],
        },
    }

    items = [{"item": item, "phase": phase, "checked": False} for item in common.get(phase, [])]

    extras = target_extras.get(target_type, {}).get(phase, [])
    items.extend({"item": item, "phase": phase, "checked": False} for item in extras)

    return items


_MITRE_ID_PATTERN = re.compile(r"^T\d{4}(\.\d{3})?$")
VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}


def validate_mitre_id(mitre_id: str | None) -> str | None:
    """Validate MITRE ATT&CK technique ID format. Returns cleaned ID or raises ValueError."""
    if not mitre_id:
        return None
    mitre_id = mitre_id.strip().upper()
    if not _MITRE_ID_PATTERN.match(mitre_id):
        raise ValueError(f"Invalid MITRE ATT&CK ID '{mitre_id}'. Expected format: T1234 or T1234.001")
    return mitre_id


def validate_severity(severity: str | None) -> str | None:
    """Validate severity level. Returns cleaned severity or raises ValueError."""
    if not severity:
        return None
    severity = severity.strip().lower()
    if severity not in VALID_SEVERITIES:
        raise ValueError(f"Invalid severity '{severity}'. Valid: {', '.join(sorted(VALID_SEVERITIES))}")
    return severity
