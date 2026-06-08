"""Code review — Rick's builder's-eye scoring & verdict rubric.

Pure function. Emits the standard the /rick-review skill applies to real findings (its own
cold scan, or findings delegated to Claude's built-in /code-review + /security-review). It does
NOT read files — judgment over a real tree is the skill's job.
"""

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool
from rick_mcp.models import CodeReviewInput

_DIMENSIONS = {
    "craftsmanship": {
        "builder_metaphor": "Built to last, or slapped together? A wall is only as good as the hands that laid it.",
        "inspect": [
            "File/module size — bloat hides bugs (this repo caps Python files at 1500 lines)",
            "Naming — do names tell the truth about what the code does?",
            "Dead code, commented-out blocks, duplicated logic — cut what you don't use",
            "Test coverage — are the load-bearing paths tested? Error cases, not just happy path",
            "Error handling — does it fail loud and honest, or swallow exceptions?",
            "Comments where the 'why' is non-obvious; silence where the code already speaks",
        ],
        "flag": [
            "Functions doing five jobs — no single responsibility",
            "Copy-paste duplication instead of a shared helper",
            "Padded code — abstraction with no payoff, indirection for its own sake",
            "Silent except/catch blocks that bury failure",
            "Zero tests on critical logic",
        ],
    },
    "security": {
        "builder_metaphor": "The joints are where it fails. Trust boundaries, inputs, secrets — that's where the water gets in.",
        "inspect": [
            "Secrets in source — API keys, passwords, tokens, private keys",
            "Injection surfaces — SQL/command/template/LDAP; is input parameterized?",
            "AuthN/AuthZ boundaries — who can call this, and is it checked every time?",
            "Unsafe deserialization, eval, pickle, dynamic code execution",
            "Dependency risk — pinned versions, known-vulnerable packages",
            "Path handling — user input reaching the filesystem without a containment check",
        ],
        "flag": [
            "Hardcoded credentials or tokens",
            "String-concatenated queries or shell commands",
            "Missing authorization check on a state-changing path",
            "User input → filesystem path with no containment",
        ],
        "chain_to": "For depth on any vuln class, chain to rick_vuln_assess; for attack-surface mapping, rick_threat_model.",
    },
    "architecture": {
        "builder_metaphor": "Find the load-bearing walls before you knock anything down. The foundation determines everything above it.",
        "inspect": [
            "Load-bearing modules — what carries the weight? What breaks if it fails?",
            "The joints — interfaces, APIs, trust boundaries between components",
            "Coupling and layering — does the dependency graph flow one way, or is it a knot?",
            "Single source of truth — is state/config defined once, or duplicated and drifting?",
            "Separation of concerns — logic, data, and presentation cleanly split?",
        ],
        "flag": [
            "Circular dependencies",
            "Business logic leaking into the transport/presentation layer",
            "Config or constants duplicated across files — drift waiting to happen",
            "A god-module everything imports",
        ],
    },
}

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

_LANGUAGE_NOTES = {
    "python": [
        "Type hints on public functions; mypy-clean",
        "No bare `except:` — catch what you handle",
        "Context managers for files/locks/connections",
        "Pin deps; watch pickle/yaml.load/eval/subprocess(shell=True)",
    ],
    "javascript": [
        "No `eval` / `Function` on user input; watch `innerHTML` (XSS)",
        "Strict equality (`===`); avoid implicit coercion bugs",
        "Promise rejection handling; no floating async",
        "Lockfile committed; audit transitive deps",
    ],
    "typescript": [
        "No `any` on boundaries; let the types carry the contract",
        "`strict` mode on; no non-null `!` to silence the compiler",
        "Discriminated unions over loose object shapes",
    ],
    "go": [
        "Errors checked, not discarded with `_`",
        "Context propagation on I/O paths",
        "Goroutine lifecycles bounded; no leaks",
        "`defer` for cleanup; mind the loop-variable capture",
    ],
}


async def rick_code_review(params: CodeReviewInput) -> str:
    """Rick's builder's-eye review rubric — the scoring + verdict standard for a codebase.

    Pure rubric, not an analyzer. The /rick-review skill applies this to real findings.
    """
    focus = (params.focus or "full").lower().strip()
    valid = {"full", *_DIMENSIONS}
    if focus not in valid:
        return f"Error: Unknown focus '{focus}'. Available: {', '.join(sorted(valid))}"

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
