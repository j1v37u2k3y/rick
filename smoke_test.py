"""Smoke test — fire every tool once, verify output.

Fires 46 of 48 registered tools against a throwaway HOME so nothing touches the
operator's real ~/.rick_mcp/ (kill-chain state, engagements, vault, caches) and the
run uses generic identity defaults — reproducible, offline, no PII. The 2 network
tools (rick_cve, rick_recon_handle) are documented skips; their real-network paths
are covered by mocked unit tests. A pass requires output > 50 chars AND the absence
of the _safe_tool error marker ("encountered an issue:"), so a tool that errors
internally counts as a failure rather than a false green.
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile

# State isolation MUST precede the rick_mcp import: jarvis_state binds
# `_STATE_DIR = Path.home() / ".rick_mcp" / "dick"` at import time, so HOME has to
# point at the throwaway dir before any rick_mcp module is loaded.
_SMOKE_HOME = tempfile.mkdtemp(prefix="rick-smoke-")
os.environ["HOME"] = _SMOKE_HOME
os.environ["USERPROFILE"] = _SMOKE_HOME  # Windows parity

from rick_mcp import (  # noqa: E402
    AppraisalInput,
    AttackChainInput,
    C2CompareInput,
    CheatsheetInput,
    ChecklistInput,
    CloudAttackInput,
    CodeReviewInput,
    CompareInput,
    CompatInput,
    CoverInput,
    DebriefInput,
    DetectionRulesInput,
    ExportInput,
    FullAutoInput,
    HardenInput,
    IncidentResponseInput,
    KillChainInput,
    LogAnalysisInput,
    MentorInput,
    ModeInput,
    NextMoveInput,
    NotesInput,
    OnboardInput,
    PayloadGuideInput,
    PivotInput,
    ProposalInput,
    ReconInput,
    ReportInput,
    ROEInput,
    RollbackInput,
    ScopeCheckInput,
    ScopingInput,
    SitrepInput,
    TagInput,
    ThreatModelInput,
    TimelineInput,
    ToolRecInput,
    TrackerInput,
    VulnInput,
    WirelessInput,
    rick_attack_chain,
    rick_c2_compare,
    rick_capabilities,
    rick_cheatsheet,
    rick_checklist,
    rick_client_onboarding,
    rick_cloud_attack_path,
    rick_code_review,
    rick_cognitive_appraisal,
    rick_compare,
    rick_compatibility_check,
    rick_cover_letter,
    rick_debrief,
    rick_demo,
    rick_detection_rules,
    rick_engagement_proposal,
    rick_export,
    rick_full_auto,
    rick_hardening,
    rick_health,
    rick_incident_response,
    rick_kill_chain,
    rick_log_analysis,
    rick_mantra,
    rick_mentorship,
    rick_mode,
    rick_next_move,
    rick_notes,
    rick_payload_guide,
    rick_pivot_plan,
    rick_recon,
    rick_report_template,
    rick_roe,
    rick_rollback,
    rick_scope_check,
    rick_scoping,
    rick_sitrep,
    rick_status,
    rick_tag,
    rick_threat_model,
    rick_timeline,
    rick_tool_recommend,
    rick_tracker,
    rick_vuln_assess,
    rick_wireless,
)
from rick_mcp.models.inputs import WriteupInput  # noqa: E402
from rick_mcp.tools.jarvis_state import KILL_CHAIN_PHASES, _save_state  # noqa: E402
from rick_mcp.tools.writeups import rick_writeups  # noqa: E402

# Network tools — fired by mocked unit tests, not here (offline + deterministic smoke).
SKIPPED = {
    "rick_cve": "network — NVD API",
    "rick_recon_handle": "network — GitHub / CTFTime / HTB APIs",
}

# The _safe_tool decorator swallows exceptions into this string; treat it as a failure
# so stateful tools hitting missing state don't count as a (>50-char) false pass.
_ERROR_MARKER = "encountered an issue:"

_FIXED_TS = "2026-01-01T00:00:00+00:00"
_ENG = "smoke-eng"
_ENG_B = "smoke-eng-b"


def _fresh_kill_chain() -> list[dict]:
    """A deep-enough copy of the phase template (new findings lists, no global mutation)."""
    return [{**phase, "findings": list(phase["findings"])} for phase in KILL_CHAIN_PHASES]


def _seed() -> None:
    """Seed two engagements in the throwaway state dir so the stateful jarvis tools
    return real output. Shape mirrors tests/test_jarvis_extended.py::_create_engagement.

    smoke-eng carries: an active phase 1 with a finding (so rick_tag has index 0), a
    snapshot (so rick_rollback has a target), a scope (so rick_scope_check is real),
    and a note. smoke-eng-b is a minimal second engagement for rick_compare.
    """
    kc = _fresh_kill_chain()
    kc[0]["status"] = "active"
    kc[0]["findings"] = [{"description": "open port 80/tcp", "timestamp": _FIXED_TS}]
    _save_state(
        _ENG,
        {
            "id": _ENG,
            "target": "smoke.local",
            "target_type": "web_app",
            "created": _FIXED_TS,
            "kill_chain": kc,
            "mission_log": [{"timestamp": _FIXED_TS, "entry": "engagement seeded for smoke"}],
            "tool_history": [],
            "notes": [{"content": "seed note", "timestamp": _FIXED_TS}],
            "scope": ["smoke.local"],
            "snapshots": [
                {
                    "timestamp": _FIXED_TS,
                    "state": {
                        "id": _ENG,
                        "target": "smoke.local",
                        "kill_chain": _fresh_kill_chain(),
                    },
                }
            ],
        },
    )
    _save_state(
        _ENG_B,
        {
            "id": _ENG_B,
            "target": "smoke-b.local",
            "target_type": "network",
            "created": _FIXED_TS,
            "kill_chain": _fresh_kill_chain(),
            "mission_log": [],
            "tool_history": [],
            "notes": [],
        },
    )


async def smoke() -> None:
    _seed()

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
        ("rick_mantra", rick_mantra()),
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
        ("rick_code_review", rick_code_review(CodeReviewInput(focus="full"))),
        ("rick_wireless", rick_wireless(WirelessInput(wireless_type="wifi"))),
        ("rick_incident_response", rick_incident_response(IncidentResponseInput(incident_type="ransomware"))),
        ("rick_detection_rules", rick_detection_rules(DetectionRulesInput(attack_pattern="credential_dumping"))),
        ("rick_log_analysis", rick_log_analysis(LogAnalysisInput(log_source="windows_event"))),
        ("rick_scoping", rick_scoping(ScopingInput(engagement_type="red_team"))),
        ("rick_capabilities", rick_capabilities()),
        # Stateless additions
        (
            "rick_cognitive_appraisal",
            rick_cognitive_appraisal(AppraisalInput(subject="defender", situation="phishing email received")),
        ),
        ("rick_writeups", rick_writeups(WriteupInput(action="list"))),
        # Stateful jarvis family — fired against the seeded engagements. Reads first, then
        # mutators; rollback last so it doesn't disturb earlier reads of smoke-eng.
        ("rick_sitrep", rick_sitrep(SitrepInput(engagement_id=_ENG))),
        ("rick_next_move", rick_next_move(NextMoveInput(engagement_id=_ENG))),
        ("rick_timeline", rick_timeline(TimelineInput(engagement_id=_ENG))),
        ("rick_scope_check", rick_scope_check(ScopeCheckInput(engagement_id=_ENG, target="smoke.local"))),
        ("rick_export", rick_export(ExportInput(engagement_id=_ENG))),
        ("rick_tag", rick_tag(TagInput(engagement_id=_ENG, phase=1, finding_index=0, severity="high"))),
        ("rick_compare", rick_compare(CompareInput(engagement_id_a=_ENG, engagement_id_b=_ENG_B))),
        ("rick_notes", rick_notes(NotesInput(engagement_id=_ENG, action="add", content="smoke note"))),
        ("rick_checklist", rick_checklist(ChecklistInput(engagement_id=_ENG, action="generate"))),
        (
            "rick_kill_chain",
            rick_kill_chain(KillChainInput(action="add_finding", engagement_id=_ENG, phase=1, finding="smoke find")),
        ),
        ("rick_full_auto", rick_full_auto(FullAutoInput(target="smoke.local"))),
        ("rick_rollback", rick_rollback(RollbackInput(engagement_id=_ENG, confirm=True))),
    ]

    passed = 0
    failures: list[tuple[str, str]] = []
    for name, coro in tools:
        try:
            result = await coro
        except Exception as exc:  # noqa: BLE001 — smoke reports every tool, never bails on one
            failures.append((name, f"raised {type(exc).__name__}: {exc}"))
            print(f"  X {name} — RAISED {type(exc).__name__}: {exc}")
            continue
        if result and len(result) > 50 and _ERROR_MARKER not in result:
            print(f"  + {name}")
            passed += 1
        else:
            snippet = result[:100] if result else "None"
            failures.append((name, f"bad output: {snippet}"))
            print(f"  X {name} — FAILED ({snippet})")

    print()
    print(f"{passed}/{len(tools)} tools fired successfully.")
    if failures:
        print("Failures:")
        for name, reason in failures:
            print(f"  - {name}: {reason}")
    print(f"{len(SKIPPED)} skipped (network): " + ", ".join(f"{k} ({v})" for k, v in SKIPPED.items()))

    from rick_mcp.server import tool_count

    print(f"{len(tools) + len(SKIPPED)}/{tool_count()} total tools accounted for.")

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(smoke())
    finally:
        shutil.rmtree(_SMOKE_HOME, ignore_errors=True)
