"""Tests for prompt builders — philosophy expansion across be_rick, jarvis, mentor_mode."""

from unittest.mock import patch

PHILOSOPHY_SUBHEADINGS = (
    "### Values",
    "### Craftsmanship",
    "### Heritage",
    "### Human",
    "### Mantras",
    "### Rick &",
)

PHILOSOPHY_READ_MARKERS = (
    "<<VALUES>>",
    "<<CRAFTSMANSHIP>>",
    "<<HERITAGE>>",
    "<<HUMAN>>",
    "<<MANTRAS>>",
    "<<RICK_AND_JIVETURKEY>>",
)


class TestBuildJarvisPhilosophy:
    def test_includes_operator_philosophy_section(self):
        from rick_mcp.prompts import build_jarvis

        result = build_jarvis()
        assert "## Operator Philosophy" in result

    def test_includes_decision_filters_section(self):
        from rick_mcp.prompts import build_jarvis

        result = build_jarvis()
        assert "## Decision Filters" in result

    def test_philosophy_section_has_six_subsections(self):
        from rick_mcp.prompts import build_jarvis

        result = build_jarvis()
        for heading in PHILOSOPHY_SUBHEADINGS:
            assert heading in result, f"missing heading: {heading}"

    def test_reads_all_six_profile_files(self):
        from rick_mcp.prompts import build_jarvis

        with patch("rick_mcp.prompts._read_soul", return_value="SOUL"):
            with patch("rick_mcp.formatting._read_data") as mock_read:
                mock_read.side_effect = lambda category, name: f"<<{name.upper()}>>"
                result = build_jarvis()

        for marker in (
            "<<SUMMARY>>",
            "<<STACK>>",
            "<<METHODOLOGY>>",
            *PHILOSOPHY_READ_MARKERS,
        ):
            assert marker in result, f"missing read: {marker}"

    def test_decision_filters_carry_behavioral_rules(self):
        from rick_mcp.prompts import build_jarvis

        result = build_jarvis()
        # The section's job is to translate values into prescriptive rules.
        # Spot-check a few load-bearing ones.
        for rule_marker in (
            "Thorough > Fast",
            "Manual depth",
            "Honesty above all",
            "Builder's eye",
            "No checkbox compliance",
            "Chain over single-vuln",
        ):
            assert rule_marker in result, f"missing decision filter: {rule_marker}"

    def test_philosophy_appears_before_jarvis_protocol(self):
        from rick_mcp.prompts import build_jarvis

        result = build_jarvis()
        philosophy_idx = result.index("## Operator Philosophy")
        filters_idx = result.index("## Decision Filters")
        protocol_idx = result.index("## JARVIS Protocol")
        assert philosophy_idx < filters_idx < protocol_idx

    def test_target_acquired_path(self):
        from rick_mcp.prompts import build_jarvis

        result = build_jarvis(target="example.com")
        assert "Target acquired" in result
        assert "example.com" in result

    def test_no_target_path(self):
        from rick_mcp.prompts import build_jarvis

        result = build_jarvis()
        assert "JARVIS is online" in result

    def test_works_when_profile_files_missing(self, tmp_path, monkeypatch):
        """Generic fallback path — no ~/.rick_mcp/profiles AND no bundled data files."""
        from rick_mcp.prompts import build_jarvis

        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        with patch("rick_mcp.formatting._read_data") as mock_read:
            mock_read.return_value = "Content for profiles/x not configured."
            result = build_jarvis()

        # Even with no profile content, structure must hold.
        assert "## Operator Philosophy" in result
        assert "## Decision Filters" in result
        assert "## JARVIS Protocol" in result


class TestBuildBeRickPhilosophy:
    def test_includes_operator_philosophy_section(self):
        from rick_mcp.prompts import build_be_rick

        result = build_be_rick()
        assert "## Operator Philosophy" in result

    def test_philosophy_section_has_six_subsections(self):
        from rick_mcp.prompts import build_be_rick

        result = build_be_rick()
        for heading in PHILOSOPHY_SUBHEADINGS:
            assert heading in result, f"missing heading: {heading}"

    def test_reads_all_six_profile_files(self):
        from rick_mcp.prompts import build_be_rick

        with patch("rick_mcp.formatting._read_data") as mock_read:
            mock_read.side_effect = lambda category, name: f"<<{name.upper()}>>"
            result = build_be_rick()

        for marker in PHILOSOPHY_READ_MARKERS:
            assert marker in result, f"missing read: {marker}"

    def test_no_decision_filters_block(self):
        """Decision Filters are JARVIS-specific; be_rick is conversational, not tactical."""
        from rick_mcp.prompts import build_be_rick

        result = build_be_rick()
        assert "## Decision Filters" not in result

    def test_philosophy_appears_after_book_before_methodology(self):
        from rick_mcp.prompts import build_be_rick

        result = build_be_rick()
        book_idx = result.index("## The Book")
        philosophy_idx = result.index("## Operator Philosophy")
        methodology_idx = result.index("## Your Methodology")
        assert book_idx < philosophy_idx < methodology_idx


class TestBuildMentorModePhilosophy:
    def test_includes_operator_philosophy_section(self):
        from rick_mcp.prompts import build_mentor_mode

        result = build_mentor_mode()
        assert "## Operator Philosophy" in result

    def test_philosophy_section_has_six_subsections(self):
        from rick_mcp.prompts import build_mentor_mode

        result = build_mentor_mode()
        for heading in PHILOSOPHY_SUBHEADINGS:
            assert heading in result, f"missing heading: {heading}"

    def test_reads_all_six_profile_files(self):
        from rick_mcp.prompts import build_mentor_mode

        with patch("rick_mcp.formatting._read_data") as mock_read:
            mock_read.side_effect = lambda category, name: f"<<{name.upper()}>>"
            result = build_mentor_mode()

        for marker in PHILOSOPHY_READ_MARKERS:
            assert marker in result, f"missing read: {marker}"

    def test_no_decision_filters_block(self):
        from rick_mcp.prompts import build_mentor_mode

        result = build_mentor_mode()
        assert "## Decision Filters" not in result

    def test_philosophy_appears_after_book_before_what_you_teach(self):
        from rick_mcp.prompts import build_mentor_mode

        result = build_mentor_mode()
        book_idx = result.index("## The Book")
        philosophy_idx = result.index("## Operator Philosophy")
        teach_idx = result.index("## What You Teach")
        assert book_idx < philosophy_idx < teach_idx


class TestBuildOtherPromptsUntouched:
    """dick_mode, pentest_mode, evaluate_fit, engagement_ops should NOT have philosophy."""

    def test_dick_mode_no_philosophy(self):
        from rick_mcp.prompts import build_dick_mode

        result = build_dick_mode()
        assert "## Operator Philosophy" not in result

    def test_pentest_mode_no_philosophy(self):
        from rick_mcp.prompts import build_pentest_mode

        result = build_pentest_mode()
        assert "## Operator Philosophy" not in result

    def test_evaluate_fit_no_philosophy(self):
        from rick_mcp.prompts import build_evaluate_fit

        result = build_evaluate_fit()
        assert "## Operator Philosophy" not in result

    def test_engagement_ops_no_philosophy(self):
        from rick_mcp.prompts import build_engagement_ops

        result = build_engagement_ops()
        assert "## Operator Philosophy" not in result
