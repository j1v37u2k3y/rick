"""
Tests for rick_code_review — the builder's-eye scoring & verdict rubric.

Covers input validation, every focus lens, both output formats, and the contract
the /rick-review skill relies on (severity scale, verdict scale, scoring rules).
"""

import json

import pytest
from pydantic import ValidationError

from rick_mcp import CodeReviewInput, ResponseFormat, rick_code_review

# ═══════════════════════════════════════════════════════════════
#  Input model validation
# ═══════════════════════════════════════════════════════════════


class TestCodeReviewInput:
    def test_defaults(self):
        m = CodeReviewInput()
        assert m.focus == "full"
        assert m.language is None
        assert m.response_format == ResponseFormat.MARKDOWN

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            CodeReviewInput(focus="full", unexpected="nope")

    def test_language_too_long(self):
        with pytest.raises(ValidationError):
            CodeReviewInput(language="x" * 51)

    def test_focus_too_long(self):
        with pytest.raises(ValidationError):
            CodeReviewInput(focus="x" * 21)

    def test_whitespace_stripped(self):
        m = CodeReviewInput(focus="  full  ")
        assert m.focus == "full"


# ═══════════════════════════════════════════════════════════════
#  Tool behavior — lenses, formats, contract
# ═══════════════════════════════════════════════════════════════


class TestRickCodeReview:
    @pytest.mark.parametrize("focus", ["full", "security", "craftsmanship", "architecture"])
    async def test_each_focus_returns_content(self, focus):
        result = await rick_code_review(CodeReviewInput(focus=focus))
        assert isinstance(result, str)
        assert len(result) > 100

    async def test_markdown_renders_cleanly(self):
        # The dimensions section must render as real markdown, not a dumped Python dict repr.
        result = await rick_code_review(CodeReviewInput(focus="full", response_format=ResponseFormat.MARKDOWN))
        assert "# " in result
        assert "## Dimensions" in result
        assert "Inspect" in result  # checklist header rendered, not buried in a dict literal
        assert "{'" not in result  # no raw dict repr leaked into markdown

    async def test_json_format_carries_contract(self):
        result = await rick_code_review(CodeReviewInput(focus="full", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        for key in ("severity_scale", "verdict_scale", "scoring", "dimensions", "inspection_method"):
            assert key in parsed

    async def test_full_lens_has_all_three_dimensions(self):
        result = await rick_code_review(CodeReviewInput(focus="full", response_format=ResponseFormat.JSON))
        dims = json.loads(result)["dimensions"]
        assert set(dims.keys()) == {"craftsmanship", "security", "architecture"}

    @pytest.mark.parametrize("focus", ["security", "craftsmanship", "architecture"])
    async def test_narrow_lens_filters_to_its_own_dimension(self, focus):
        result = await rick_code_review(CodeReviewInput(focus=focus, response_format=ResponseFormat.JSON))
        dims = json.loads(result)["dimensions"]
        assert set(dims.keys()) == {focus}

    async def test_none_focus_resolves_to_full(self):
        result = await rick_code_review(CodeReviewInput(focus=None, response_format=ResponseFormat.JSON))
        dims = json.loads(result)["dimensions"]
        assert set(dims.keys()) == {"craftsmanship", "security", "architecture"}

    async def test_security_lens_chains_to_vuln_assess(self):
        result = await rick_code_review(CodeReviewInput(focus="security"))
        assert "rick_vuln_assess" in result

    async def test_language_notes_included_when_known(self):
        result = await rick_code_review(
            CodeReviewInput(focus="craftsmanship", language="python", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert "language_notes" in parsed
        assert "python" in parsed["language_notes"]

    async def test_language_notes_absent_when_unknown(self):
        result = await rick_code_review(
            CodeReviewInput(focus="full", language="cobol", response_format=ResponseFormat.JSON)
        )
        assert "language_notes" not in json.loads(result)

    async def test_language_notes_absent_for_nonquality_lens(self):
        # Language notes are craftsmanship-flavored — not attached to architecture/security lenses.
        result = await rick_code_review(
            CodeReviewInput(focus="architecture", language="python", response_format=ResponseFormat.JSON)
        )
        assert "language_notes" not in json.loads(result)

    async def test_unknown_focus_returns_graceful_error(self):
        # The bare function early-returns a graceful string for an unknown focus (no raise).
        result = await rick_code_review(CodeReviewInput(focus="bogus"))
        assert "Unknown focus" in result


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
