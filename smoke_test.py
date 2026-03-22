"""Smoke test — fire every tool once, verify output."""

import asyncio
import json
import sys

from rick_mcp import (
    AttackChainInput,
    C2CompareInput,
    CheatsheetInput,
    CloudAttackInput,
    CompatInput,
    CoverInput,
    DebriefInput,
    DetectionRulesInput,
    HardenInput,
    IncidentResponseInput,
    LogAnalysisInput,
    MentorInput,
    ModeInput,
    OnboardInput,
    PayloadGuideInput,
    PivotInput,
    ProposalInput,
    ReconInput,
    ReportInput,
    ROEInput,
    ScopingInput,
    ThreatModelInput,
    ToolRecInput,
    TrackerInput,
    VulnInput,
    WirelessInput,
    rick_attack_chain,
    rick_c2_compare,
    rick_capabilities,
    rick_cheatsheet,
    rick_client_onboarding,
    rick_cloud_attack_path,
    rick_compatibility_check,
    rick_cover_letter,
    rick_debrief,
    rick_demo,
    rick_detection_rules,
    rick_engagement_proposal,
    rick_hardening,
    rick_health,
    rick_incident_response,
    rick_log_analysis,
    rick_mentorship,
    rick_mode,
    rick_payload_guide,
    rick_pivot_plan,
    rick_recon,
    rick_report_template,
    rick_roe,
    rick_scoping,
    rick_status,
    rick_threat_model,
    rick_tool_recommend,
    rick_tracker,
    rick_vuln_assess,
    rick_wireless,
)


async def smoke():
    tools = [
        ("rick_recon", rick_recon(ReconInput(target_type="web_app"))),
        ("rick_vuln_assess", rick_vuln_assess(VulnInput(vuln_category="injection"))),
        ("rick_roe", rick_roe(ROEInput(engagement_type="pentest"))),
        ("rick_report_template", rick_report_template(ReportInput(section="finding"))),
        ("rick_tool_recommend", rick_tool_recommend(ToolRecInput(scenario="web app pentest"))),
        ("rick_engagement_proposal", rick_engagement_proposal(ProposalInput(engagement_type="red_team"))),
        ("rick_client_onboarding", rick_client_onboarding(OnboardInput())),
        (
            "rick_compatibility_check",
            rick_compatibility_check(CompatInput(description="OSCP pentester web app cloud remote")),
        ),
        ("rick_cover_letter", rick_cover_letter(CoverInput(company_name="Test", role_title="Pentester"))),
        ("rick_attack_chain", rick_attack_chain(AttackChainInput(scenario="external_to_da"))),
        ("rick_pivot_plan", rick_pivot_plan(PivotInput(position="linux_webserver"))),
        ("rick_hardening", rick_hardening(HardenInput(technology="active_directory"))),
        ("rick_cheatsheet", rick_cheatsheet(CheatsheetInput(tool="nmap"))),
        ("rick_debrief", rick_debrief(DebriefInput(engagement_type="pentest"))),
        ("rick_mentorship", rick_mentorship(MentorInput(topic="mindset"))),
        ("rick_threat_model", rick_threat_model(ThreatModelInput(target="web_app"))),
        ("rick_status", rick_status()),
        ("rick_health", rick_health()),
        ("rick_demo", rick_demo()),
        ("rick_mode", rick_mode(ModeInput(mode="be_rick"))),
        (
            "rick_tracker",
            rick_tracker(
                TrackerInput(
                    action="create",
                    data=json.dumps({"client": "Smoke Test Corp", "type": "pentest"}),
                )
            ),
        ),
        # v2.0 tools
        ("rick_c2_compare", rick_c2_compare(C2CompareInput(scenario="stealth"))),
        ("rick_payload_guide", rick_payload_guide(PayloadGuideInput(payload_type="initial_access"))),
        ("rick_cloud_attack_path", rick_cloud_attack_path(CloudAttackInput(cloud_provider="aws"))),
        ("rick_wireless", rick_wireless(WirelessInput(wireless_type="wifi"))),
        ("rick_incident_response", rick_incident_response(IncidentResponseInput(incident_type="ransomware"))),
        ("rick_detection_rules", rick_detection_rules(DetectionRulesInput(attack_pattern="credential_dumping"))),
        ("rick_log_analysis", rick_log_analysis(LogAnalysisInput(log_source="windows_event"))),
        ("rick_scoping", rick_scoping(ScopingInput(engagement_type="red_team"))),
        ("rick_capabilities", rick_capabilities()),
    ]

    # Skip rick_cve in smoke test — requires network access to NVD API
    # ("rick_cve", rick_cve(CVEInput(query="CVE-2021-44228"))),

    passed = 0
    for name, coro in tools:
        result = await coro
        if result and len(result) > 50:
            print(f"  + {name}")
            passed += 1
        else:
            print(f"  X {name} — FAILED (output: {result[:100] if result else 'None'})")

    skipped = ["rick_cve (requires network — NVD API)"]

    print()
    print(f"{passed}/{len(tools)} tools fired successfully.")
    print(f"{len(skipped)} skipped: {', '.join(skipped)}")
    from rick_mcp.server import tool_count

    print(f"{passed + len(skipped)}/{tool_count()} total tools accounted for.")

    if passed < len(tools):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(smoke())
