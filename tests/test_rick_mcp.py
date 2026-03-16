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
    STARTUP_BANNER,
    AttackChainInput,
    CheatsheetInput,
    CompatInput,
    CoverInput,
    CVEInput,
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
    ToolRecInput,
    TrackerInput,
    VulnInput,
    _fmt,
    _safe_tool,
    _sanitize,
    logger,
    mcp,
    rick_attack_chain,
    rick_cheatsheet,
    rick_client_onboarding,
    rick_compatibility_check,
    rick_cover_letter,
    rick_cve,
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
    rick_tool_recommend,
    rick_tracker,
    rick_vuln_assess,
)

# ═══════════════════════════════════════════════════════════════
#  CONSTANTS — Verify the foundation
# ═══════════════════════════════════════════════════════════════


class TestConstants:
    def test_version(self):
        from __version__ import __version__

        assert __version__ == "1.0.0"
        assert __version__ in STARTUP_BANNER

    def test_callsign(self):
        assert CALLSIGN == "j1v37u2k3y"

    def test_certifications_not_empty(self):
        assert len(CERTIFICATIONS) >= 5
        assert "OSCP (2019)" in CERTIFICATIONS

    def test_languages_not_empty(self):
        assert len(LANGUAGES) >= 10
        assert "Python" in LANGUAGES

    def test_primary_tools_not_empty(self):
        assert len(PRIMARY_TOOLS) >= 15
        assert "Burp Suite (preferred proxy)" in PRIMARY_TOOLS

    def test_specializations_not_empty(self):
        assert len(SPECIALIZATIONS) >= 7

    def test_mission_phases(self):
        assert len(MISSION_PHASES) == 7
        assert MISSION_PHASES[0]["phase"] == 1
        assert MISSION_PHASES[0]["name"] == "Reconnaissance"
        assert MISSION_PHASES[-1]["name"] == "Remediation Strategy"

    def test_startup_banner(self):
        assert "RICK MCP v1.0" in STARTUP_BANNER
        assert "SEMPER FIDELIS" in STARTUP_BANNER


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
        assert "Rick and jiveturkey" in result
        assert "Rick" in result
        assert "jiveturkey" in result

    @pytest.mark.asyncio
    async def test_res_summary(self):
        from rick_mcp import res_summary

        result = await res_summary()
        assert "j1v37u2k3y" in result
        assert "OSCP" in result

    @pytest.mark.asyncio
    async def test_res_values(self):
        from rick_mcp import res_values

        result = await res_values()
        assert "Honor" in result
        assert "Courage" in result
        assert "Commitment" in result
        assert "Honesty" in result

    @pytest.mark.asyncio
    async def test_res_heritage(self):
        from rick_mcp import res_heritage

        result = await res_heritage()
        assert "Lineage" in result
        assert "Builder Bloodline" in result
        assert "Rick to jiveturkey" in result

    @pytest.mark.asyncio
    async def test_res_craftsmanship(self):
        from rick_mcp import res_craftsmanship

        result = await res_craftsmanship()
        assert "Philosophy" in result
        assert "Tradecraft Principles" in result
        assert "Builder to Breaker" in result

    @pytest.mark.asyncio
    async def test_res_stack(self):
        from rick_mcp import res_stack

        result = await res_stack()
        assert "Languages" in result
        assert "Offensive Tools" in result
        assert "Python" in result

    @pytest.mark.asyncio
    async def test_res_methodology(self):
        from rick_mcp import res_methodology

        result = await res_methodology()
        assert "Phase 7" in result
        assert "OWASP" in result

    @pytest.mark.asyncio
    async def test_res_mantras(self):
        from rick_mcp import res_mantras

        result = await res_mantras()
        assert "Operational" in result
        assert "SEMPER FIDELIS" in result

    @pytest.mark.asyncio
    async def test_res_human(self):
        from rick_mcp import res_human

        result = await res_human()
        assert "Father" in result
        assert "Cycle Breaker" in result
        assert "Ever Evolving" in result
        assert "The Poet" in result

    @pytest.mark.asyncio
    async def test_res_entertainment(self):
        from rick_mcp import res_entertainment

        result = await res_entertainment()
        assert "Always Sunny" in result
        assert "Rick & Morty" in result

    @pytest.mark.asyncio
    async def test_res_wwm(self):
        from rick_mcp import res_wwm

        result = await res_wwm()
        assert "Working With Me" in result
        assert "Semper Fidelis" in result
        assert "OSCP" in result

    @pytest.mark.asyncio
    async def test_res_resume_overview(self):
        from rick_mcp import res_resume_overview

        result = await res_resume_overview()
        assert "j1v37u2k3y" in result
        assert "How to Evaluate" in result

    @pytest.mark.asyncio
    async def test_res_resume_evidence(self):
        from rick_mcp import res_resume_evidence

        result = await res_resume_evidence()
        assert "Exhibits" in result or "rick_recon" in result
        assert "rick_recon" in result

    @pytest.mark.asyncio
    async def test_res_resume_portfolio(self):
        from rick_mcp import res_resume_portfolio

        result = await res_resume_portfolio()
        assert "Public" in result
        assert "Gated" in result

    @pytest.mark.asyncio
    async def test_res_resume_contact(self):
        from rick_mcp import res_resume_contact

        result = await res_resume_contact()
        assert "Ready For" in result
        assert "Next Steps" in result
        assert "jiveturkey.rocks/about" in result

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
        assert "HONOR" in result.upper() or "not found" in result.lower()

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
        assert "Birth of Rick" in result

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
        assert "Semper Fidelis" in result

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
        from rick_mcp import ThreatModelInput, rick_threat_model

        result = await rick_threat_model(ThreatModelInput(target=target))
        assert CALLSIGN in result
        assert "STRIDE" in result

    @pytest.mark.asyncio
    async def test_invalid_target(self):
        from rick_mcp import ThreatModelInput, rick_threat_model

        result = await rick_threat_model(ThreatModelInput(target="nope"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_with_context(self):
        from rick_mcp import ThreatModelInput, rick_threat_model

        result = await rick_threat_model(ThreatModelInput(target="web_app", context="Django app with PostgreSQL"))
        assert "Django" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        from rick_mcp import ThreatModelInput, rick_threat_model

        result = await rick_threat_model(ThreatModelInput(target="api", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "stride" in parsed

    def test_input_rejects_extra_fields(self):
        from rick_mcp import ThreatModelInput

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
        assert "1.0.0" in result
        assert "OPERATIONAL" in result

    @pytest.mark.asyncio
    async def test_status_has_counts(self):
        result = await rick_status()
        assert "22" in result  # resource count
        assert "22" in result  # tool count


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
        assert "jiveturkey.rocks/about" in result


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
        assert "Rick" in result
        assert CALLSIGN in result

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

        assert len(AVAILABLE_MODES) == 5
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
    async def test_demo_ends_with_semper_fi(self):
        result = await rick_demo()
        assert "Semper Fidelis" in result


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


# ═══════════════════════════════════════════════════════════════
#  TOOL 19: rick_cve — NVD CVE Lookup (mocked)
# ═══════════════════════════════════════════════════════════════


class TestRickCVE:
    @pytest.mark.asyncio
    async def test_cve_lookup_mocked(self):
        mock_response = json.dumps(
            {
                "totalResults": 1,
                "vulnerabilities": [
                    {
                        "cve": {
                            "id": "CVE-2021-44228",
                            "descriptions": [{"lang": "en", "value": "Apache Log4j2 RCE vulnerability"}],
                            "metrics": {
                                "cvssMetricV31": [{"cvssData": {"baseScore": 10.0, "baseSeverity": "CRITICAL"}}]
                            },
                            "weaknesses": [{"description": [{"value": "CWE-502"}]}],
                            "references": [{"url": "https://example.com"}],
                        }
                    }
                ],
            }
        ).encode()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: s
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            mock_urlopen.return_value.read.return_value = mock_response

            result = await rick_cve(CVEInput(query="CVE-2021-44228"))
            assert "CVE-2021-44228" in result
            assert "10.0" in result

    @pytest.mark.asyncio
    async def test_cve_keyword_mocked(self):
        mock_response = json.dumps(
            {
                "totalResults": 0,
                "vulnerabilities": [],
            }
        ).encode()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: s
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            mock_urlopen.return_value.read.return_value = mock_response

            result = await rick_cve(CVEInput(query="nonexistent-thing-xyz"))
            assert "No CVEs found" in result

    @pytest.mark.asyncio
    async def test_cve_http_error(self):
        import urllib.error

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(url="", code=403, msg="Forbidden", hdrs=None, fp=None)
            result = await rick_cve(CVEInput(query="CVE-2021-44228"))
            assert "Error" in result
            assert "403" in result

    @pytest.mark.asyncio
    async def test_cve_url_error(self):
        import urllib.error

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
            result = await rick_cve(CVEInput(query="CVE-2021-44228"))
            assert "Error" in result
            assert "NVD API" in result

    @pytest.mark.asyncio
    async def test_cve_timeout(self):
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError()
            result = await rick_cve(CVEInput(query="CVE-2021-44228"))
            assert "timed out" in result

    def test_cve_input_validation(self):
        with pytest.raises(ValidationError):
            CVEInput(query="")

    def test_cve_input_max_results_bounds(self):
        with pytest.raises(ValidationError):
            CVEInput(query="test", max_results=0)
        with pytest.raises(ValidationError):
            CVEInput(query="test", max_results=21)

    def test_cve_input_rejects_extra(self):
        with pytest.raises(ValidationError):
            CVEInput(query="test", extra="nope")

    @pytest.mark.asyncio
    async def test_cve_json_format(self):
        mock_response = json.dumps(
            {
                "totalResults": 1,
                "vulnerabilities": [
                    {
                        "cve": {
                            "id": "CVE-2021-44228",
                            "descriptions": [{"lang": "en", "value": "Test"}],
                            "metrics": {},
                            "weaknesses": [],
                            "references": [],
                        }
                    }
                ],
            }
        ).encode()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: s
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            mock_urlopen.return_value.read.return_value = mock_response

            result = await rick_cve(CVEInput(query="CVE-2021-44228", response_format=ResponseFormat.JSON))
            parsed = json.loads(result)
            assert isinstance(parsed, dict)
            assert "results" in parsed


# ═══════════════════════════════════════════════════════════════
#  TOOL 20: rick_tracker — Engagement Tracker
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def tracker_dir(tmp_path):
    """Use a temp directory for tracker tests."""
    eng_dir = tmp_path / ".rick_mcp" / "engagements"
    eng_dir.mkdir(parents=True)
    with patch("pathlib.Path.home", return_value=tmp_path):
        yield eng_dir


class TestRickTracker:
    @pytest.mark.asyncio
    async def test_create_engagement(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="create",
                    data=json.dumps({"client": "Test Corp", "type": "pentest", "id": "ENG-TEST-001"}),
                )
            )
        assert "ENG-TEST-001" in result
        assert "Test Corp" in result

    @pytest.mark.asyncio
    async def test_add_finding(self, tracker_dir):
        # Create engagement first
        eng = {
            "id": "ENG-TEST-002",
            "client": "Test Corp",
            "type": "pentest",
            "status": "active",
            "findings": [],
            "created_at": "2026-01-01T00:00:00",
        }
        (tracker_dir / "ENG-TEST-002.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="add_finding",
                    engagement_id="ENG-TEST-002",
                    data=json.dumps({"title": "SQLi in Login", "severity": "critical"}),
                )
            )
        assert "F-001" in result
        assert "SQLi in Login" in result

    @pytest.mark.asyncio
    async def test_update_finding(self, tracker_dir):
        eng = {
            "id": "ENG-TEST-003",
            "client": "Test Corp",
            "type": "pentest",
            "status": "active",
            "findings": [{"id": "F-001", "title": "Test", "severity": "high", "status": "open"}],
            "created_at": "2026-01-01T00:00:00",
        }
        (tracker_dir / "ENG-TEST-003.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="update_finding",
                    engagement_id="ENG-TEST-003",
                    data=json.dumps({"finding_id": "F-001", "status": "remediated"}),
                )
            )
        assert "F-001" in result
        assert "Updated" in result

    @pytest.mark.asyncio
    async def test_status_single(self, tracker_dir):
        eng = {
            "id": "ENG-TEST-004",
            "client": "Test Corp",
            "type": "pentest",
            "status": "active",
            "findings": [
                {"id": "F-001", "title": "Test", "severity": "critical", "status": "open"},
                {"id": "F-002", "title": "Test2", "severity": "high", "status": "open"},
            ],
            "created_at": "2026-01-01T00:00:00",
        }
        (tracker_dir / "ENG-TEST-004.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="status", engagement_id="ENG-TEST-004"))
        assert "ENG-TEST-004" in result
        assert "critical" in result

    @pytest.mark.asyncio
    async def test_status_all(self, tracker_dir):
        for i in range(3):
            eng = {
                "id": f"ENG-ALL-{i}",
                "client": "Test",
                "type": "pentest",
                "status": "active",
                "findings": [],
            }
            (tracker_dir / f"ENG-ALL-{i}.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="status"))
        assert "3" in result

    @pytest.mark.asyncio
    async def test_export(self, tracker_dir):
        eng = {"id": "ENG-EXPORT", "client": "Test", "findings": []}
        (tracker_dir / "ENG-EXPORT.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="export", engagement_id="ENG-EXPORT"))
        parsed = json.loads(result)
        assert parsed["id"] == "ENG-EXPORT"

    @pytest.mark.asyncio
    async def test_invalid_action(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="invalid"))
        assert "Error" in result
        assert "Unknown action" in result

    @pytest.mark.asyncio
    async def test_add_finding_missing_engagement(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="add_finding", engagement_id="NONEXISTENT"))
        assert "Error" in result
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_add_finding_no_id(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="add_finding"))
        assert "Error" in result
        assert "engagement_id required" in result

    @pytest.mark.asyncio
    async def test_update_finding_not_found(self, tracker_dir):
        eng = {
            "id": "ENG-UPD",
            "findings": [{"id": "F-001", "title": "Test", "severity": "high", "status": "open"}],
        }
        (tracker_dir / "ENG-UPD.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="update_finding",
                    engagement_id="ENG-UPD",
                    data=json.dumps({"finding_id": "F-999"}),
                )
            )
        assert "Error" in result
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_export_missing(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="export", engagement_id="NOPE"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_export_no_id(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="export"))
        assert "Error" in result
        assert "engagement_id required" in result

    @pytest.mark.asyncio
    async def test_create_invalid_json(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="create", data="not json"))
        assert "Error" in result
        assert "Invalid JSON" in result

    @pytest.mark.asyncio
    async def test_status_no_engagements(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="status"))
        assert "No engagements found" in result

    @pytest.mark.asyncio
    async def test_update_finding_missing_finding_id(self, tracker_dir):
        eng = {"id": "ENG-MIS", "findings": []}
        (tracker_dir / "ENG-MIS.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="update_finding",
                    engagement_id="ENG-MIS",
                    data=json.dumps({"status": "closed"}),
                )
            )
        assert "Error" in result
        assert "finding_id required" in result

    def test_tracker_input_rejects_extra(self):
        with pytest.raises(ValidationError):
            TrackerInput(action="status", extra="nope")


