"""Cognitive Appraisal — defense-first appraisal-theory reasoning scaffold.

Clean-room build from public-domain cognitive-appraisal theory (OCC, Lazarus, Scherer).
For a (subject, situation) pair it emits a per-concern scaffold: the published appraisal
checks → a predicted response tendency. The output contract asks the filler to cite each
concern's evidence, mark a confidence level, and attach a refutation condition.

Defense is the default deliverable (lever exposed + detection / hardening). Red-team
(pretext) output sits behind an operator-set scope gate: it appears only when the named
engagement carries a non-empty scope (the same rick_scope_check flag). That's deliberate
friction and an intent signal, not access control — the operator controls that flag.

Like rick_code_review, this is a deterministic scaffold, not an analyzer: it echoes the
in-scope evidence and lays out the framework the caller fills in. The tool itself enforces
the mode gate, an insufficient-evidence short-circuit, deterministic structure, and
statelessness, and makes no capability claim; sourcing each concern and honoring the
hard-refusal policy are the caller's job — the tool can't verify them.
"""

import re

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import AppraisalInput
from rick_mcp.tools.jarvis_state import _load_state

_VALID_MODES = frozenset({"defense", "redteam"})

# A word is two+ letters — used by the fabrication guard to tell real evidence from
# punctuation/noise. No letters in subject or situation → nothing to appraise.
_WORD_RE = re.compile(r"[A-Za-z]{2,}")

# Coarse keyword speed bump on the OFFENSIVE path only — defense output is never blocked
# (detecting and hardening against coercion is the whole mission). It downgrades the
# red-team brief to defense-only on obvious coercion/vulnerable terms, but it's easily
# reworded around: friction, not a real filter. The scope gate is the actual control; the
# hard-refusal policy in _GUARDS is what the caller must honor.
_COERCION_RE = re.compile(
    r"\b(blackmail|extort|extortion|coerce|coercion|sextortion|stalk|stalking|"
    r"harass|harassment|intimidate|intimidation|doxx?|dox)\b",
    re.IGNORECASE,
)
_VULNERABLE_RE = re.compile(
    r"\b(child|children|minor|minors|toddler|infant|elderly|dementia|alzheimer|"
    r"grieving|bereaved|suicidal|self-harm)\b",
    re.IGNORECASE,
)

# The five published appraisal checks. OCC names the concern branches; Lazarus the
# primary/secondary appraisal; Scherer the stimulus evaluation checks. Our own phrasing.
_APPRAISAL_CHECKS = {
    "relevance": "Does the situation bear on this concern at all? (Lazarus: goal relevance.) No relevance → no emotion; stop the row here.",
    "congruence": "Beneficial or harmful to the concern? (Lazarus: goal congruence/incongruence.) Sets the positive vs negative tone.",
    "agency_blame": "Who is accountable — self, another agent, or impersonal circumstance? (OCC agent/standards branch; Lazarus blame/credit.) This axis splits anger (other) vs guilt (self) vs sadness (circumstance).",
    "certainty": "Is the outcome known or only anticipated? (Scherer: outcome probability.) Splits fear vs anger, hope vs joy, distress vs relief.",
    "coping_potential": "Can the subject act on it — change it, or only endure it? (Lazarus: secondary appraisal; Scherer: control/power/adjustment.) Splits anger/challenge (high control) vs fear/resignation (low control).",
}

# How an appraisal pattern reads off to an affective + behavioral lean. Textbook
# OCC/Lazarus/Scherer mappings — no invented machinery, no severity ladder.
_RESPONSE_TENDENCY_MAP = {
    "other_blame + harmful + high coping": "Anger / confrontation — lean to push back, demand, retaliate.",
    "self_blame + harmful": "Guilt / shame — lean to withdraw, make amends, comply.",
    "harmful + uncertain + low coping": "Fear / anxiety — lean to avoid, freeze, seek safety or reassurance.",
    "harmful + certain + low coping": "Sadness / resignation — lean to disengage, accept, seek comfort.",
    "beneficial + uncertain": "Hope / anticipation — lean to pursue, wait, take the chance.",
    "beneficial + certain": "Relief / joy — lean to approach, reciprocate, lower the guard.",
    "circumstance_blame + harmful": "Distress without a target — lean to seek an explanation or a measure of control.",
}

