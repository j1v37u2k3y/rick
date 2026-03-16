"""Meta tools — status and health check."""

from pathlib import Path

from __version__ import __version__
from rick_mcp.constants import (
    CALLSIGN,
    CERTIFICATIONS,
    LANGUAGES,
    MISSION_PHASES,
    PRIMARY_TOOLS,
    SPECIALIZATIONS,
    ResponseFormat,
)
from rick_mcp.formatting import _fmt, _read_md, _safe_tool, _sanitize
from rick_mcp.models import HealthInput, ModeInput


async def rick_status() -> str:
    """Rick MCP server status. Version, tool count, resource count, callsign, operational readiness."""
    return _fmt(
        {
            "server": "rick_mcp",
            "version": __version__,
            "callsign": CALLSIGN,
            "tools": 22,
            "resources": 22,
            "mission_phases": len(MISSION_PHASES),
            "certifications": CERTIFICATIONS,
            "specializations": len(SPECIALIZATIONS),
            "languages": len(LANGUAGES),
            "primary_tools": len(PRIMARY_TOOLS),
            "status": "OPERATIONAL — Standing by for mission parameters.",
            "rick_says": "I'm still building. Are you?",
            "semper_fidelis": True,
        },
        ResponseFormat.MARKDOWN,
        title=f"{CALLSIGN} Status",
    )