# ═══════════════════════════════════════════════════════════════
#  PYDANTIC MODEL VALIDATION — Extra field rejection across all
# ═══════════════════════════════════════════════════════════════


class TestInputValidation:
    """Every input model uses ConfigDict(extra='forbid') — verify they all reject unknown fields."""

    @pytest.mark.parametrize(
        "model_cls,kwargs",
        [
            (ReconInput, {"target_type": "web_app", "extra": "nope"}),
            (VulnInput, {"vuln_category": "xss", "extra": "nope"}),
            (ROEInput, {"engagement_type": "pentest", "extra": "nope"}),
            (ReportInput, {"section": "finding", "extra": "nope"}),
            (ToolRecInput, {"scenario": "web app test", "extra": "nope"}),
            (ProposalInput, {"engagement_type": "red_team", "extra": "nope"}),
            (OnboardInput, {"extra": "nope"}),
            (CompatInput, {"description": "a valid description for testing", "extra": "nope"}),
            (CoverInput, {"company_name": "X", "role_title": "Y", "extra": "nope"}),
            (AttackChainInput, {"scenario": "external_to_da", "extra": "nope"}),
            (PivotInput, {"position": "container", "extra": "nope"}),
            (HardenInput, {"technology": "linux_server", "extra": "nope"}),
            (CheatsheetInput, {"tool": "nmap", "extra": "nope"}),
            (DebriefInput, {"engagement_type": "pentest", "key_findings": "test", "extra": "nope"}),
            (MentorInput, {"topic": "mindset", "extra": "nope"}),
            (CVEInput, {"query": "test", "extra": "nope"}),
            (HealthInput, {"fix": True, "extra": "nope"}),
            (ModeInput, {"mode": "be_rick", "extra": "nope"}),
            (TrackerInput, {"action": "status", "extra": "nope"}),
        ],
    )
    def test_extra_fields_rejected(self, model_cls, kwargs):
        with pytest.raises(ValidationError):
            model_cls(**kwargs)


