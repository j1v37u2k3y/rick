"""
Tests for rick_cognitive_appraisal — the defense-first cognitive-appraisal lens.

These tests ARE the acceptance criteria from the hand-off brief:
- refuses unauthorized red-team requests (no scoped engagement → no offensive output);
- never emits an unsourced concern (fabrication guard);
- every prediction carries a confidence level AND a refutation condition;
- deterministic structure (same input → same output shape);
- no benchmark / SOTA claim anywhere;
- public-domain appraisal vocabulary (OCC / Lazarus / Scherer), not MHH vocabulary.
Plus input validation, both output formats, and the _safe_tool production path.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from rick_mcp import AppraisalInput, ResponseFormat, rick_cognitive_appraisal

_PATCH_TARGET = "rick_mcp.tools.jarvis_state._STATE_DIR"

_SUBJECT = (
    "Finance clerk, processes vendor invoices; cares about not making a costly mistake and keeping the boss happy."
)
_SITUATION = "An email claiming to be the CFO demands an urgent wire transfer before end of day, no time to verify."


def _scoped_engagement(tmp_path, eng_id="eng-appraisal", scope=("acme.example",)):
    """Create a kill-chain engagement with a non-empty scope under a patched state dir."""
    from rick_mcp.tools.jarvis_state import _save_state

    state = {"id": eng_id, "target": "acme.example", "scope": list(scope)}
    with patch(_PATCH_TARGET, tmp_path):
        _save_state(eng_id, state)
    return eng_id


def _unscoped_engagement(tmp_path, eng_id="eng-noscope"):
    """Create an engagement that exists but has no scope defined."""
    from rick_mcp.tools.jarvis_state import _save_state

    with patch(_PATCH_TARGET, tmp_path):
        _save_state(eng_id, {"id": eng_id, "target": "acme.example"})
    return eng_id


# ═══════════════════════════════════════════════════════════════
#  Input model validation
# ═══════════════════════════════════════════════════════════════


class TestAppraisalInput:
    def test_defaults(self):
        m = AppraisalInput(subject=_SUBJECT, situation=_SITUATION)
        assert m.mode == "defense"
        assert m.engagement_id is None
        assert m.response_format == ResponseFormat.MARKDOWN

    def test_subject_required(self):
        with pytest.raises(ValidationError):
            AppraisalInput(situation=_SITUATION)

    def test_situation_required(self):
        with pytest.raises(ValidationError):
            AppraisalInput(subject=_SUBJECT)

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            AppraisalInput(subject=_SUBJECT, situation=_SITUATION, unexpected="nope")

    def test_subject_too_long(self):
        with pytest.raises(ValidationError):
            AppraisalInput(subject="x" * 2001, situation=_SITUATION)

    def test_whitespace_stripped(self):
        m = AppraisalInput(subject=f"  {_SUBJECT}  ", situation=_SITUATION)
        assert m.subject == _SUBJECT


# ═══════════════════════════════════════════════════════════════
#  Mode validation + defense default
# ═══════════════════════════════════════════════════════════════


class TestModes:
    async def test_unknown_mode_graceful_error(self):
        result = await rick_cognitive_appraisal(AppraisalInput(subject=_SUBJECT, situation=_SITUATION, mode="bogus"))
        assert "Unknown mode" in result

    async def test_defense_is_default_delivery(self):
        result = await rick_cognitive_appraisal(
            AppraisalInput(subject=_SUBJECT, situation=_SITUATION, response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert parsed["mode_delivered"] == "defense"
        assert "defensive_brief" in parsed
        assert "redteam_brief" not in parsed


# ═══════════════════════════════════════════════════════════════
#  Acceptance: red-team gating (no scoped engagement → no offensive output)
# ═══════════════════════════════════════════════════════════════


class TestRedTeamGate:
    async def test_redteam_without_engagement_falls_back_to_defense(self):
        result = await rick_cognitive_appraisal(
            AppraisalInput(subject=_SUBJECT, situation=_SITUATION, mode="redteam", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert parsed["mode_requested"] == "redteam"
        assert parsed["mode_delivered"] == "defense"
        assert "redteam_brief" not in parsed
        assert "defensive_brief" in parsed
        assert "gate" in parsed  # one-line reason for the refusal

    async def test_redteam_unknown_engagement_falls_back(self, tmp_path):
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_cognitive_appraisal(
                AppraisalInput(
                    subject=_SUBJECT,
                    situation=_SITUATION,
                    mode="redteam",
                    engagement_id="does-not-exist",
                    response_format=ResponseFormat.JSON,
                )
            )
        parsed = json.loads(result)
        assert parsed["mode_delivered"] == "defense"
        assert "redteam_brief" not in parsed
        assert "gate" in parsed

    async def test_redteam_engagement_without_scope_falls_back(self, tmp_path):
        eng_id = _unscoped_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_cognitive_appraisal(
                AppraisalInput(
                    subject=_SUBJECT,
                    situation=_SITUATION,
                    mode="redteam",
                    engagement_id=eng_id,
                    response_format=ResponseFormat.JSON,
                )
            )
        parsed = json.loads(result)
        assert parsed["mode_delivered"] == "defense"
        assert "redteam_brief" not in parsed
        assert "scope" in parsed["gate"].lower()

    async def test_redteam_with_scoped_engagement_authorized(self, tmp_path):
        eng_id = _scoped_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_cognitive_appraisal(
                AppraisalInput(
                    subject=_SUBJECT,
                    situation=_SITUATION,
                    mode="redteam",
                    engagement_id=eng_id,
                    response_format=ResponseFormat.JSON,
                )
            )
        parsed = json.loads(result)
        assert parsed["mode_delivered"] == "redteam"
        assert "redteam_brief" in parsed
        assert parsed["authorized_engagement"] == eng_id
        assert "defensive_brief" not in parsed

    @pytest.mark.parametrize(
        "tainted",
        [
            "Use this to blackmail the target into paying.",
            "The mark is a grieving widow we can pressure.",
            "Pretext aimed at a child in the household.",
        ],
    )
    async def test_authorized_redteam_still_refuses_coercion_or_vulnerable(self, tmp_path, tainted):
        # Even with a scoped engagement, coercion/harm or vulnerable-population content
        # blocks the offensive path and returns defense-only.
        eng_id = _scoped_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_cognitive_appraisal(
                AppraisalInput(
                    subject=_SUBJECT,
                    situation=tainted,
                    mode="redteam",
                    engagement_id=eng_id,
                    response_format=ResponseFormat.JSON,
                )
            )
        parsed = json.loads(result)
        assert parsed["mode_delivered"] == "defense"
        assert "redteam_brief" not in parsed
        assert "gate" in parsed


# ═══════════════════════════════════════════════════════════════
#  Acceptance: fabrication guard (no input evidence → no invented concern)
# ═══════════════════════════════════════════════════════════════


class TestFabricationGuard:
    @pytest.mark.parametrize(
        "subject,situation",
        [
            ("123 456", _SITUATION),  # subject has no real words
            (_SUBJECT, "!!! ... 999"),  # situation has no real words
            ("...", "###"),  # neither
        ],
    )
    async def test_insufficient_evidence_short_circuit(self, subject, situation):
        result = await rick_cognitive_appraisal(
            AppraisalInput(subject=subject, situation=situation, response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert parsed["verdict"] == "INSUFFICIENT EVIDENCE"
        # The scaffold is withheld — nothing to fill in, nothing invented.
        assert "appraisal_checks" not in parsed
        assert "defensive_brief" not in parsed

    async def test_real_evidence_produces_scaffold_bound_to_input(self):
        result = await rick_cognitive_appraisal(
            AppraisalInput(subject=_SUBJECT, situation=_SITUATION, response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        # The only sanctioned source for concerns is the echoed evidence base.
        assert parsed["evidence_base"]["subject"] == _SUBJECT
        assert parsed["evidence_base"]["situation"] == _SITUATION
        assert "fabrication_guard" in parsed["guards"]


# ═══════════════════════════════════════════════════════════════
#  Acceptance: confidence + refutation on every prediction
# ═══════════════════════════════════════════════════════════════


class TestConfidenceAndRefutation:
    async def test_confidence_scale_and_falsifiability_present(self):
        result = await rick_cognitive_appraisal(
            AppraisalInput(subject=_SUBJECT, situation=_SITUATION, response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        guards = parsed["guards"]
        assert set(guards["confidence_scale"]) == {"stated", "high", "medium", "speculation"}
        assert "refutation" in guards["falsifiability"].lower()

    async def test_output_contract_requires_confidence_and_refutation(self):
        result = await rick_cognitive_appraisal(
            AppraisalInput(subject=_SUBJECT, situation=_SITUATION, response_format=ResponseFormat.JSON)
        )
        per_concern = json.loads(result)["output_contract"]["per_concern"]
        assert "confidence" in per_concern
        assert "refutation_condition" in per_concern
        # the agency/blame axis the brief specifically calls for
        assert "agency_blame" in per_concern


# ═══════════════════════════════════════════════════════════════
#  Acceptance: deterministic structure
# ═══════════════════════════════════════════════════════════════


class TestDeterminism:
    async def test_same_input_same_output(self):
        a = await rick_cognitive_appraisal(AppraisalInput(subject=_SUBJECT, situation=_SITUATION))
        b = await rick_cognitive_appraisal(AppraisalInput(subject=_SUBJECT, situation=_SITUATION))
        assert a == b


# ═══════════════════════════════════════════════════════════════
#  Acceptance: no benchmark/SOTA claim; clean-room vocabulary
# ═══════════════════════════════════════════════════════════════


class TestHonestyAndCleanRoom:
    @pytest.mark.parametrize("mode", ["defense", "redteam"])
    async def test_no_benchmark_or_sota_claim_in_output(self, tmp_path, mode):
        eng_id = _scoped_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_cognitive_appraisal(
                AppraisalInput(subject=_SUBJECT, situation=_SITUATION, mode=mode, engagement_id=eng_id)
            )
        low = result.lower()
        for banned in ("benchmark", "sota", "state-of-the-art", "state of the art", "outperform", "% accuracy"):
            assert banned not in low

    def test_no_benchmark_claim_in_source(self):
        from rick_mcp.tools import appraisal

        src = Path(appraisal.__file__).read_text(encoding="utf-8").lower()
        for banned in ("benchmark", "sota", "state-of-the-art", "outperform"):
            assert banned not in src

    async def test_public_domain_vocabulary_present(self):
        result = await rick_cognitive_appraisal(AppraisalInput(subject=_SUBJECT, situation=_SITUATION))
        for src in ("OCC", "Lazarus", "Scherer"):
            assert src in result

    @pytest.mark.parametrize("mode", ["defense", "redteam"])
    async def test_no_mhh_vocabulary(self, tmp_path, mode):
        eng_id = _scoped_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_cognitive_appraisal(
                AppraisalInput(subject=_SUBJECT, situation=_SITUATION, mode=mode, engagement_id=eng_id)
            )
        low = result.lower()
        for banned in ("webb", "{self}", "power level", "ep ∆ p", "equation of emotion", "severity ladder"):
            assert banned not in low


# ═══════════════════════════════════════════════════════════════
#  Output formats
# ═══════════════════════════════════════════════════════════════


class TestOutputFormats:
    async def test_markdown_renders_cleanly(self):
        result = await rick_cognitive_appraisal(
            AppraisalInput(subject=_SUBJECT, situation=_SITUATION, response_format=ResponseFormat.MARKDOWN)
        )
        assert "# 🐢🤘 Cognitive Appraisal" in result or "Cognitive Appraisal" in result
        assert "## Appraisal Checks" in result
        assert "relevance" in result.lower()
        assert "{'" not in result  # no dict repr leaked
        assert "['" not in result  # no list repr leaked

    async def test_json_parses_and_carries_contract(self):
        result = await rick_cognitive_appraisal(
            AppraisalInput(subject=_SUBJECT, situation=_SITUATION, response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        for key in (
            "evidence_base",
            "appraisal_checks",
            "response_tendency_map",
            "output_contract",
            "guards",
            "sources",
        ):
            assert key in parsed


# ═══════════════════════════════════════════════════════════════
#  _safe_tool wrapper — the production path MCP clients actually hit
# ═══════════════════════════════════════════════════════════════


class TestSafeToolWrapper:
    async def test_catches_exceptions_and_returns_message(self):
        from rick_mcp import _safe_tool

        async def boom(_params):
            raise ValueError("boom")

        wrapped = _safe_tool(boom)
        result = await wrapped(None)
        assert "encountered an issue" in result