async def rick_health(params: HealthInput | None = None) -> str:
    """Health check with self-healing. Diagnose by default, repair with fix=True."""
    import json as _json

    # Lazy imports to avoid circular dependencies
    from rick_mcp.resources import (
        res_achievements,
        res_changelog,
        res_contributing,
        res_craftsmanship,
        res_entertainment,
        res_heritage,
        res_human,
        res_mantras,
        res_methodology,
        res_profile,
        res_resume_contact,
        res_resume_evidence,
        res_resume_overview,
        res_resume_portfolio,
        res_rick_and_jiveturkey,
        res_security,
        res_soul,
        res_stack,
        res_summary,
        res_the_book,
        res_values,
        res_wwm,
    )
    from rick_mcp.tools.career import rick_compatibility_check, rick_cover_letter, rick_mentorship
    from rick_mcp.tools.cve import rick_cve
    from rick_mcp.tools.defensive import rick_hardening
    from rick_mcp.tools.engagement import (
        rick_client_onboarding,
        rick_debrief,
        rick_engagement_proposal,
        rick_report_template,
        rick_roe,
        rick_tracker,
    )
    from rick_mcp.tools.offensive import (
        rick_attack_chain,
        rick_cheatsheet,
        rick_pivot_plan,
        rick_recon,
        rick_threat_model,
        rick_tool_recommend,
        rick_vuln_assess,
    )

    fix = params.fix if params else False
    fmt = params.response_format if params else ResponseFormat.MARKDOWN
    checks: dict[str, str] = {}
    repairs: list[str] = []

    # Check version
    checks["version"] = "PASS" if __version__ else "FAIL"

    # Check _fmt works
    try:
        result = _fmt({"test": "value"}, ResponseFormat.MARKDOWN, title="Health")
        checks["fmt"] = "PASS" if "test" in result.lower() or "value" in result.lower() else "FAIL"
    except Exception:
        checks["fmt"] = "FAIL"

    # Check _read_md can find files
    try:
        result = _read_md("README.md")
        checks["read_md"] = "PASS" if "not found" not in result.lower() else "FAIL"
    except Exception:
        checks["read_md"] = "FAIL"

    # Check all tool functions are callable
    tool_fns = [
        rick_recon,
        rick_vuln_assess,
        rick_roe,
        rick_report_template,
        rick_tool_recommend,
        rick_engagement_proposal,
        rick_client_onboarding,
        rick_compatibility_check,
        rick_cover_letter,
        rick_attack_chain,
        rick_pivot_plan,
        rick_hardening,
        rick_cheatsheet,
        rick_debrief,
        rick_mentorship,
        rick_threat_model,
        rick_status,
        rick_health,
        rick_cve,
        rick_tracker,
    ]
    callable_count = sum(1 for fn in tool_fns if callable(fn))
    checks["tools_callable"] = f"PASS ({callable_count}/{len(tool_fns)})"

    # Check all resource functions are callable
    resource_fns = [
        res_rick_and_jiveturkey,
        res_summary,
        res_values,
        res_heritage,
        res_craftsmanship,
        res_stack,
        res_methodology,
        res_mantras,
        res_human,
        res_entertainment,
        res_wwm,
        res_the_book,
        res_soul,
        res_profile,
        res_achievements,
        res_contributing,
        res_changelog,
        res_security,
        res_resume_overview,
        res_resume_evidence,
        res_resume_portfolio,
        res_resume_contact,
    ]
    res_callable = sum(1 for fn in resource_fns if callable(fn))
    checks["resources_callable"] = f"PASS ({res_callable}/{len(resource_fns)})"

    # Check sanitize works
    try:
        assert _sanitize(None) is None
        assert _sanitize("  test\x00  ") == "test"
        checks["sanitize"] = "PASS"
    except Exception:
        checks["sanitize"] = "FAIL"

    # Check data directory exists (for tracker)
    data_dir = Path.home() / ".rick_mcp" / "engagements"
    if data_dir.exists():
        checks["data_dir"] = "PASS"
    else:
        checks["data_dir"] = "FAIL — directory missing"
        if fix:
            data_dir.mkdir(parents=True, exist_ok=True)
            checks["data_dir"] = "REPAIRED — created directory"
            repairs.append(f"Created {data_dir}")

    # Check engagement JSON integrity
    if data_dir.exists():
        corrupt_files: list[str] = []
        for eng_file in data_dir.glob("*.json"):
            try:
                data = _json.loads(eng_file.read_text())
                if "id" not in data:
                    corrupt_files.append(f"{eng_file.name} (missing id)")
            except _json.JSONDecodeError:
                corrupt_files.append(f"{eng_file.name} (invalid JSON)")
                if fix:
                    backup = eng_file.with_suffix(".json.corrupt")
                    eng_file.rename(backup)
                    repairs.append(f"Quarantined {eng_file.name} → {backup.name}")

        if corrupt_files:
            checks["engagement_integrity"] = f"FAIL — {', '.join(corrupt_files)}"
            if fix and any("invalid JSON" in c for c in corrupt_files):
                checks["engagement_integrity"] = "REPAIRED — quarantined corrupt files"
        else:
            eng_count = len(list(data_dir.glob("*.json")))
            checks["engagement_integrity"] = f"PASS ({eng_count} engagements)"

    # Check markdown files accessible
    expected_md = ["README.md", "WORKING_WITH_ME.md", "CHANGELOG.md", "SECURITY.md"]
    missing_md: list[str] = []
    for md_file in expected_md:
        result = _read_md(md_file)
        if "not found" in result.lower():
            missing_md.append(md_file)
    if missing_md:
        checks["markdown_files"] = f"FAIL — missing: {', '.join(missing_md)}"
    else:
        checks["markdown_files"] = f"PASS ({len(expected_md)} files)"

    # Overall
    failed = [k for k, v in checks.items() if "FAIL" in v]
    repaired = [k for k, v in checks.items() if "REPAIRED" in v]

    if not failed and not repaired:
        checks["overall"] = "ALL PASS"
    elif failed and not fix:
        checks["overall"] = f"DEGRADED — {len(failed)} issue(s)"
    elif repaired and not failed:
        checks["overall"] = f"HEALED — {len(repaired)} repair(s)"
    else:
        checks["overall"] = f"PARTIAL — {len(repaired)} repaired, {len(failed)} remaining"

    if repairs:
        checks["repairs_performed"] = "; ".join(repairs)

    if fix and not repairs and not failed:
        checks["fix_note"] = "Nothing to fix. Rick is healthy."

    return _fmt(
        checks,
        fmt,
        title=f"{CALLSIGN} Health Check" + (" — HEALING" if fix else ""),
    )