_ANALYSIS_PROTOCOL = [
    "1. From the evidence_base, name the subject's salient concerns — goals, standards, attitudes in play (OCC's three branches). Cite the span for each. No span → insufficient evidence; do not invent one.",
    "2. For each concern, run the five appraisal_checks in order. Stop at relevance if the situation doesn't bear on it.",
    "3. Read the appraisal pattern off the response_tendency_map to a predicted affective + behavioral tendency.",
    "4. Mark every line with a confidence level and attach a refutation_condition to every prediction.",
    "5. Translate to the active mode's brief: defensive (lever + detection + hardening) by default; red-team pretext only under an authorized, scoped engagement.",
]

_OUTPUT_CONTRACT = {
    "per_concern": [
        "concern",
        "cited_evidence",
        "relevance",
        "congruence",
        "agency_blame",
        "certainty",
        "coping_potential",
        "predicted_tendency",
        "confidence",
        "refutation_condition",
    ],
}

_DEFENSE_BRIEF_CONTRACT = {
    "for_each_tendency": [
        "lever_exposed — which appraisal a manipulator would target to induce this tendency (inflate certainty to force fear, shift blame to provoke anger, manufacture scarcity to rush a decision).",
        "detection — observable signs the lever is being pulled (urgency cues, manufactured authority, false scarcity, blame reframing).",
        "hardening — the countermeasure that neutralizes the lever (verification step, decision delay, out-of-band check, targeted training).",
    ],
    "principle": "Name the lever, then close it. Defense is the default deliverable.",
}

_REDTEAM_BRIEF_CONTRACT = {
    "scope_binding": "Every pretext element must map to the authorized engagement scope. Out-of-scope → do not produce it.",
    "for_each_lever": [
        "pretext_frame — the legitimate-looking framing that exercises the appraisal lever within scope.",
        "appraisal_targeted — which check (relevance/congruence/agency/certainty/coping) the frame moves, and in which direction.",
        "success_signal — what an authorized operator would observe if the frame lands.",
        "abort_condition — what mandates standing down (scope edge, non-consenting third party, vulnerable individual).",
    ],
}

_GUARDS = {
    "fabrication_guard": "Every concern and appraisal must cite a span from the evidence_base. No supporting span → mark 'insufficient evidence'. Never invent a backstory to fill a gap. (A rule for the filler — the tool can't verify your spans are real.)",
    "confidence_scale": {
        "stated": "Directly asserted in the evidence_base.",
        "high": "Strongly implied by the evidence; little else fits.",
        "medium": "A plausible reading of the evidence among a few.",
        "speculation": "A guess beyond the evidence — flag it as such, or drop it.",
    },
    "falsifiability": "Every predicted tendency carries a refutation_condition — the observation that would prove it wrong. No refutation condition, no prediction.",
    "hard_refusals": [
        "Real, named, non-consenting individuals outside an authorized engagement.",
        "Targeting of vulnerable populations.",
        "Anything aimed at coercion or harm of specific real people.",
    ],
    "stateless": "No subject data is stored, profiled, or persisted. This lens reads only the in-scope input you provide.",
}

_SOURCES = [
    "Ortony, Clore & Collins (1988), The Cognitive Structure of Emotions (the OCC model).",
    "Lazarus (1991), Emotion and Adaptation (primary/secondary appraisal).",
    "Scherer — Component Process Model / Stimulus Evaluation Checks.",
]

_RICK_NOTE = (
    "This is a lens, not a mind-reader — and a frame, not the analysis: it lays out the checks, you do the "
    "reasoning. Cite the evidence or say you don't know. Defense is the default; the offensive frame sits "
    "behind an operator-set scope gate — friction and intent, not a lock. No invented backstories, no "
    "confidence you didn't earn."
)


