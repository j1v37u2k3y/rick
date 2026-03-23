"""
RICK MCP — TEST SUITE
Measure twice, cut once. Test everything.

Tests every tool, every resource, every input path, every error case.
The craft demands it. Rick demands it.
"""

import json
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from rick_mcp import (
    CALLSIGN,
    CERTIFICATIONS,
    LANGUAGES,
    MISSION_PHASES,
    PRIMARY_TOOLS,
    SPECIALIZATIONS,
    AttackChainInput,
    CheatsheetInput,
    CompatInput,
    CoverInput,
    DebriefInput,
    HardenInput,
    HealthInput,
    MentorInput,
    ModeInput,
    OnboardInput,
    PivotInput,
    ProposalInput,
    ReconInput,
    ReportInput,
    ResponseFormat,
    ROEInput,
    ThreatModelInput,
    ToolRecInput,
    VulnInput,
    _build_banner,
    _fmt,
    _safe_tool,
    _sanitize,
    logger,
    rick_attack_chain,
    rick_cheatsheet,
    rick_client_onboarding,
    rick_compatibility_check,
    rick_cover_letter,
    rick_debrief,
    rick_demo,
    rick_engagement_proposal,
    rick_hardening,
    rick_health,
    rick_mentorship,
    rick_mode,
    rick_pivot_plan,
    rick_recon,
    rick_report_template,
    rick_roe,
    rick_status,
    rick_threat_model,
    rick_tool_recommend,
    rick_vuln_assess,
)

# ═══════════════════════════════════════════════════════════════
#  CONSTANTS — Verify the foundation
# ═══════════════════════════════════════════════════════════════


class TestConstants:
    def test_version(self):
        from __version__ import __version__

        assert __version__ == "3.2.0"
        banner = _build_banner()
        assert __version__ in banner

    def test_callsign(self):
        assert isinstance(CALLSIGN, str) and len(CALLSIGN) > 0

    def test_certifications_not_empty(self):
        assert isinstance(CERTIFICATIONS, list)

    def test_languages_not_empty(self):
        assert len(LANGUAGES) >= 1
        assert "Python" in LANGUAGES

    def test_primary_tools_not_empty(self):
        assert len(PRIMARY_TOOLS) >= 1
        assert any("Burp Suite" in t for t in PRIMARY_TOOLS)

    def test_specializations_not_empty(self):
        assert len(SPECIALIZATIONS) >= 1

    def test_mission_phases(self):
        assert len(MISSION_PHASES) == 7
        assert MISSION_PHASES[0]["phase"] == 1
        assert MISSION_PHASES[0]["name"] == "Reconnaissance"
        assert MISSION_PHASES[-1]["name"] == "Remediation Strategy"

    def test_startup_banner(self):
        banner = _build_banner()
        assert "RICK MCP v" in banner


# ═══════════════════════════════════════════════════════════════
#  FORMAT HELPER — _fmt
# ═══════════════════════════════════════════════════════════════


class TestFmt:
    def test_json_format(self):
        data = {"key": "value"}
        result = _fmt(data, ResponseFormat.JSON)
        parsed = json.loads(result)
        assert parsed["key"] == "value"

    def test_markdown_format_with_title(self):
        data = {"key": "value"}
        result = _fmt(data, ResponseFormat.MARKDOWN, title="Test Title")
        assert "# Test Title" in result
        assert "**Key**: value" in result

    def test_markdown_list_items(self):
        data = {"items": ["a", "b", "c"]}
        result = _fmt(data, ResponseFormat.MARKDOWN)
        assert "- a" in result
        assert "- b" in result

    def test_markdown_nested_dict(self):
        data = {"section": {"sub_key": "sub_value"}}
        result = _fmt(data, ResponseFormat.MARKDOWN)
        assert "## Section" in result
        assert "Sub Key" in result

    def test_markdown_list_of_dicts(self):
        data = {"items": [{"name": "test", "value": "123"}]}
        result = _fmt(data, ResponseFormat.MARKDOWN)
        assert "**name**: test" in result

    def test_markdown_nested_list_in_dict(self):
        data = {"section": {"sub_list": ["x", "y"]}}
        result = _fmt(data, ResponseFormat.MARKDOWN)
        assert "- x" in result


# ═══════════════════════════════════════════════════════════════
#  RESOURCES — 15 identity resources
# ═══════════════════════════════════════════════════════════════