async def rick_demo() -> str:
    """Guided tour of Rick MCP. Fires one tool from each category with curated examples."""
    from rick_mcp.models import (
        AttackChainInput,
        CheatsheetInput,
        HardenInput,
        MentorInput,
        ReconInput,
        ROEInput,
        ToolRecInput,
        VulnInput,
    )
    from rick_mcp.tools.career import rick_mentorship
    from rick_mcp.tools.defensive import rick_hardening
    from rick_mcp.tools.engagement import rick_roe
    from rick_mcp.tools.offensive import (
        rick_attack_chain,
        rick_cheatsheet,
        rick_recon,
        rick_tool_recommend,
        rick_vuln_assess,
    )

    sections: list[str] = []
    sections.append("# Rick MCP — The Full Tour")
    sections.append("")
    sections.append(
        "Rick is the father. jiveturkey is the son. The MCP is Rick. "
        "20 tools, 23 resources, built with Marine Corps precision. "
        "Here's one from each category."
    )
    sections.append("")

    demos = [
        (
            "RECON — Reconnaissance Playbook",
            "rick_recon(target_type='active_directory')",
            rick_recon(ReconInput(target_type="active_directory")),
        ),
        (
            "VULN ASSESS — Vulnerability Assessment",
            "rick_vuln_assess(vuln_category='injection')",
            rick_vuln_assess(VulnInput(vuln_category="injection")),
        ),
        (
            "ATTACK CHAIN — MITRE ATT&CK Kill Chain",
            "rick_attack_chain(scenario='external_to_da')",
            rick_attack_chain(AttackChainInput(scenario="external_to_da")),
        ),
        (
            "TOOL RECOMMEND — Scenario-Aware Recommendations",
            "rick_tool_recommend(scenario='internal network pentest Active Directory')",
            rick_tool_recommend(ToolRecInput(scenario="internal network pentest Active Directory")),
        ),
        (
            "CHEATSHEET — Field Manual",
            "rick_cheatsheet(tool='nmap')",
            rick_cheatsheet(CheatsheetInput(tool="nmap")),
        ),
        (
            "HARDENING — Defensive Blueprint",
            "rick_hardening(technology='active_directory', priority='critical')",
            rick_hardening(HardenInput(technology="active_directory", priority="critical")),
        ),
        (
            "ROE — Rules of Engagement",
            "rick_roe(engagement_type='red_team', client_name='Demo Corp', duration_days=15)",
            rick_roe(ROEInput(engagement_type="red_team", client_name="Demo Corp", duration_days=15)),
        ),
        (
            "MENTORSHIP — Learning Path",
            "rick_mentorship(topic='getting_started')",
            rick_mentorship(MentorInput(topic="getting_started")),
        ),
    ]

    for title, call, coro in demos:
        result = await coro
        sections.append("---")
        sections.append(f"## {title}")
        sections.append(f"**Call:** `{call}`")
        sections.append("")
        # Trim to first 40 lines to keep the tour digestible
        result_lines = result.strip().splitlines()
        if len(result_lines) > 40:
            sections.extend(result_lines[:40])
            sections.append(f"*... ({len(result_lines) - 40} more lines — run the full tool for complete output)*")
        else:
            sections.append(result)
        sections.append("")

    sections.append("---")
    sections.append("## What Else Rick Can Do")
    sections.append("")
    sections.append("**Not shown in this demo:**")
    sections.append("- `rick_cve` — Live NVD CVE lookup (requires network)")
    sections.append("- `rick_tracker` — Stateful engagement tracker (create, findings, export)")
    sections.append("- `rick_health` — Self-healing health check (fix=True to repair)")
    sections.append("- `rick_threat_model` — STRIDE threat modeling for 8 system types")
    sections.append("- `rick_pivot_plan` — Lateral movement playbook by position")
    sections.append("- `rick_report_template` — Pentest report section templates")
    sections.append("- `rick_engagement_proposal` — SOW/proposal generator")
    sections.append("- `rick_client_onboarding` — Client onboarding packet")
    sections.append("- `rick_compatibility_check` — Job posting fit analyzer")
    sections.append("- `rick_cover_letter` — Cover letter generator (3 tones)")
    sections.append("- `rick_debrief` — Post-engagement debrief template")
    sections.append("")
    sections.append("**23 identity resources** available via `profile://`, `doc://`, and `resume://` URIs.")
    sections.append("")
    sections.append("Run `rick_status` for the full count. Run `rick_health` to verify everything's operational.")
    sections.append("")
    sections.append("*I'm still building. Are you? — Semper Fidelis.*")

    return "\n".join(sections)


async def rick_mode(params: ModeInput) -> str:
    """Activate a Rick persona mode. Injects identity, values, and live content into the conversation."""
    from rick_mcp.prompts import AVAILABLE_MODES, MODE_BUILDERS

    mode = (_sanitize(params.mode) or "").lower().strip()

    if mode not in MODE_BUILDERS:
        return f"Error: Unknown mode '{mode}'. Available: {', '.join(AVAILABLE_MODES)}"

    content = MODE_BUILDERS[mode](context=params.context or "")
    return content


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_status",
        annotations={
            "title": "Server Status",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_status))
    mcp.tool(
        name="rick_health",
        annotations={
            "title": "Health Check",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_health))
    mcp.tool(
        name="rick_demo",
        annotations={
            "title": "Guided Tour",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_demo))
    mcp.tool(
        name="rick_mode",
        annotations={
            "title": "Activate Rick Mode",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_mode))
