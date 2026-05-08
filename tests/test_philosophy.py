"""Tests for rick_mcp.philosophy + its wiring into rick_tool_recommend / rick_threat_model."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from rick_mcp.constants import ResponseFormat
from rick_mcp.models import ThreatModelInput, ToolRecInput
from rick_mcp.philosophy import (
    ARSENAL_CHAIN,
    CORE_PRINCIPLES,
    DECISION_FILTERS,
    METHODOLOGY_GATE_KEYWORDS,
    PHILOSOPHY_BUNDLED_PATH,
    STRIDE_FILTER_MAP,
    STRIDE_PRINCIPLE_ANCHORS,
    VALIDATION_RULES,
    _load_philosophy,
    apply_filters,
    chain_for,
    chain_validation,
    filters_for_stride,
    infer_methodology_gate,
    principle_anchors,
)
from rick_mcp.tools.offensive import rick_tool_recommend
from rick_mcp.tools.offensive_tradecraft import rick_threat_model

# ═══════════════════════════════════════════════════════════════
#  Module structure — single source of truth
# ═══════════════════════════════════════════════════════════════


class TestPhilosophyModule:
    def test_core_principles_count(self):
        # 7 soul values from SOUL.md — locked-down count so accidental
        # additions/removals trip a test.
        assert len(CORE_PRINCIPLES) == 7

    def test_core_principles_have_operational_meaning(self):
        for slug, body in CORE_PRINCIPLES.items():
            assert isinstance(slug, str) and slug
            assert isinstance(body, str) and len(body) > 20

    def test_decision_filters_count(self):
        # 9 active constraints from build_jarvis (prompts.py:633-645).
        assert len(DECISION_FILTERS) == 9

    def test_decision_filters_shape(self):
        required = {"slug", "name", "rule", "triggers"}
        for f in DECISION_FILTERS:
            assert required.issubset(f.keys())
            assert isinstance(f["triggers"], list) and f["triggers"]

    def test_validation_rules_count(self):
        # 5 RoE rules. Locking this down so the engagement contract isn't
        # silently weakened.
        assert len(VALIDATION_RULES) == 5

    def test_methodology_gate_keywords_cover_all_phases(self):
        # Every keyword group must point at a real MISSION_PHASES name.
        from rick_mcp.constants import MISSION_PHASES

        phase_names = {p["name"] for p in MISSION_PHASES}
        for _, name in METHODOLOGY_GATE_KEYWORDS:
            assert name in phase_names

    def test_stride_principle_anchors_use_real_principle_slugs(self):
        for category, slugs in STRIDE_PRINCIPLE_ANCHORS.items():
            for slug in slugs:
                assert slug in CORE_PRINCIPLES, f"{category} → unknown principle {slug}"

    def test_stride_filter_map_uses_real_filter_slugs(self):
        valid = {f["slug"] for f in DECISION_FILTERS}
        for category, slugs in STRIDE_FILTER_MAP.items():
            for slug in slugs:
                assert slug in valid, f"{category} → unknown filter {slug}"


# ═══════════════════════════════════════════════════════════════
#  Helper functions — apply_filters / infer_methodology_gate / chain_for
# ═══════════════════════════════════════════════════════════════


class TestApplyFilters:
    def test_empty_text_returns_empty(self):
        assert apply_filters("") == []
        assert apply_filters(None) == []  # type: ignore[arg-type]

    def test_recon_text_fires_thorough_over_fast(self):
        result = apply_filters("network recon and port scan")
        slugs = [f["slug"] for f in result]
        assert "thorough_over_fast" in slugs

    def test_scanner_text_fires_manual_over_scanner(self):
        result = apply_filters("Nuclei scanner sweep with automated templates")
        slugs = [f["slug"] for f in result]
        assert "manual_over_scanner" in slugs

    def test_finding_text_fires_chain_and_honesty(self):
        result = apply_filters("vuln finding chain")
        slugs = [f["slug"] for f in result]
        assert "chain_over_isolation" in slugs
        assert "honesty_above_all" in slugs


class TestInferMethodologyGate:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("active directory recon and OSINT", "Reconnaissance"),
            ("vulnerability scan of the web app", "Vulnerability Assessment"),
            ("SQL injection exploit chain", "Exploitation"),
            ("linux privesc via SUID", "Privilege Escalation"),
            ("lateral movement with psexec", "Lateral Movement"),
            ("write up the report and document evidence", "Documentation"),
            ("hardening blueprint and detection rules", "Remediation Strategy"),
        ],
    )
    def test_keyword_to_phase(self, text, expected):
        assert infer_methodology_gate(text) == expected

    def test_unknown_text_falls_back_to_recon(self):
        # Default starting phase when nothing matches.
        assert infer_methodology_gate("xyz qwerty") == "Reconnaissance"

    def test_empty_text_falls_back_to_recon(self):
        assert infer_methodology_gate("") == "Reconnaissance"


class TestChainFor:
    def test_web_scenario_chains_vuln_assess(self):
        chain = chain_for("web application penetration test")
        assert "rick_vuln_assess" in chain

    def test_cloud_scenario_chains_cloud_attack_path(self):
        chain = chain_for("aws cloud audit")
        assert "rick_cloud_attack_path" in chain

    def test_chain_dedup(self):
        # 'web' and 'http' both map to the same chain row, so duplicates
        # must collapse.
        chain = chain_for("web http api")
        assert chain.count("rick_vuln_assess") == 1

    def test_empty_returns_empty(self):
        assert chain_for("") == []


class TestPrincipleAnchors:
    def test_known_category(self):
        assert "do_no_harm" in principle_anchors("denial_of_service")

    def test_unknown_returns_empty(self):
        assert principle_anchors("unknown_pillar") == []


class TestFiltersForStride:
    def test_known_category_returns_filter_dicts(self):
        result = filters_for_stride("spoofing")
        assert result
        for entry in result:
            assert {"slug", "name", "rule"}.issubset(entry.keys())

    def test_unknown_returns_empty(self):
        assert filters_for_stride("nope") == []

    def test_every_stride_pillar_has_filters(self):
        for category in STRIDE_FILTER_MAP:
            assert filters_for_stride(category)


class TestChainValidation:
    def test_each_stride_category_has_a_chain_note(self):
        for category in STRIDE_PRINCIPLE_ANCHORS:
            assert chain_validation(category)

    def test_unknown_returns_empty(self):
        assert chain_validation("nope") == ""


# ═══════════════════════════════════════════════════════════════
#  Wiring — rick_tool_recommend
# ═══════════════════════════════════════════════════════════════


class TestToolRecommendWiring:
    @pytest.mark.asyncio
    async def test_decision_filters_present_for_audit_scenario(self):
        # "audit" + "scanner" — should fire no_checkbox_compliance and manual_over_scanner.
        result = await rick_tool_recommend(
            ToolRecInput(
                scenario="web application audit using scanner output",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert "decision_filters_applied" in parsed
        assert any("Manual depth" in f or "checkbox" in f.lower() for f in parsed["decision_filters_applied"])

    @pytest.mark.asyncio
    async def test_methodology_gate_present(self):
        result = await rick_tool_recommend(
            ToolRecInput(scenario="osint recon and intelligence gathering", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert parsed["methodology_gate"] == "Reconnaissance"

    @pytest.mark.asyncio
    async def test_validation_checklist_always_present(self):
        result = await rick_tool_recommend(
            ToolRecInput(scenario="literally anything xyz", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert parsed["validation_checklist"] == VALIDATION_RULES

    @pytest.mark.asyncio
    async def test_chain_to_present_for_known_scenario(self):
        result = await rick_tool_recommend(
            ToolRecInput(scenario="active directory domain compromise", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert "rick_attack_chain" in parsed["chain_to"]

    @pytest.mark.asyncio
    async def test_markdown_format_renders_filter_section(self):
        result = await rick_tool_recommend(ToolRecInput(scenario="web application audit"))
        # Output uses _fmt — list keys become headers via title-case.
        assert "Decision Filters Applied" in result
        assert "Validation Checklist" in result


# ═══════════════════════════════════════════════════════════════
#  Wiring — rick_threat_model
# ═══════════════════════════════════════════════════════════════


class TestThreatModelWiring:
    @pytest.mark.asyncio
    async def test_each_stride_category_has_decision_filters(self):
        result = await rick_threat_model(ThreatModelInput(target="web_app", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        for category, payload in parsed["stride"].items():
            # Filters fire on the threats text for every standard STRIDE
            # category — locking that contract here.
            assert "decision_filters" in payload, f"{category} missing decision_filters"
            assert payload["decision_filters"], f"{category} has empty filter list"

    @pytest.mark.asyncio
    async def test_each_stride_category_has_chain_validation(self):
        result = await rick_threat_model(ThreatModelInput(target="api", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        for category, payload in parsed["stride"].items():
            assert payload.get("chain_validation"), f"{category} missing chain_validation"

    @pytest.mark.asyncio
    async def test_each_stride_category_has_principle_anchors(self):
        result = await rick_threat_model(ThreatModelInput(target="cloud_infra", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        for category, payload in parsed["stride"].items():
            anchors = payload.get("core_principle_anchors")
            assert anchors, f"{category} missing core_principle_anchors"
            for slug in anchors:
                assert slug in CORE_PRINCIPLES

    @pytest.mark.asyncio
    async def test_threat_model_markdown_renders_anchors(self):
        result = await rick_threat_model(ThreatModelInput(target="active_directory"))
        # Anchors live inside the stride dict; _fmt uses title-cased keys.
        assert "core_principle_anchors" in result.lower() or "Core Principle Anchors" in result


# ═══════════════════════════════════════════════════════════════
#  Sanity — arsenal chain table is non-empty and well-formed
# ═══════════════════════════════════════════════════════════════


class TestArsenalChain:
    def test_arsenal_chain_non_empty(self):
        assert ARSENAL_CHAIN

    def test_arsenal_chain_targets_are_tool_names(self):
        for _keywords, targets in ARSENAL_CHAIN:
            for t in targets:
                assert t.startswith("rick_"), f"chain target {t} not a rick_* tool name"


# ═══════════════════════════════════════════════════════════════
#  YAML loader — bundled defaults + override path
# ═══════════════════════════════════════════════════════════════


class TestPhilosophyLoader:
    def test_bundled_yaml_exists(self):
        # Bundled defaults must ship with the package.
        assert PHILOSOPHY_BUNDLED_PATH.exists()

    def test_loader_returns_required_top_level_keys(self):
        loaded = _load_philosophy()
        assert "core_principles" in loaded
        assert "decision_filters" in loaded
        assert "validation_rules" in loaded

    def test_bundled_yaml_parses_to_module_constants(self):
        # When override doesn't exist, loader returns the bundled content;
        # module-level constants should match.
        loaded = _load_philosophy()
        assert loaded["core_principles"] == CORE_PRINCIPLES
        assert loaded["decision_filters"] == DECISION_FILTERS
        assert loaded["validation_rules"] == VALIDATION_RULES

    def test_override_path_takes_precedence(self, tmp_path):
        # Write a custom philosophy.yaml at a fake override path and confirm
        # the loader picks it up over the bundled file.
        custom = tmp_path / "philosophy.yaml"
        custom.write_text(
            "core_principles:\n"
            '  custom_value: "Test override"\n'
            "decision_filters:\n"
            "  - slug: test_filter\n"
            '    name: "Test Filter"\n'
            '    rule: "Test rule"\n'
            "    triggers: [test]\n"
            "validation_rules:\n"
            '  - "Test validation rule"\n',
            encoding="utf-8",
        )
        with patch("rick_mcp.philosophy.PHILOSOPHY_OVERRIDE_PATH", custom):
            loaded = _load_philosophy()
        assert "custom_value" in loaded["core_principles"]
        assert loaded["decision_filters"][0]["slug"] == "test_filter"

    def test_loader_falls_back_when_override_malformed(self, tmp_path):
        bad = tmp_path / "philosophy.yaml"
        bad.write_text("not: a: valid: yaml: structure: [", encoding="utf-8")
        with patch("rick_mcp.philosophy.PHILOSOPHY_OVERRIDE_PATH", bad):
            loaded = _load_philosophy()
        # Should silently fall through to bundled.
        assert "do_no_harm" in loaded["core_principles"]

    def test_loader_falls_back_when_override_missing(self):
        nonexistent = Path("/nonexistent/philosophy.yaml")
        with patch("rick_mcp.philosophy.PHILOSOPHY_OVERRIDE_PATH", nonexistent):
            loaded = _load_philosophy()
        # Bundled defaults should load.
        assert "do_no_harm" in loaded["core_principles"]