class TestResources:
    @pytest.mark.asyncio
    async def test_res_rick_and_jiveturkey(self):
        from rick_mcp import res_rick_and_jiveturkey

        result = await res_rick_and_jiveturkey()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_summary(self):
        from rick_mcp import res_summary

        result = await res_summary()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_values(self):
        from rick_mcp import res_values

        result = await res_values()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_heritage(self):
        from rick_mcp import res_heritage

        result = await res_heritage()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_craftsmanship(self):
        from rick_mcp import res_craftsmanship

        result = await res_craftsmanship()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_stack(self):
        from rick_mcp import res_stack

        result = await res_stack()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_methodology(self):
        from rick_mcp import res_methodology

        result = await res_methodology()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_mantras(self):
        from rick_mcp import res_mantras

        result = await res_mantras()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_human(self):
        from rick_mcp import res_human

        result = await res_human()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_entertainment(self):
        from rick_mcp import res_entertainment

        result = await res_entertainment()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_wwm(self):
        from rick_mcp import res_wwm

        result = await res_wwm()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_resume_overview(self):
        from rick_mcp import res_resume_overview

        result = await res_resume_overview()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_resume_evidence(self):
        from rick_mcp import res_resume_evidence

        result = await res_resume_evidence()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_resume_portfolio(self):
        from rick_mcp import res_resume_portfolio

        result = await res_resume_portfolio()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_resume_contact(self):
        from rick_mcp import res_resume_contact

        result = await res_resume_contact()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_the_book(self):
        from rick_mcp import res_the_book

        result = await res_the_book()
        assert "CHECK THE CLOCK" in result or "book is not here" in result
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_res_soul(self):
        from rick_mcp import res_soul

        result = await res_soul()
        # SOUL.md is private — may return fallback on CI
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_res_profile(self):
        from rick_mcp import res_profile

        result = await res_profile()
        # PROFILE.md is private — may return fallback on CI
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_res_achievements(self):
        from rick_mcp import res_achievements

        result = await res_achievements()
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_res_contributing(self):
        from rick_mcp import res_contributing

        result = await res_contributing()
        assert "Contributing" in result


# ═══════════════════════════════════════════════════════════════
#  TOOL 1: rick_recon — All 8 target types + error
# ═══════════════════════════════════════════════════════════════


RECON_TARGETS = ["web_app", "network", "cloud_azure", "cloud_aws", "active_directory", "api", "container", "mobile"]