def _check_redteam_gate(engagement_id: str) -> tuple[bool, str]:
    """Authorize the red-team path. Returns (authorized, reason_if_not).

    Composes with rick_scope_check's authorization signal: the engagement must exist in
    kill-chain state AND carry a non-empty scope. No engagement / no scope → defense-only.
    """
    if not engagement_id:
        return (
            False,
            "Red-team pretext output requires an authorized engagement_id. None supplied — returning defense-only.",
        )
    state = _load_state(engagement_id)
    if not state:
        return (
            False,
            f"No engagement '{engagement_id}' found. Red-team output requires an active, scoped engagement — returning defense-only.",
        )
    if not state.get("scope"):
        return False, (
            f"Engagement '{engagement_id}' has no scope defined. Set scope via rick_scope_check before requesting "
            "red-team output — returning defense-only."
        )
    return True, ""


async def rick_cognitive_appraisal(params: AppraisalInput) -> str:
    """Defense-first cognitive-appraisal scaffold (OCC/Lazarus/Scherer).

    Per salient concern: relevance/congruence/agency-blame/certainty/coping → a predicted
    response tendency, evidence-cited, confidence-marked, with a refutation condition.
    Defense brief by default; red-team pretext gated behind a scoped engagement.
    """
    mode = (params.mode or "defense").lower().strip()
    if mode not in _VALID_MODES:
        return f"Error: Unknown mode '{mode}'. Available: {', '.join(sorted(_VALID_MODES))}"

    subject = _sanitize(params.subject) or ""
    situation = _sanitize(params.situation) or ""
    evidence_base = {"subject": subject, "situation": situation}

    # Fabrication guard (deterministic short-circuit): no real evidence → invent nothing.
    if not _WORD_RE.search(subject) or not _WORD_RE.search(situation):
        return _fmt(
            {
                "verdict": "INSUFFICIENT EVIDENCE",
                "reason": "The lens does not invent concerns. Provide a subject (role/context + in-scope concerns) and a situation with enough substance to cite.",
                "evidence_base": evidence_base,
                "guards": {"fabrication_guard": _GUARDS["fabrication_guard"]},
            },
            params.response_format,
            title=f"{CALLSIGN} Cognitive Appraisal",
        )

    eng_id = _sanitize(params.engagement_id) or (params.engagement_id or "")
    combined = f"{subject}\n{situation}"

    # Gate the offensive (red-team) path.
    authorized = False
    gate_reason = ""
    if mode == "redteam":
        authorized, gate_reason = _check_redteam_gate(eng_id)
        # Secondary tripwire: never produce a pretext touching coercion/harm or a
        # potentially vulnerable population, even inside an authorized engagement.
        if authorized and (_COERCION_RE.search(combined) or _VULNERABLE_RE.search(combined)):
            authorized = False
            gate_reason = (
                "Hard refusal: the input touches coercion/harm or a potentially vulnerable population. "
                "No pretext will be produced — returning defensive guidance only."
            )

    effective_mode = "redteam" if (mode == "redteam" and authorized) else "defense"

    result: dict = {
        "mode_requested": mode,
        "mode_delivered": effective_mode,
        "evidence_base": evidence_base,
        "method": (
            "Cognitive appraisal (OCC / Lazarus / Scherer). The sections below are a reasoning scaffold — "
            "fill each concern only from the evidence_base above, honoring every guard."
        ),
        "analysis_protocol": _ANALYSIS_PROTOCOL,
        "appraisal_checks": _APPRAISAL_CHECKS,
        "response_tendency_map": _RESPONSE_TENDENCY_MAP,
        "output_contract": _OUTPUT_CONTRACT,
    }

    if effective_mode == "defense":
        result["defensive_brief"] = _DEFENSE_BRIEF_CONTRACT
    else:
        result["redteam_brief"] = _REDTEAM_BRIEF_CONTRACT
        result["authorized_engagement"] = eng_id

    if gate_reason:
        result["gate"] = gate_reason
    result["guards"] = _GUARDS
    result["sources"] = _SOURCES
    result["rick_note"] = _RICK_NOTE

    return _fmt(result, params.response_format, title=f"{CALLSIGN} Cognitive Appraisal")


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_cognitive_appraisal",
        annotations={
            "title": "Cognitive Appraisal Lens",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_cognitive_appraisal))