# ═══════════════════════════════════════════════════════════════
#  RESPONSE FORMAT — Both formats work for all tools
# ═══════════════════════════════════════════════════════════════


class TestResponseFormats:
    @pytest.mark.asyncio
    async def test_enum_values(self):
        assert ResponseFormat.MARKDOWN == "markdown"
        assert ResponseFormat.JSON == "json"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "tool_fn,params",
        [
            (rick_recon, ReconInput(target_type="web_app", response_format=ResponseFormat.JSON)),
            (rick_vuln_assess, VulnInput(vuln_category="xss", response_format=ResponseFormat.JSON)),
            (rick_roe, ROEInput(engagement_type="pentest", response_format=ResponseFormat.JSON)),
            (rick_report_template, ReportInput(section="finding", response_format=ResponseFormat.JSON)),
            (rick_tool_recommend, ToolRecInput(scenario="web app test", response_format=ResponseFormat.JSON)),
            (rick_engagement_proposal, ProposalInput(engagement_type="red_team", response_format=ResponseFormat.JSON)),
            (rick_client_onboarding, OnboardInput(response_format=ResponseFormat.JSON)),
            (rick_hardening, HardenInput(technology="linux_server", response_format=ResponseFormat.JSON)),
            (rick_cheatsheet, CheatsheetInput(tool="nmap", response_format=ResponseFormat.JSON)),
            (rick_mentorship, MentorInput(topic="mindset", response_format=ResponseFormat.JSON)),
        ],
    )
    async def test_json_output_is_valid(self, tool_fn, params):
        result = await tool_fn(params)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)


# ═══════════════════════════════════════════════════════════════
#  MCP SERVER — Registration integrity
# ═══════════════════════════════════════════════════════════════


class TestMCPServer:
    def test_server_name(self):
        assert mcp.name == "rick_mcp"
