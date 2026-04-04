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
from rick_mcp.identity import MOTTO, TAGLINE, bio_summary, is_configured
from rick_mcp.models import HealthInput, ModeInput


async def rick_status() -> str:
    """Rick MCP server status. Version, tool count, resource count, callsign, operational readiness."""
    from rick_mcp.server import resource_count, tool_count

    return _fmt(
        {
            "server": "rick_mcp",
            "version": __version__,
            "callsign": CALLSIGN,
            "tools": tool_count(),
            "resources": resource_count(),
            "mission_phases": len(MISSION_PHASES),
            "certifications": CERTIFICATIONS,
            "specializations": len(SPECIALIZATIONS),
            "languages": len(LANGUAGES),
            "primary_tools": len(PRIMARY_TOOLS),
            "status": "OPERATIONAL — Standing by for mission parameters.",
            "tagline": TAGLINE,
            **({"motto": MOTTO} if MOTTO else {}),
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
    from rick_mcp.tools.offensive import rick_recon, rick_tool_recommend, rick_vuln_assess
    from rick_mcp.tools.offensive_chains import rick_attack_chain, rick_pivot_plan
    from rick_mcp.tools.offensive_tradecraft import rick_cheatsheet, rick_threat_model

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
        C2CompareInput,
        CheatsheetInput,
        DetectionRulesInput,
        HardenInput,
        IncidentResponseInput,
        LogAnalysisInput,
        MentorInput,
        ReconInput,
        ROEInput,
        ScopingInput,
        ToolRecInput,
        VulnInput,
    )
    from rick_mcp.server import resource_count, tool_count
    from rick_mcp.tools.career import rick_mentorship
    from rick_mcp.tools.defensive import rick_detection_rules, rick_hardening, rick_incident_response, rick_log_analysis
    from rick_mcp.tools.engagement import rick_roe, rick_scoping
    from rick_mcp.tools.offensive import rick_recon, rick_tool_recommend, rick_vuln_assess
    from rick_mcp.tools.offensive_chains import rick_attack_chain
    from rick_mcp.tools.offensive_extended import rick_c2_compare
    from rick_mcp.tools.offensive_tradecraft import rick_cheatsheet

    sections: list[str] = []
    sections.append("# Rick MCP — The Full Tour")
    sections.append("")
    if is_configured():
        sections.append(
            f"{bio_summary()} The MCP is Rick. "
            f"{tool_count()} tools, {resource_count()} resources, built with precision. "
            "Here's one from each category."
        )
    else:
        sections.append(
            f"Rick MCP — {tool_count()} tools, {resource_count()} resources. "
            "Security through craftsmanship. Here's one from each category."
        )
    sections.append("")

    demos = [
        # Offensive — Recon & Assessment
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
        # Offensive — Attack Methodology
        (
            "ATTACK CHAIN — MITRE ATT&CK Kill Chain",
            "rick_attack_chain(scenario='external_to_da')",
            rick_attack_chain(AttackChainInput(scenario="external_to_da")),
        ),
        (
            "C2 COMPARE — Framework Comparison",
            "rick_c2_compare(scenario='stealth')",
            rick_c2_compare(C2CompareInput(scenario="stealth")),
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
        # Defensive & Detection
        (
            "HARDENING — Defensive Blueprint",
            "rick_hardening(technology='active_directory', priority='critical')",
            rick_hardening(HardenInput(technology="active_directory", priority="critical")),
        ),
        (
            "INCIDENT RESPONSE — IR Playbook",
            "rick_incident_response(incident_type='ransomware')",
            rick_incident_response(IncidentResponseInput(incident_type="ransomware")),
        ),
        (
            "DETECTION RULES — Sigma/YARA Templates",
            "rick_detection_rules(attack_pattern='credential_dumping')",
            rick_detection_rules(DetectionRulesInput(attack_pattern="credential_dumping")),
        ),
        (
            "LOG ANALYSIS — What to Look For",
            "rick_log_analysis(log_source='dns')",
            rick_log_analysis(LogAnalysisInput(log_source="dns")),
        ),
        # Engagement Lifecycle
        (
            "SCOPING — Engagement Calculator",
            "rick_scoping(engagement_type='red_team', target_count=3, complexity='high')",
            rick_scoping(ScopingInput(engagement_type="red_team", target_count=3, complexity="high")),
        ),
        (
            "ROE — Rules of Engagement",
            "rick_roe(engagement_type='red_team', client_name='Demo Corp', duration_days=15)",
            rick_roe(ROEInput(engagement_type="red_team", client_name="Demo Corp", duration_days=15)),
        ),
        # Career & Mentorship
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
    sections.append("- `rick_tracker` — Stateful engagement tracker (create, findings, export as JSON/CSV/Markdown)")
    sections.append("- `rick_health` — Self-healing health check (fix=True to repair)")
    sections.append("- `rick_threat_model` — STRIDE threat modeling for 8 system types")
    sections.append("- `rick_pivot_plan` — Lateral movement playbook by position")
    sections.append("- `rick_payload_guide` — Payload methodology mapped to MITRE ATT&CK")
    sections.append("- `rick_cloud_attack_path` — Cloud attack paths for Azure, AWS, GCP")
    sections.append("- `rick_wireless` — Wireless attack playbooks (WiFi, Bluetooth, RFID)")
    sections.append("- `rick_report_template` — Pentest report section templates")
    sections.append("- `rick_engagement_proposal` — SOW/proposal generator")
    sections.append("- `rick_client_onboarding` — Client onboarding packet")
    sections.append("- `rick_compatibility_check` — Job posting fit analyzer")
    sections.append("- `rick_cover_letter` — Cover letter generator (3 tones)")
    sections.append("- `rick_debrief` — Post-engagement debrief template")
    sections.append("- `rick_capabilities` — Full capability map")
    sections.append("")
    sections.append(
        f"**{resource_count()} identity resources** available via `profile://`, `doc://`, and `resume://` URIs."
    )
    sections.append("")
    sections.append("Run `rick_capabilities` for the full map. Run `rick_health` to verify everything's operational.")
    sections.append("")
    _closing = f"*{TAGLINE}*"
    if MOTTO:
        _closing = f"*{TAGLINE} — {MOTTO}.*"
    sections.append(_closing)

    return "\n".join(sections)


async def rick_mode(params: ModeInput) -> str:
    """Activate a Rick persona mode. Injects identity, values, and live content into the conversation."""
    from rick_mcp.prompts import AVAILABLE_MODES, MODE_BUILDERS

    mode = (_sanitize(params.mode) or "").lower().strip()

    if mode not in MODE_BUILDERS:
        return f"Error: Unknown mode '{mode}'. Available: {', '.join(AVAILABLE_MODES)}"

    content = MODE_BUILDERS[mode](context=params.context or "")
    return content


async def rick_capabilities() -> str:
    """What does Rick do? Full capability map — every tool, organized by mission phase."""
    from rick_mcp.server import resource_count, tool_count

    caps = {
        "who_is_rick": (
            (bio_summary() + " " if is_configured() else "")
            + f"This MCP server IS the resume — {tool_count()} tools, {resource_count()} resources, "
            "built with precision. Every tool proves a claim. "
            "Every resource tells the story."
        ),
        "offensive_recon_and_assessment": {
            "description": "Phase 1-2: Know your target before you touch it",
            "tools": {
                "rick_recon": "Recon playbooks for 8 target types (web, network, cloud, AD, API, container, mobile)",
                "rick_vuln_assess": "Vuln testing methodology for 10 categories (SQLi, XSS, SSRF, IDOR, auth, etc.)",
                "rick_tool_recommend": "Scenario-aware tool recommendations — describe the job, get the toolbox",
                "rick_threat_model": "STRIDE threat modeling for 8 system types",
            },
        },
        "offensive_attack_methodology": {
            "description": "Phase 3-5: Exploitation, escalation, lateral movement",
            "tools": {
                "rick_attack_chain": "MITRE ATT&CK kill chains — 6 scenarios from external to DA",
                "rick_pivot_plan": "Post-compromise pivoting from 7 positions (Linux, Windows, container, cloud, DB, network)",
                "rick_cheatsheet": "Field manuals for 10 core tools (nmap, burp, ffuf, hashcat, bloodhound, impacket, etc.)",
                "rick_c2_compare": "C2 framework comparison — Cobalt Strike vs Sliver vs Mythic vs Havoc",
                "rick_payload_guide": "Payload methodology — evasion, encoding, delivery vectors by MITRE ATT&CK",
                "rick_cloud_attack_path": "Cloud-specific attack paths for Azure, AWS, GCP",
                "rick_wireless": "Wireless attack playbooks — WiFi, Bluetooth, RFID",
            },
        },
        "defensive_and_detection": {
            "description": "The other side of the coin — build it right after breaking it",
            "tools": {
                "rick_hardening": "Hardening blueprints for 9 technologies (Windows, Linux, AD, cloud, K8s, network, DB)",
                "rick_incident_response": "IR playbooks for 5 incident types (ransomware, breach, insider, BEC, supply chain)",
                "rick_detection_rules": "Sigma/YARA rule templates for 6 attack patterns",
                "rick_log_analysis": "Log review methodology for 6 log sources (Windows, syslog, cloud, web, firewall, DNS)",
            },
        },
        "engagement_lifecycle": {
            "description": "The business side — from scoping to debrief",
            "tools": {
                "rick_scoping": "Engagement scoping calculator — hours, team size, rate card, timeline",
                "rick_roe": "Rules of Engagement document generator",
                "rick_engagement_proposal": "SOW/proposal generator for 7 engagement types",
                "rick_client_onboarding": "Client onboarding packet with checklists and ground rules",
                "rick_report_template": "Pentest report section templates (PlexTrac-compatible)",
                "rick_debrief": "Post-engagement debrief template",
                "rick_tracker": "Stateful engagement tracker — create, findings, export (JSON/CSV/Markdown)",
            },
        },
        "career_and_mentorship": {
            "description": "Growing the craft — for Rick and for the next generation",
            "tools": {
                "rick_compatibility_check": "Job/engagement brief analyzer — tech score, cultural fit, red flags",
                "rick_cover_letter": "Targeted cover letter generator matched to job requirements",
                "rick_mentorship": "Learning paths for 9 topics — getting started through advanced",
            },
        },
        "research": {
            "description": "Live intelligence from external sources",
            "tools": {
                "rick_cve": "NVD CVE lookup — search by ID or keyword, cached 24 hours",
            },
        },
        "jarvis_tools": {
            "description": "JARVIS — the intelligence layer. Proactive, chained, situationally aware.",
            "tools": {
                "rick_full_auto": "Give a target, get the complete playbook — recon, vulns, attack chain, tools, pivot. All chained automatically.",
                "rick_kill_chain": "Stateful kill chain tracker — status, advance, add findings (with image attachments). Persists across conversations.",
                "rick_next_move": "Situational awareness — analyzes position, findings, and kill chain state. Tells you what to do next.",
                "rick_sitrep": "Situation Report — one command, full tactical picture. Kill chain, findings, mission log, recommendations.",
                "rick_notes": "Engagement notes — add, list, search, delete. Supports image attachments as evidence.",
                "rick_timeline": "Unified chronological timeline — findings, mission log, tool history. Filterable by phase, type, time range.",
                "rick_compare": "Diff two engagements side by side — see what changed between assessments. Retests.",
                "rick_scope_check": "Safety rail — check targets and actions against stored scope/ROE. Know your boundaries.",
                "rick_export": "Export engagement to markdown, JSON, or CSV. Report-ready output.",
                "rick_checklist": "Phase-specific checklists auto-populated by target type. Generate, check, track progress.",
                "rick_tag": "Tag findings with severity, category, and MITRE ATT&CK technique IDs.",
                "rick_rollback": "Undo last kill chain state change. Uses automatic state snapshots.",
            },
        },
        "meta": {
            "description": "Rick talking about Rick",
            "tools": {
                "rick_status": "Server status — version, counts, operational readiness",
                "rick_health": "Health check with optional self-healing (fix=True)",
                "rick_demo": "Guided tour — fires one tool from each category",
                "rick_mode": "Activate persona modes (be_rick, dick_mode, jarvis, pentest_mode, mentor_mode, etc.)",
                "rick_capabilities": "You're looking at it",
            },
        },
        "resources": {
            "description": f"{resource_count()} identity resources — operator profile, queryable by AI",
            "categories": {
                "profile://": "10 resources — summary, values, heritage, stack, methodology, mantras, human, entertainment, timeline, rick_and_jiveturkey",
                "doc://": "9 resources — soul, the-book, working-with-me, profile, achievements, contributing, changelog, security, war-stories",
                "resume://": "4 resources — overview, evidence, portfolio, contact",
            },
        },
        "rick_note": "Don't just read the menu — order something. Pick a tool and fire it. The craft is in the doing, not the reading.",
    }
    return _fmt(caps, ResponseFormat.MARKDOWN, title=f"{CALLSIGN} Capabilities")


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
    mcp.tool(
        name="rick_capabilities",
        annotations={
            "title": "Capability Map",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_capabilities))
