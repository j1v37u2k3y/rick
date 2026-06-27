"""
Tests for rick_code_review — the builder's-eye scoring & verdict rubric.

Covers input validation, every focus lens, both output formats, and the contract
the /rick-review skill relies on (severity scale, verdict scale, scoring rules).
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from rick_mcp import CodeReviewInput, ResponseFormat, rick_code_review
from rick_mcp.tools.code_review import (
    _DIMENSIONS,
    _LANGUAGE_NOTES,
    CODE_REVIEW_BUNDLED_PATH,
    _load_rubric,
)

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
        # The dimensions section must render as real markdown, not a dumped dict/list repr.
        result = await rick_code_review(CodeReviewInput(focus="full", response_format=ResponseFormat.MARKDOWN))
        assert "## Dimensions" in result
        assert "- **Inspect:**" in result  # the checklist sub-header rendered as a bullet
        assert "File/module size" in result  # an actual checklist item, not buried in a literal
        assert "{'" not in result  # no dict repr leaked
        assert "['" not in result  # no list repr leaked

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

    async def test_language_notes_present_on_full_lens(self):
        # The default + most common path: full lens with a known language attaches notes.
        result = await rick_code_review(
            CodeReviewInput(focus="full", language="python", response_format=ResponseFormat.JSON)
        )
        assert "python" in json.loads(result)["language_notes"]

    async def test_language_notes_absent_on_security_lens(self):
        result = await rick_code_review(
            CodeReviewInput(focus="security", language="python", response_format=ResponseFormat.JSON)
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


# ═══════════════════════════════════════════════════════════════
#  YAML loader — bundled rubric + ~/.rick_mcp/ override path
# ═══════════════════════════════════════════════════════════════


class TestCodeReviewLoader:
    def test_bundled_yaml_exists(self):
        # Bundled rubric must ship with the package.
        assert CODE_REVIEW_BUNDLED_PATH.exists()

    def test_loader_returns_required_top_level_keys(self):
        loaded = _load_rubric()
        assert "dimensions" in loaded
        assert "language_notes" in loaded

    def test_bundled_yaml_parses_to_module_constants(self):
        # When no override exists, the loader returns the bundled content; the
        # module-level constants should match it byte-for-byte (output parity).
        loaded = _load_rubric()
        assert loaded["dimensions"] == _DIMENSIONS
        assert loaded.get("language_notes", {}) == _LANGUAGE_NOTES

    def test_bundled_has_all_three_dimensions(self):
        loaded = _load_rubric()
        assert set(loaded["dimensions"].keys()) == {"craftsmanship", "security", "architecture"}

    def test_override_path_takes_precedence(self, tmp_path):
        # Write a custom rubric at a fake override path and confirm the loader
        # picks it up over the bundled file — the forkable-customization path.
        custom = tmp_path / "code_review.yaml"
        custom.write_text(
            "dimensions:\n"
            "  craftsmanship:\n"
            '    builder_metaphor: "Custom metaphor"\n'
            "    inspect:\n"
            '      - "Custom inspect item"\n'
            "    flag:\n"
            '      - "Custom flag item"\n'
            "language_notes:\n"
            "  rust:\n"
            '    - "Borrow checker is your friend"\n',
            encoding="utf-8",
        )
        with patch("rick_mcp.tools.code_review.CODE_REVIEW_OVERRIDE_PATH", custom):
            loaded = _load_rubric()
        assert loaded["dimensions"]["craftsmanship"]["builder_metaphor"] == "Custom metaphor"
        assert "rust" in loaded["language_notes"]

    def test_loader_falls_back_when_override_malformed(self, tmp_path):
        bad = tmp_path / "code_review.yaml"
        bad.write_text("not: a: valid: yaml: structure: [", encoding="utf-8")
        with patch("rick_mcp.tools.code_review.CODE_REVIEW_OVERRIDE_PATH", bad):
            loaded = _load_rubric()
        # Should silently fall through to bundled defaults.
        assert set(loaded["dimensions"].keys()) == {"craftsmanship", "security", "architecture"}

    def test_loader_falls_back_when_override_missing(self):
        nonexistent = Path("/nonexistent/code_review.yaml")
        with patch("rick_mcp.tools.code_review.CODE_REVIEW_OVERRIDE_PATH", nonexistent):
            loaded = _load_rubric()
        # Bundled defaults should load.
        assert "craftsmanship" in loaded["dimensions"]