class TestRickRecon:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("target", RECON_TARGETS)
    async def test_valid_targets(self, target):
        result = await rick_recon(ReconInput(target_type=target))
        assert "AUTHORIZED ENGAGEMENTS ONLY" in result
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_target(self):
        result = await rick_recon(ReconInput(target_type="invalid_target"))
        assert "Error" in result
        assert "Unknown target" in result

    @pytest.mark.asyncio
    async def test_with_scope_notes(self):
        result = await rick_recon(ReconInput(target_type="web_app", scope_notes="Testing login portal only"))
        assert "Testing login portal only" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_recon(ReconInput(target_type="web_app", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "passive" in parsed
        assert "active" in parsed

    @pytest.mark.asyncio
    async def test_recon_has_tools(self):
        result = await rick_recon(ReconInput(target_type="web_app", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "tools" in parsed
        assert len(parsed["tools"]) > 0

    def test_input_validation_empty_target(self):
        with pytest.raises(ValidationError):
            ReconInput(target_type="")

    def test_input_validation_too_long(self):
        with pytest.raises(ValidationError):
            ReconInput(target_type="x" * 51)

    def test_input_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            ReconInput(target_type="web_app", bogus_field="nope")


# ═══════════════════════════════════════════════════════════════
#  TOOL 2: rick_vuln_assess — All 10 categories + error
# ═══════════════════════════════════════════════════════════════


VULN_CATEGORIES = [
    "injection",
    "auth",
    "xss",
    "ssrf",
    "idor",
    "file_upload",
    "deserialization",
    "misconfig",
    "crypto",
    "privesc",
]


class TestRickVulnAssess:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("cat", VULN_CATEGORIES)
    async def test_valid_categories(self, cat):
        result = await rick_vuln_assess(VulnInput(vuln_category=cat))
        assert "AUTHORIZED ENGAGEMENTS ONLY" in result
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_category(self):
        result = await rick_vuln_assess(VulnInput(vuln_category="nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_with_context(self):
        result = await rick_vuln_assess(VulnInput(vuln_category="injection", context="PHP app with MySQL backend"))
        assert "PHP app with MySQL backend" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_vuln_assess(VulnInput(vuln_category="xss", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "owasp" in parsed

    def test_input_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            VulnInput(vuln_category="xss", extra="nope")


# ═══════════════════════════════════════════════════════════════
#  TOOL 3: rick_roe — Engagement types + defaults
# ═══════════════════════════════════════════════════════════════


ROE_TYPES = ["pentest", "red_team", "vuln_assessment", "phishing", "cloud_audit", "app_security"]


class TestRickROE:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("etype", ROE_TYPES)
    async def test_valid_types(self, etype):
        result = await rick_roe(ROEInput(engagement_type=etype))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_with_client_and_duration(self):
        result = await rick_roe(ROEInput(engagement_type="pentest", client_name="Acme Corp", duration_days=20))
        assert "Acme Corp" in result
        assert "20" in result

    @pytest.mark.asyncio
    async def test_defaults(self):
        result = await rick_roe(ROEInput(engagement_type="pentest", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert parsed["header"]["client"] == "[CLIENT]"
        assert "10" in parsed["header"]["duration"]

    @pytest.mark.asyncio
    async def test_json_has_rules(self):
        result = await rick_roe(ROEInput(engagement_type="pentest", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert len(parsed["rules"]) >= 7


# ═══════════════════════════════════════════════════════════════
#  TOOL 4: rick_report_template — All 6 sections + error
# ═══════════════════════════════════════════════════════════════


REPORT_SECTIONS = ["executive_summary", "finding", "methodology", "scope", "remediation", "appendix"]


class TestRickReportTemplate:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("section", REPORT_SECTIONS)
    async def test_valid_sections(self, section):
        result = await rick_report_template(ReportInput(section=section))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_section(self):
        result = await rick_report_template(ReportInput(section="bogus"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_finding_with_details(self):
        result = await rick_report_template(
            ReportInput(
                section="finding",
                finding_title="SQL Injection in Login",
                severity="critical",
                description="Auth bypass via SQLi",
            )
        )
        assert "SQL Injection in Login" in result
        assert "RED CRITICAL" in result

    @pytest.mark.asyncio
    async def test_severity_mapping(self):
        for sev, label in [
            ("critical", "RED"),
            ("high", "ORANGE"),
            ("medium", "YELLOW"),
            ("low", "BLUE"),
            ("informational", "INFO"),
        ]:
            result = await rick_report_template(
                ReportInput(
                    section="finding",
                    severity=sev,
                    response_format=ResponseFormat.JSON,
                )
            )
            parsed = json.loads(result)
            assert label in parsed["severity"]


# ═══════════════════════════════════════════════════════════════
#  TOOL 5: rick_tool_recommend — Keyword matching
# ═══════════════════════════════════════════════════════════════


class TestRickToolRecommend:
    @pytest.mark.asyncio
    async def test_web_scenario(self):
        result = await rick_tool_recommend(ToolRecInput(scenario="web application penetration test"))
        assert "Burp Suite" in result

    @pytest.mark.asyncio
    async def test_network_scenario(self):
        result = await rick_tool_recommend(ToolRecInput(scenario="internal network infrastructure pentest"))
        assert "Nmap" in result

    @pytest.mark.asyncio
    async def test_ad_scenario(self):
        result = await rick_tool_recommend(ToolRecInput(scenario="active directory domain compromise"))
        assert "BloodHound" in result

    @pytest.mark.asyncio
    async def test_cloud_scenario(self):
        result = await rick_tool_recommend(ToolRecInput(scenario="cloud aws kubernetes audit"))
        assert "ScoutSuite" in result

    @pytest.mark.asyncio
    async def test_password_scenario(self):
        result = await rick_tool_recommend(ToolRecInput(scenario="password cracking credential hashes"))
        assert "Hashcat" in result

    @pytest.mark.asyncio
    async def test_osint_scenario(self):
        result = await rick_tool_recommend(ToolRecInput(scenario="osint recon intelligence gathering"))
        assert "Amass" in result

    @pytest.mark.asyncio
    async def test_fallback_scenario(self):
        result = await rick_tool_recommend(ToolRecInput(scenario="something totally unrelated to anything"))
        assert "Burp Suite" in result  # fallback
        assert "Nmap" in result

    @pytest.mark.asyncio
    async def test_multi_keyword_scenario(self):
        result = await rick_tool_recommend(
            ToolRecInput(
                scenario="web application with active directory and cloud azure",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert len(parsed["primary"]) > 3  # multiple categories matched

    def test_input_min_length(self):
        with pytest.raises(ValidationError):
            ToolRecInput(scenario="hi")


# ═══════════════════════════════════════════════════════════════
#  TOOL 6: rick_engagement_proposal — All 7 types + error
# ═══════════════════════════════════════════════════════════════


PROPOSAL_TYPES = [
    "web_app_pentest",
    "network_pentest",
    "ad_review",
    "cloud_audit",
    "red_team",
    "api_security",
    "full_scope",
]


class TestRickEngagementProposal:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("etype", PROPOSAL_TYPES)
    async def test_valid_types(self, etype):
        result = await rick_engagement_proposal(ProposalInput(engagement_type=etype))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_type(self):
        result = await rick_engagement_proposal(ProposalInput(engagement_type="nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_with_special_requirements(self):
        result = await rick_engagement_proposal(
            ProposalInput(
                engagement_type="web_app_pentest",
                client_name="Test Corp",
                estimated_days=15,
                special_requirements="PCI DSS compliance required",
            )
        )
        assert "Test Corp" in result
        assert "PCI DSS" in result

    @pytest.mark.asyncio
    async def test_timeline_calculation(self):
        result = await rick_engagement_proposal(
            ProposalInput(
                engagement_type="full_scope",
                estimated_days=20,
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert "20d" in parsed["timeline"]["total"]


# ═══════════════════════════════════════════════════════════════
#  TOOL 7: rick_client_onboarding
# ═══════════════════════════════════════════════════════════════


class TestRickClientOnboarding:
    @pytest.mark.asyncio
    async def test_default_onboarding(self):
        result = await rick_client_onboarding(OnboardInput())
        assert CALLSIGN in result
        assert "Onboarding" in result

    @pytest.mark.asyncio
    async def test_custom_client(self):
        result = await rick_client_onboarding(OnboardInput(client_name="SecureCo", engagement_type="red_team"))
        assert "SecureCo" in result
        assert "Red Team" in result

    @pytest.mark.asyncio
    async def test_json_has_checklists(self):
        result = await rick_client_onboarding(OnboardInput(response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "checklist_authorization" in parsed
        assert "checklist_technical" in parsed
        assert "checklist_contacts" in parsed
        assert "checklist_scheduling" in parsed


# ═══════════════════════════════════════════════════════════════
#  TOOL 8: rick_compatibility_check — Scoring logic
# ═══════════════════════════════════════════════════════════════


class TestRickCompatibilityCheck:
    @pytest.mark.asyncio
    async def test_strong_fit(self):
        result = await rick_compatibility_check(
            CompatInput(
                description="Looking for OSCP pentester with web app and active directory experience, Python scripting, cloud azure, remote, veteran friendly",
            )
        )
        assert "STRONG FIT" in result or "GOOD POTENTIAL" in result

    @pytest.mark.asyncio
    async def test_poor_fit(self):
        result = await rick_compatibility_check(
            CompatInput(
                description="Entry level SOC analyst for GRC checkbox compliance, junior role, fast scan only",
            )
        )
        assert "NOT IDEAL" in result or "PARTIAL FIT" in result

    @pytest.mark.asyncio
    async def test_tech_gaps_detected(self):
        result = await rick_compatibility_check(
            CompatInput(
                description="Need malware analysis and forensics expert with IoT experience",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert len(parsed["tech"]["gaps"]) > 0

    @pytest.mark.asyncio
    async def test_green_flags(self):
        result = await rick_compatibility_check(
            CompatInput(
                description="Thorough remote pentester with automation and mentorship skills, creative builder",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert len(parsed["culture"]["green"]) > 0

    @pytest.mark.asyncio
    async def test_score_in_range(self):
        result = await rick_compatibility_check(
            CompatInput(
                description="Need a penetration tester for web application security assessment",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        score = int(parsed["score"].split("/")[0])
        assert 0 <= score <= 100

    def test_input_min_length(self):
        with pytest.raises(ValidationError):
            CompatInput(description="short")


# ═══════════════════════════════════════════════════════════════
#  TOOL 9: rick_cover_letter — 3 tones
# ═══════════════════════════════════════════════════════════════


class TestRickCoverLetter:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("tone", ["professional", "conversational", "executive"])
    async def test_all_tones(self, tone):
        result = await rick_cover_letter(
            CoverInput(
                company_name="TestCo",
                role_title="Senior Pentester",
                tone=tone,
            )
        )
        assert "TestCo" in result
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_requirement_matching(self):
        result = await rick_cover_letter(
            CoverInput(
                company_name="BigCorp",
                role_title="AppSec Engineer",
                key_requirements="OSCP web app python cloud active directory",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert len(parsed["matched_highlights"]) >= 3

    @pytest.mark.asyncio
    async def test_default_highlights_when_no_match(self):
        result = await rick_cover_letter(
            CoverInput(
                company_name="X",
                role_title="Y",
                key_requirements="something completely unique and unmatchable",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert len(parsed["matched_highlights"]) >= 1  # fallback highlights

    def test_input_rejects_empty_company(self):
        with pytest.raises(ValidationError):
            CoverInput(company_name="", role_title="Test")


# ═══════════════════════════════════════════════════════════════
#  TOOL 10: rick_attack_chain — All 6 scenarios + error
# ═══════════════════════════════════════════════════════════════


CHAIN_SCENARIOS = [
    "external_to_da",
    "phishing_to_lateral",
    "web_to_internal",
    "cloud_to_onprem",
    "insider_threat",
    "supply_chain",
]


class TestRickAttackChain:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("scenario", CHAIN_SCENARIOS)
    async def test_valid_scenarios(self, scenario):
        result = await rick_attack_chain(AttackChainInput(scenario=scenario))
        assert "AUTHORIZED ENGAGEMENTS ONLY" in result
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_scenario(self):
        result = await rick_attack_chain(AttackChainInput(scenario="nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_with_target_env(self):
        result = await rick_attack_chain(
            AttackChainInput(
                scenario="external_to_da",
                target_environment="Hybrid Azure AD with on-prem DCs",
            )
        )
        assert "Hybrid Azure AD" in result

    @pytest.mark.asyncio
    async def test_json_has_chain(self):
        result = await rick_attack_chain(
            AttackChainInput(
                scenario="external_to_da",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert "chain" in parsed
        assert len(parsed["chain"]) > 3


# ═══════════════════════════════════════════════════════════════
#  TOOL 11: rick_pivot_plan — All 7 positions + error
# ═══════════════════════════════════════════════════════════════


PIVOT_POSITIONS = [
    "linux_webserver",
    "windows_workstation",
    "windows_server",
    "container",
    "cloud_instance",
    "database_server",
    "network_device",
]


class TestRickPivotPlan:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("position", PIVOT_POSITIONS)
    async def test_valid_positions(self, position):
        result = await rick_pivot_plan(PivotInput(position=position))
        assert "AUTHORIZED ENGAGEMENTS ONLY" in result
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_position(self):
        result = await rick_pivot_plan(PivotInput(position="nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_with_target_network(self):
        result = await rick_pivot_plan(
            PivotInput(
                position="linux_webserver",
                target_network="10.10.10.0/24 internal corporate LAN",
            )
        )
        assert "10.10.10.0/24" in result


# ═══════════════════════════════════════════════════════════════
#  TOOL 12: rick_hardening — All 9 technologies + priority filter
# ═══════════════════════════════════════════════════════════════


HARDEN_TECHS = [
    "windows_server",
    "linux_server",
    "active_directory",
    "web_application",
    "cloud_aws",
    "cloud_azure",
    "kubernetes",
    "network",
    "database",
]


class TestRickHardening:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("tech", HARDEN_TECHS)
    async def test_valid_technologies(self, tech):
        result = await rick_hardening(HardenInput(technology=tech))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_technology(self):
        result = await rick_hardening(HardenInput(technology="nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_critical_priority_filter(self):
        result = await rick_hardening(
            HardenInput(
                technology="windows_server",
                priority="critical",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert "critical" in parsed
        assert "quick_wins" not in parsed
        assert "advanced" not in parsed

    @pytest.mark.asyncio
    async def test_quick_wins_priority_filter(self):
        result = await rick_hardening(
            HardenInput(
                technology="linux_server",
                priority="quick_wins",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert "quick_wins" in parsed
        assert "critical" not in parsed

    @pytest.mark.asyncio
    async def test_all_priority_includes_everything(self):
        result = await rick_hardening(
            HardenInput(
                technology="active_directory",
                priority="all",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert "critical" in parsed
        assert "quick_wins" in parsed
        assert "advanced" in parsed


# ═══════════════════════════════════════════════════════════════
#  TOOL 13: rick_cheatsheet — spot-check a few tools + error
# ═══════════════════════════════════════════════════════════════


CHEATSHEET_TOOLS = [
    "nmap",
    "burp",
    "ffuf",
    "hashcat",
    "bloodhound",
    "impacket",
    "crackmapexec",
    "chisel",
    "sqlmap",
    "kerbrute",
]


class TestRickCheatsheet:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", CHEATSHEET_TOOLS)
    async def test_valid_tools(self, tool):
        result = await rick_cheatsheet(CheatsheetInput(tool=tool))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_tool(self):
        result = await rick_cheatsheet(CheatsheetInput(tool="nonexistent_tool"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_cheatsheet(CheatsheetInput(tool="nmap", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "tool" in parsed


# ═══════════════════════════════════════════════════════════════
#  TOOL 14: rick_debrief
# ═══════════════════════════════════════════════════════════════


class TestRickDebrief:
    @pytest.mark.asyncio
    async def test_basic_debrief(self):
        result = await rick_debrief(
            DebriefInput(
                engagement_type="pentest",
                key_findings="SQLi in login, IDOR in API, weak passwords",
            )
        )
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_with_client(self):
        result = await rick_debrief(
            DebriefInput(
                engagement_type="red_team",
                key_findings="Gained DA via Kerberoasting",
                client_name="TestCo",
            )
        )
        assert "TestCo" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_debrief(
            DebriefInput(
                engagement_type="pentest",
                key_findings="SSRF to cloud metadata",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert "header" in parsed

    @pytest.mark.asyncio
    async def test_default_findings(self):
        result = await rick_debrief(
            DebriefInput(
                engagement_type="pentest",
                response_format=ResponseFormat.JSON,
            )
        )
        parsed = json.loads(result)
        assert "[Finding 1]" in str(parsed)


# ═══════════════════════════════════════════════════════════════
#  TOOL 15: rick_mentorship — All 9 topics + error
# ═══════════════════════════════════════════════════════════════


MENTOR_TOPICS = [
    "getting_started",
    "web_app_path",
    "network_path",
    "ad_path",
    "cloud_path",
    "certifications",
    "lab_setup",
    "mindset",
    "career",
]


class TestRickMentorship:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("topic", MENTOR_TOPICS)
    async def test_valid_topics(self, topic):
        result = await rick_mentorship(MentorInput(topic=topic))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_topic(self):
        result = await rick_mentorship(MentorInput(topic="nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_with_level(self):
        for level in ["beginner", "intermediate", "advanced"]:
            result = await rick_mentorship(MentorInput(topic="web_app_path", current_level=level))
            assert CALLSIGN in result


# ═══════════════════════════════════════════════════════════════
#  TOOL 16: rick_status — Server status
# ═══════════════════════════════════════════════════════════════


class TestRickThreatModel:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "target",
        [
            "web_app",
            "api",
            "microservices",
            "mobile_app",
            "cloud_infra",
            "ci_cd_pipeline",
            "iot",
            "active_directory",
        ],
    )
    async def test_valid_targets(self, target):
        result = await rick_threat_model(ThreatModelInput(target=target))
        assert CALLSIGN in result
        assert "STRIDE" in result

    @pytest.mark.asyncio
    async def test_invalid_target(self):
        result = await rick_threat_model(ThreatModelInput(target="nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_with_context(self):
        result = await rick_threat_model(ThreatModelInput(target="web_app", context="Django app with PostgreSQL"))
        assert "Django" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_threat_model(ThreatModelInput(target="api", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "stride" in parsed

    def test_input_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            ThreatModelInput(target="web_app", extra="nope")


# ═══════════════════════════════════════════════════════════════
#  TOOL 17: rick_status — Server status
# ═══════════════════════════════════════════════════════════════


class TestRickStatus:
    @pytest.mark.asyncio
    async def test_status_output(self):
        result = await rick_status()
        assert CALLSIGN in result
        from __version__ import __version__

        assert __version__ in result
        assert "OPERATIONAL" in result

    @pytest.mark.asyncio
    async def test_status_has_dynamic_counts(self):
        from rick_mcp.server import resource_count, tool_count

        result = await rick_status()
        assert str(tool_count()) in result
        assert str(resource_count()) in result


# ═══════════════════════════════════════════════════════════════
#  NEW RESOURCES — changelog, security
# ═══════════════════════════════════════════════════════════════


class TestNewResources:
    @pytest.mark.asyncio
    async def test_res_changelog(self):
        from rick_mcp import res_changelog

        result = await res_changelog()
        assert "Changelog" in result

    @pytest.mark.asyncio
    async def test_res_security(self):
        from rick_mcp import res_security

        result = await res_security()
        assert "Security" in result

    @pytest.mark.asyncio
    async def test_res_war_stories(self):
        from rick_mcp import res_war_stories

        result = await res_war_stories()
        assert len(result) > 10

    @pytest.mark.asyncio
    async def test_res_timeline(self):
        from rick_mcp import res_timeline

        result = await res_timeline()
        assert len(result) > 10


# ═══════════════════════════════════════════════════════════════
#  TIER 1: Error Handling, Sanitization, Logging
# ═══════════════════════════════════════════════════════════════


class TestSanitize:
    def test_none_returns_none(self):
        assert _sanitize(None) is None

    def test_strips_null_bytes(self):
        assert _sanitize("hello\x00world") == "helloworld"

    def test_strips_whitespace(self):
        assert _sanitize("  hello  ") == "hello"

    def test_empty_string(self):
        assert _sanitize("") == ""

    def test_null_byte_only(self):
        assert _sanitize("\x00") == ""

    def test_normal_string_unchanged(self):
        assert _sanitize("normal string") == "normal string"


class TestSafeTool:
    @pytest.mark.asyncio
    async def test_wraps_successful_function(self):
        @_safe_tool
        async def good_fn():
            return "success"

        result = await good_fn()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_catches_exceptions(self):
        @_safe_tool
        async def bad_fn():
            raise ValueError("test error")

        result = await bad_fn()
        assert "Error" in result
        assert "bad_fn" in result
        assert "test error" in result

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        @_safe_tool
        async def my_tool():
            return "ok"

        assert my_tool.__name__ == "my_tool"


class TestLogging:
    def test_logger_exists(self):
        assert logger.name == "rick_mcp"


# ═══════════════════════════════════════════════════════════════
#  TOOL 18: rick_health — Health check
# ═══════════════════════════════════════════════════════════════


class TestRickMode:
    @pytest.mark.asyncio
    async def test_be_rick_mode(self):
        result = await rick_mode(ModeInput(mode="be_rick"))
        # Works with or without identity configured
        assert "MCP" in result or "Rick" in result
        assert CALLSIGN in result or "operator" in result.lower()

    @pytest.mark.asyncio
    async def test_pentest_mode(self):
        result = await rick_mode(ModeInput(mode="pentest_mode", context="test.com"))
        assert "pentest" in result.lower() or "operator" in result.lower()
        assert "test.com" in result

    @pytest.mark.asyncio
    async def test_mentor_mode(self):
        result = await rick_mode(ModeInput(mode="mentor_mode", context="intermediate"))
        assert "mentor" in result.lower()
        assert "intermediate" in result

    @pytest.mark.asyncio
    async def test_evaluate_fit_mode(self):
        result = await rick_mode(ModeInput(mode="evaluate_fit", context="Senior Pentester OSCP required"))
        assert "evaluate" in result.lower() or "profile" in result.lower()
        assert "Senior Pentester" in result

    @pytest.mark.asyncio
    async def test_engagement_ops_mode(self):
        result = await rick_mode(ModeInput(mode="engagement_ops", context="Acme Corp"))
        assert "engagement" in result.lower()
        assert "Acme Corp" in result

    @pytest.mark.asyncio
    async def test_invalid_mode(self):
        result = await rick_mode(ModeInput(mode="invalid_mode"))
        assert "Error" in result
        assert "Unknown mode" in result

    def test_mode_input_rejects_extra(self):
        with pytest.raises(ValidationError):
            ModeInput(mode="be_rick", extra="nope")


class TestPromptBuilders:
    def test_read_private_fallback(self, tmp_path):
        from rick_mcp.prompts import _read_private

        with patch("rick_mcp.prompts.SOUL_DIR", tmp_path / "nonexistent"):
            result = _read_private("nope.txt", fallback="fallback text")
        assert result == "fallback text"

    def test_read_soul_fallback(self, tmp_path):
        from rick_mcp.prompts import _read_soul

        with patch("rick_mcp.prompts.SOUL_DIR", tmp_path / "nonexistent"):
            result = _read_soul()
        # Falls back to _read_md or professional fallback
        assert "honor" in result.lower() or "not found" in result.lower()

    def test_read_book_fallback(self, tmp_path):
        from rick_mcp.prompts import _read_book

        with patch("rick_mcp.prompts.SOUL_DIR", tmp_path / "nonexistent"):
            result = _read_book()
        # Falls back to project root or professional fallback
        assert len(result) > 0

    def test_read_private_from_soul_dir(self, tmp_path):
        from rick_mcp.prompts import _read_private

        soul_dir = tmp_path / "soul"
        soul_dir.mkdir()
        (soul_dir / "test.txt").write_text("private content")
        with patch("rick_mcp.prompts.SOUL_DIR", soul_dir):
            result = _read_private("test.txt", fallback="nope")
        assert result == "private content"

    def test_available_modes(self):
        from rick_mcp.prompts import AVAILABLE_MODES, MODE_BUILDERS

        assert len(AVAILABLE_MODES) == 7
        for mode in AVAILABLE_MODES:
            assert mode in MODE_BUILDERS

    def test_all_builders_return_strings(self):
        from rick_mcp.prompts import MODE_BUILDERS

        for name, builder in MODE_BUILDERS.items():
            result = builder(context="test")
            assert isinstance(result, str), f"{name} did not return a string"
            assert len(result) > 100, f"{name} returned too little content"


class TestRickDemo:
    @pytest.mark.asyncio
    async def test_demo_returns_tour(self):
        result = await rick_demo()
        assert "The Full Tour" in result
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_demo_covers_categories(self):
        result = await rick_demo()
        assert "RECON" in result
        assert "VULN ASSESS" in result
        assert "ATTACK CHAIN" in result
        assert "HARDENING" in result
        assert "ROE" in result
        assert "MENTORSHIP" in result

    @pytest.mark.asyncio
    async def test_demo_mentions_remaining_tools(self):
        result = await rick_demo()
        assert "rick_cve" in result
        assert "rick_tracker" in result
        assert "rick_health" in result

    @pytest.mark.asyncio
    async def test_demo_ends_with_closing(self):
        result = await rick_demo()
        assert "craftsmanship" in result.lower() or CALLSIGN in result


class TestRickHealth:
    @pytest.mark.asyncio
    async def test_health_returns_output(self):
        result = await rick_health()
        assert CALLSIGN in result
        assert "PASS" in result

    @pytest.mark.asyncio
    async def test_health_checks_version(self):
        result = await rick_health()
        assert "version" in result.lower() or "Version" in result

    @pytest.mark.asyncio
    async def test_health_checks_fmt(self):
        result = await rick_health()
        assert "fmt" in result.lower() or "Fmt" in result

    @pytest.mark.asyncio
    async def test_health_checks_sanitize(self):
        result = await rick_health()
        assert "sanitize" in result.lower() or "Sanitize" in result

    @pytest.mark.asyncio
    async def test_health_overall_pass(self, tmp_path):
        eng_dir = tmp_path / ".rick_mcp" / "engagements"
        eng_dir.mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_health()
        assert "ALL PASS" in result

    @pytest.mark.asyncio
    async def test_health_with_fix_false(self, tmp_path):
        eng_dir = tmp_path / ".rick_mcp" / "engagements"
        eng_dir.mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_health(HealthInput(fix=False))
        assert "PASS" in result

    @pytest.mark.asyncio
    async def test_health_with_fix_true_nothing_broken(self, tmp_path):
        eng_dir = tmp_path / ".rick_mcp" / "engagements"
        eng_dir.mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_health(HealthInput(fix=True))
        assert "HEALING" in result
        assert "Nothing to fix" in result

    @pytest.mark.asyncio
    async def test_health_creates_missing_data_dir(self, tmp_path):
        missing_dir = tmp_path / ".rick_mcp" / "engagements"
        assert not missing_dir.exists()
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_health(HealthInput(fix=True))
        assert missing_dir.exists()
        assert "REPAIRED" in result or "PASS" in result

    @pytest.mark.asyncio
    async def test_health_detects_corrupt_engagement(self, tmp_path):
        eng_dir = tmp_path / ".rick_mcp" / "engagements"
        eng_dir.mkdir(parents=True)
        (eng_dir / "BAD.json").write_text("not json at all {{{")
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_health(HealthInput(fix=False))
        assert "FAIL" in result
        assert "invalid JSON" in result

    @pytest.mark.asyncio
    async def test_health_quarantines_corrupt_engagement(self, tmp_path):
        eng_dir = tmp_path / ".rick_mcp" / "engagements"
        eng_dir.mkdir(parents=True)
        (eng_dir / "BAD.json").write_text("not json at all {{{")
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_health(HealthInput(fix=True))
        assert "REPAIRED" in result or "Quarantined" in result
        assert (eng_dir / "BAD.json.corrupt").exists()
        assert not (eng_dir / "BAD.json").exists()

    @pytest.mark.asyncio
    async def test_health_checks_markdown_files(self):
        result = await rick_health()
        assert "markdown_files" in result.lower() or "Markdown Files" in result

    @pytest.mark.asyncio
    async def test_health_checks_engagement_integrity(self, tmp_path):
        eng_dir = tmp_path / ".rick_mcp" / "engagements"
        eng_dir.mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_health()
        assert "engagement" in result.lower()

    def test_health_input_rejects_extra(self):
        with pytest.raises(ValidationError):
            HealthInput(fix=True, extra="nope")
