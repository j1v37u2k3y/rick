"""Code review — Rick's builder's-eye scoring & verdict rubric.

Emits the standard the /rick-review skill applies to real findings (its own cold scan, or
findings delegated to Claude's built-in /code-review + /security-review). The rubric
(dimensions + language notes) loads from a YAML data file at import — override at
~/.rick_mcp/code_review.yaml, falling back to the bundled rick_mcp/data/code_review.yaml —
so a fork can retune it without editing source. The tool function itself stays pure: no
per-call file I/O, and judgment over a real tree is the skill's job.
"""

import logging
from pathlib import Path

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool
from rick_mcp.models import CodeReviewInput

logger = logging.getLogger("rick_mcp")

CODE_REVIEW_OVERRIDE_PATH = Path.home() / ".rick_mcp" / "code_review.yaml"
CODE_REVIEW_BUNDLED_PATH = Path(__file__).parent.parent / "data" / "code_review.yaml"


# Last-resort baseline if both YAML files are missing/unparseable or pyyaml is absent.
# Keeps the module importable (and _VALID_FOCUS structurally complete) in pathological
# environments. The bundled YAML is the real contract — this is not a full copy.
_MINIMAL_DEFAULTS: dict = {
    "dimensions": {
        "craftsmanship": {
            "builder_metaphor": "A wall is only as good as the hands that laid it.",
            "inspect": ["Naming, size, tests, error handling — does it fail loud and honest?"],
            "flag": ["Functions doing five jobs; silent except blocks; zero tests on critical logic"],
        },
        "security": {
            "builder_metaphor": "The joints are where it fails — trust boundaries, inputs, secrets.",
            "inspect": ["Secrets in source, injection surfaces, auth boundaries, unsafe deserialization"],
            "flag": ["Hardcoded credentials; string-concatenated queries; missing authz checks"],
            "chain_to": "For depth on any vuln class, chain to rick_vuln_assess.",
        },
        "architecture": {
            "builder_metaphor": "Find the load-bearing walls before you knock anything down.",
            "inspect": ["Load-bearing modules, coupling, single source of truth, separation of concerns"],
            "flag": ["Circular dependencies; duplicated config; a god-module everything imports"],
        },
    },
    "language_notes": {
        "python": ["Type hints + mypy-clean; no bare except; pin deps; watch eval/pickle/subprocess(shell=True)"],
    },
}


def _load_rubric() -> dict:
    """Load the code-review rubric YAML with override → bundled → minimal-baseline fallback."""
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("pyyaml not installed — using minimal code-review rubric defaults.")
        return dict(_MINIMAL_DEFAULTS)

    for path in (CODE_REVIEW_OVERRIDE_PATH, CODE_REVIEW_BUNDLED_PATH):
        if not path.exists():
            continue
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and raw.get("dimensions"):
                logger.info(f"Code-review rubric loaded from {path}")
                return raw
            logger.warning(f"{path} is malformed — trying next source.")
        except Exception as e:
            logger.warning(f"Error loading {path}: {e} — trying next source.")

    logger.warning("No code-review rubric YAML found — using minimal defaults.")
    return dict(_MINIMAL_DEFAULTS)


_rubric = _load_rubric()

# Operator-customizable rubric data (override at ~/.rick_mcp/code_review.yaml).
_DIMENSIONS: dict = _rubric["dimensions"]
_LANGUAGE_NOTES: dict = _rubric.get("language_notes", {})

# Voiced scales stay in code: voice register, not rubric data (single source of voice).
_SEVERITY_SCALE = {
    "critical": "🔴 Load-bearing or exploitable. Breaks the build, leaks data, or compromises trust. Fix before ship.",
    "moderate": "🟡 Real, but not load-bearing. Degrades quality or maintainability. Fix this pass or next.",
    "minor": "🟢 Polish. Style, naming, small dead code. Fix when you're in the neighborhood.",
}

_VERDICT_SCALE = [
    "Ship it — foundation's solid, joints hold. Minor polish only.",
    "One polish pass — sound, but a few 🟡s to clean before it's right.",
    "Needs work — real cracks. Address the 🔴/🟡 before this carries weight.",
    "Redesign the foundation — load-bearing problems. Patching paint won't hold.",
]

_SCORING = {
    "normalize": (
        "Map every finding — your own, /code-review's, /security-review's, rick_vuln_assess's — "
        "onto the severity scale. One finding, one severity. No inflating to look thorough, no "
        "minimizing to dodge a hard conversation."
    ),
    "prioritize": (
        "Load-bearing first. A 🔴 in a module everything depends on outranks ten 🟢s in a leaf. "
        "Report in severity order, then by blast radius."
    ),
    "every_finding": "Location · impact · blueprint-to-fix. Don't just say it's broken — hand them the fix.",
}

_INSPECTION_METHOD = [
    "1. Understand the architecture — how it was built before you judge how it breaks",
    "2. Find the load-bearing walls — which components carry the weight",
    "3. Test the joints — interfaces, APIs, and trust boundaries are where vulns live",
    "4. Report like an inspector — severity, location, impact, remediation",
    "5. Remediate like a contractor — actionable fixes with the blueprint, not just criticism",
]

_VALID_FOCUS = frozenset({"full", *_DIMENSIONS})


async def rick_code_review(params: CodeReviewInput) -> str:
    """Rick's builder's-eye review rubric — the scoring + verdict standard for a codebase.

    Pure rubric, not an analyzer. The /rick-review skill applies this to real findings.
    """
    focus = (params.focus or "full").lower().strip()
    if focus not in _VALID_FOCUS:
        return f"Error: Unknown focus '{focus}'. Available: {', '.join(sorted(_VALID_FOCUS))}"

    dims = _DIMENSIONS if focus == "full" else {focus: _DIMENSIONS[focus]}

    result: dict = {
        "focus": focus,
        "how_to_use": (
            "Rubric only — apply it via the /rick-review skill. If there's a diff/PR, delegate to "
            "Claude's /code-review (+ /security-review) and score their findings here. If it's a cold "
            "repo, walk the load-bearing files yourself using the inspection_method."
        ),
        "dimensions": dims,
        "severity_scale": _SEVERITY_SCALE,
        "verdict_scale": _VERDICT_SCALE,
        "scoring": _SCORING,
        "inspection_method": _INSPECTION_METHOD,
        "rick_note": (
            "No padded reports. No inflated severity to look impressive, no minimized severity to "
            "dodge a hard conversation. Real findings, real impact, real blueprint. Build it like "
            "your name's on it."
        ),
    }

    # Language notes are craftsmanship-flavored — only relevant to the full or craftsmanship lens.
    lang = (params.language or "").lower().strip()
    if focus in {"full", "craftsmanship"} and lang and lang in _LANGUAGE_NOTES:
        result["language_notes"] = {lang: _LANGUAGE_NOTES[lang]}

    return _fmt(result, params.response_format, title=f"{CALLSIGN} Code Review Rubric")


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_code_review",
        annotations={
            "title": "Code Review Rubric",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_code_review))
