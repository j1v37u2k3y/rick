"""JARVIS — the intelligence layer. Proactive, chained, situationally aware.

The nervous system connecting Rick (foundation), Dick (operator), and all tools.
Automatic tool chaining, stateful kill chain tracking, situational awareness,
and mission logging. Dick is the persona. JARVIS is the system.
"""

import json
from datetime import datetime, timezone
from typing import Any

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import (
    AttackChainInput,
    FullAutoInput,
    KillChainInput,
    NextMoveInput,
    PivotInput,
    ReconInput,
    SitrepInput,
    ToolRecInput,
    VulnInput,
)
from rick_mcp.tools import jarvis_state as _js
from rick_mcp.tools.jarvis_state import (
    KILL_CHAIN_PHASES,
    _add_mission_log,
    _load_state,
    _phase_advice,
    _save_state,
    _validate_image_path,
)

# ═══════════════════════════════════════════════════════════════
# Tool: rick_full_auto — Chain everything. Automatically.
# ═══════════════════════════════════════════════════════════════


async def rick_full_auto(params: FullAutoInput) -> str:
    """Dick's full auto mode. Give a target, get the complete playbook — recon, vulns, attack chain, tools, pivot plan. All chained. No waiting."""
    from rick_mcp.tools.offensive import rick_recon, rick_tool_recommend, rick_vuln_assess
    from rick_mcp.tools.offensive_chains import rick_attack_chain, rick_pivot_plan

    target = _sanitize(params.target) or params.target
    target_type = (_sanitize(params.target_type) or "web_app").lower().strip()

    sections: list[str] = []
    sections.append(f"# FULL AUTO — {target}")
    sections.append("*Dick opened all the doors. Here's what's behind them.*")
    sections.append(f"**Target:** {target}")
    sections.append(f"**Type:** {target_type}")
    sections.append(f"**Timestamp:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    sections.append("")

    # Phase 1: Recon
    sections.append("---")
    sections.append("## Phase 1: RECONNAISSANCE")
    sections.append("*Know your target better than they know themselves.*")
    sections.append("")
    recon_result = await rick_recon(ReconInput(target_type=target_type, scope_notes=f"Target: {target}"))
    sections.append(recon_result)
    sections.append("")

    # Phase 2: Vulnerability Assessment
    sections.append("---")
    sections.append("## Phase 2: VULNERABILITY ASSESSMENT")
    sections.append("*Scanners find what's known. Dick finds what's new.*")
    sections.append("")
    # Map target types to most relevant vuln categories
    vuln_map = {
        "web_app": "injection",
        "api": "auth",
        "network": "misconfig",
        "active_directory": "privesc",
        "cloud_azure": "misconfig",
        "cloud_aws": "misconfig",
        "container": "misconfig",
        "mobile": "auth",
    }
    vuln_cat = vuln_map.get(target_type, "injection")
    vuln_result = await rick_vuln_assess(
        VulnInput(vuln_category=vuln_cat, context=f"Target: {target}, Type: {target_type}")
    )
    sections.append(vuln_result)
    sections.append("")

    # Phase 3: Attack Chain
    sections.append("---")
    sections.append("## Phase 3: ATTACK CHAIN")
    sections.append("*Think in chains, not isolated vulnerabilities.*")
    sections.append("")
    chain_map = {
        "web_app": "web_to_internal",
        "api": "web_to_internal",
        "network": "external_to_da",
        "active_directory": "external_to_da",
        "cloud_azure": "cloud_to_onprem",
        "cloud_aws": "cloud_to_onprem",
        "container": "web_to_internal",
        "mobile": "web_to_internal",
    }
    chain_scenario = chain_map.get(target_type, "external_to_da")
    chain_result = await rick_attack_chain(
        AttackChainInput(scenario=chain_scenario, target_environment=f"{target} ({target_type})")
    )
    sections.append(chain_result)
    sections.append("")

    # Phase 4: Tool Recommendations
    sections.append("---")
    sections.append("## Phase 4: ARSENAL — What to Bring")
    sections.append("*The right tool for the right door.*")
    sections.append("")
    tool_result = await rick_tool_recommend(ToolRecInput(scenario=f"{target_type} assessment against {target}"))
    sections.append(tool_result)
    sections.append("")

    # Phase 5: Pivot Plan
    sections.append("---")
    sections.append("## Phase 5: POST-COMPROMISE — Where to Go Next")
    sections.append("*Initial access is step one of twenty.*")
    sections.append("")
    pivot_map = {
        "web_app": "linux_webserver",
        "api": "linux_webserver",
        "network": "network_device",
        "active_directory": "windows_server",
        "cloud_azure": "cloud_instance",
        "cloud_aws": "cloud_instance",
        "container": "container",
        "mobile": "linux_webserver",
    }
    pivot_pos = pivot_map.get(target_type, "linux_webserver")
    pivot_result = await rick_pivot_plan(
        PivotInput(position=pivot_pos, target_network=f"Internal network behind {target}")
    )
    sections.append(pivot_result)
    sections.append("")

    # Initialize kill chain state if engagement_id provided
    if params.engagement_id:
        eng_id = _sanitize(params.engagement_id) or params.engagement_id
        kill_chain = [dict(p) for p in KILL_CHAIN_PHASES]
        kill_chain[0]["status"] = "active"
        now = datetime.now(timezone.utc).isoformat()
        state: dict[str, Any] = {
            "id": eng_id,
            "target": target,
            "target_type": target_type,
            "created": now,
            "objective": "",
            "notes": [],
            "kill_chain": kill_chain,
            "mission_log": [{"timestamp": now, "entry": f"Full auto initiated for {target} ({target_type})"}],
            "tool_history": [{"tool": "rick_full_auto", "timestamp": now, "summary": f"Full auto for {target}"}],
        }
        _save_state(eng_id, state)
        sections.append("---")
        sections.append(f"## Engagement Tracking: `{eng_id}`")
        sections.append("Kill chain state initialized. Phase 1 (Reconnaissance) is ACTIVE.")
        sections.append(f"Use `rick_kill_chain(action='status', engagement_id='{eng_id}')` to check progress.")
        sections.append(f"Use `rick_next_move(engagement_id='{eng_id}')` for Dick's recommendation.")
        sections.append("")

    sections.append("---")
    sections.append(f"*Full auto complete. {CALLSIGN} has the playbook. Now go open some doors.*")

    return "\n".join(sections)


# ═══════════════════════════════════════════════════════════════
# Tool: rick_kill_chain — Stateful kill chain tracker
# ═══════════════════════════════════════════════════════════════


async def rick_kill_chain(params: KillChainInput) -> str:
    """Track your position in the kill chain. Dick knows where you are, what you've found, and what's next. Stateful across conversations."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    action = (_sanitize(params.action) or "status").lower().strip()
    fmt = params.response_format

    if action == "list":
        # List all active engagements
        _js._STATE_DIR.mkdir(parents=True, exist_ok=True)
        engagements = []
        for f in sorted(_js._STATE_DIR.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                active_phase = "Unknown"
                for p in data.get("kill_chain", []):
                    if p.get("status") == "active":
                        active_phase = f"Phase {p['phase']}: {p['name']}"
                        break
                engagements.append(
                    {
                        "id": data.get("id", f.stem),
                        "target": data.get("target", "Unknown"),
                        "active_phase": active_phase,
                        "created": data.get("created", "Unknown"),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue

        if not engagements:
            return "No active engagements. Use `rick_full_auto` to start one, or `rick_kill_chain(action='status', engagement_id='...')` to create manually."

        return _fmt(
            {"engagements": engagements, "count": len(engagements)},
            fmt,
            title=f"{CALLSIGN} Active Engagements",
        )

    state = _load_state(eng_id)

    if action == "status":
        if not state:
            # Create new engagement state
            state = {
                "id": eng_id,
                "target": "Not yet specified",
                "created": datetime.now(timezone.utc).isoformat(),
                "kill_chain": [dict(p) for p in KILL_CHAIN_PHASES],
            }
            _save_state(eng_id, state)
            return _fmt(
                {
                    "engagement": eng_id,
                    "status": "NEW — Kill chain initialized",
                    "kill_chain": state["kill_chain"],
                    "next": "Use action='advance' with phase=1 to begin recon.",
                },
                fmt,
                title=f"{CALLSIGN} Kill Chain — {eng_id}",
            )

        # Calculate progress
        completed = sum(1 for p in state["kill_chain"] if p["status"] == "completed")
        active = [p for p in state["kill_chain"] if p["status"] == "active"]
        total_findings = sum(len(p.get("findings", [])) for p in state["kill_chain"])

        result = {
            "engagement": eng_id,
            "target": state.get("target", "Unknown"),
            "progress": f"{completed}/7 phases completed",
            "total_findings": total_findings,
            "kill_chain": state["kill_chain"],
        }
        if active:
            result["current_phase"] = f"Phase {active[0]['phase']}: {active[0]['name']}"
        elif completed == 7:
            result["status"] = "COMPLETE — All phases executed. Time for the report."
        else:
            next_pending = next((p for p in state["kill_chain"] if p["status"] == "pending"), None)
            if next_pending:
                result["next_phase"] = f"Phase {next_pending['phase']}: {next_pending['name']}"

        return _fmt(result, fmt, title=f"{CALLSIGN} Kill Chain — {eng_id}")

    if action == "advance":
        if not state:
            return f"Error: No engagement '{eng_id}' found. Use action='status' to create one first."

        phase_num = params.phase
        if not phase_num:
            # Auto-advance: complete current active, activate next pending
            for p in state["kill_chain"]:
                if p["status"] == "active":
                    p["status"] = "completed"
                    p["completed_at"] = datetime.now(timezone.utc).isoformat()
                    phase_num = p["phase"]
                    break

            if phase_num:
                # Activate next
                next_phase = next((p for p in state["kill_chain"] if p["status"] == "pending"), None)
                if next_phase:
                    next_phase["status"] = "active"
                    _save_state(eng_id, state)
                    _add_mission_log(
                        eng_id, f"Advanced: Phase {phase_num} complete → Phase {next_phase['phase']} active"
                    )
                    return _fmt(
                        {
                            "action": "ADVANCED",
                            "completed": f"Phase {phase_num}",
                            "now_active": f"Phase {next_phase['phase']}: {next_phase['name']}",
                            "dick_says": _phase_advice(next_phase["phase"]),
                        },
                        fmt,
                        title=f"{CALLSIGN} Kill Chain — Advanced",
                    )
                else:
                    _save_state(eng_id, state)
                    return _fmt(
                        {
                            "action": "COMPLETE",
                            "status": "All 7 phases completed.",
                            "dick_says": "Time to write the report. Document like your freedom depends on it.",
                        },
                        fmt,
                        title=f"{CALLSIGN} Kill Chain — Complete",
                    )
            else:
                return "No active phase to advance. Use phase= to specify, or set a phase to active first."
        else:
            # Advance specific phase
            idx = phase_num - 1
            state["kill_chain"][idx]["status"] = "active"
            _save_state(eng_id, state)
            return _fmt(
                {
                    "action": "ACTIVATED",
                    "phase": f"Phase {phase_num}: {state['kill_chain'][idx]['name']}",
                    "dick_says": _phase_advice(phase_num),
                },
                fmt,
                title=f"{CALLSIGN} Kill Chain — Phase {phase_num} Active",
            )

    if action == "add_finding":
        if not state:
            return f"Error: No engagement '{eng_id}' found. Use action='status' to create one first."

        finding = _sanitize(params.finding) or params.finding
        if not finding:
            return "Error: finding= is required for add_finding."

        phase_num = params.phase
        if not phase_num:
            # Add to current active phase
            kc = state["kill_chain"]
            active_p = next((p for p in kc if p["status"] == "active"), None)
            if active_p:
                phase_num = active_p["phase"]
            else:
                return "Error: No active phase. Specify phase= or advance to a phase first."

        idx = phase_num - 1
        if "findings" not in state["kill_chain"][idx]:
            state["kill_chain"][idx]["findings"] = []
        finding_entry: dict[str, Any] = {
            "description": finding,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if params.image_path:
            try:
                validated_path = _validate_image_path(params.image_path)
                if validated_path:
                    finding_entry["image_path"] = validated_path
            except ValueError as e:
                return f"Error: {e}"
        state["kill_chain"][idx]["findings"].append(finding_entry)
        _save_state(eng_id, state)
        _add_mission_log(eng_id, f"Finding logged in Phase {phase_num}: {finding[:80]}")

        return _fmt(
            {
                "action": "FINDING LOGGED",
                "phase": f"Phase {phase_num}: {state['kill_chain'][idx]['name']}",
                "finding": finding,
                "total_phase_findings": len(state["kill_chain"][idx]["findings"]),
                "dick_says": "Documented. Now chain it. What does this finding unlock?",
            },
            fmt,
            title=f"{CALLSIGN} Finding Added",
        )

    if action == "reset":
        if not state:
            return f"No engagement '{eng_id}' to reset."
        state["kill_chain"] = [dict(p) for p in KILL_CHAIN_PHASES]
        state["reset_at"] = datetime.now(timezone.utc).isoformat()
        _save_state(eng_id, state)
        return _fmt(
            {"action": "RESET", "engagement": eng_id, "status": "Kill chain reset. All phases pending."},
            fmt,
            title=f"{CALLSIGN} Kill Chain — Reset",
        )

    return f"Error: Unknown action '{action}'. Available: 'status', 'advance', 'add_finding', 'reset', 'list'"


# ═══════════════════════════════════════════════════════════════
# Tool: rick_next_move — Situational awareness. What's next.
# ═══════════════════════════════════════════════════════════════


async def rick_next_move(params: NextMoveInput) -> str:
    """Dick tells you what to do next. Analyzes your position, findings, and kill chain state. JARVIS-level situational awareness."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    state = _load_state(eng_id)
    fmt = params.response_format

    if not state:
        return _fmt(
            {
                "error": f"No engagement '{eng_id}' found.",
                "suggestion": f"Start one: rick_full_auto(target='...', engagement_id='{eng_id}')",
            },
            fmt,
            title=f"{CALLSIGN} Next Move",
        )

    # Analyze current state
    completed_phases = [p for p in state["kill_chain"] if p["status"] == "completed"]
    active_phases = [p for p in state["kill_chain"] if p["status"] == "active"]
    all_findings = []
    for p in state["kill_chain"]:
        for f in p.get("findings", []):
            all_findings.append({"phase": p["name"], "finding": f["description"]})

    # Override position if provided
    position = _sanitize(params.current_position) if params.current_position else None
    extra_findings = _sanitize(params.findings_so_far) if params.findings_so_far else None

    result: dict[str, Any] = {
        "engagement": eng_id,
        "target": state.get("target", "Unknown"),
    }

    # Current situation
    if active_phases:
        current = active_phases[0]
        result["current_phase"] = f"Phase {current['phase']}: {current['name']}"
        result["phase_findings"] = len(current.get("findings", []))
    elif completed_phases and len(completed_phases) < 7:
        next_p = next((p for p in state["kill_chain"] if p["status"] == "pending"), None)
        result["current_phase"] = "Between phases"
        if next_p:
            result["next_phase"] = f"Phase {next_p['phase']}: {next_p['name']}"

    if position:
        result["reported_position"] = position

    result["completed_phases"] = len(completed_phases)
    result["total_findings"] = len(all_findings)

    # Generate Dick's recommendations based on state
    recommendations: list[str] = []
    tools_to_use: list[str] = []

    if not active_phases and not completed_phases:
        # Haven't started
        recommendations.append("You haven't started. Run recon first — know your target before you touch it.")
        recommendations.append("Use rick_full_auto to get the complete playbook, or advance to Phase 1 manually.")
        tools_to_use.extend(["rick_full_auto", "rick_recon", "rick_kill_chain(action='advance', phase=1)"])
    elif active_phases:
        phase_num = active_phases[0]["phase"]
        phase_findings = active_phases[0].get("findings", [])

        if phase_num == 1:
            # Recon phase
            if len(phase_findings) < 3:
                recommendations.append("Not enough recon data. Keep digging.")
                recommendations.append(
                    "Subdomain enumeration, port scans, tech stack fingerprinting, OSINT — all of it."
                )
                recommendations.append("Don't move to exploitation until you've mapped the full attack surface.")
                tools_to_use.extend(["rick_recon", "rick_threat_model"])
            else:
                recommendations.append(
                    f"Good recon — {len(phase_findings)} findings logged. Consider advancing to Phase 2."
                )
                recommendations.append("Review findings for attack vectors before moving on.")
                tools_to_use.extend(["rick_vuln_assess", "rick_kill_chain(action='advance')"])

        elif phase_num == 2:
            recommendations.append("Weaponization: match what recon found to exploits.")
            recommendations.append("Custom payloads for the specific tech stack. Test in your lab first.")
            tools_to_use.extend(["rick_payload_guide", "rick_tool_recommend", "rick_cheatsheet"])

        elif phase_num == 3:
            recommendations.append("Delivery: pick your entry point. Path of least resistance.")
            if position:
                recommendations.append(f"From {position}, evaluate: phishing, direct exploit, or credential attack?")
            tools_to_use.extend(["rick_attack_chain", "rick_tool_recommend"])

        elif phase_num == 4:
            recommendations.append("Exploitation: execute the plan. First shot should count.")
            recommendations.append("If initial exploit fails, DON'T spray. Reassess, adjust, retry with precision.")
            if position:
                recommendations.append(f"Position: {position} — check for privesc vectors immediately after landing.")
            tools_to_use.extend(["rick_vuln_assess", "rick_cheatsheet", "rick_pivot_plan"])

        elif phase_num == 5:
            recommendations.append("Persistence: you're in, now stay in. Multiple mechanisms.")
            recommendations.append("Web shells, scheduled tasks, certs, golden tickets — don't rely on one.")
            tools_to_use.extend(["rick_pivot_plan", "rick_attack_chain"])

        elif phase_num == 6:
            recommendations.append("C2: blend your traffic. Slow beacons. Domain fronting. Encrypted channels.")
            recommendations.append("Operational security is everything now. Don't get burned.")
            tools_to_use.extend(["rick_c2_compare", "rick_detection_rules"])

        elif phase_num == 7:
            recommendations.append("Actions on objectives. Get what you came for.")
            recommendations.append("Document EVERYTHING. Screenshots, hashes, proof. This is the report.")
            recommendations.append("Start cleanup planning. Remove persistence, test accounts, artifacts.")
            tools_to_use.extend(["rick_report_template", "rick_debrief", "rick_tracker"])

    elif len(completed_phases) == 7:
        recommendations.append("All phases complete. Time to write the report.")
        recommendations.append("Prioritize findings by business impact, not just CVSS.")
        recommendations.append(
            "Include remediation for every finding. Don't just say it's broken — hand them the blueprint."
        )
        tools_to_use.extend(["rick_report_template", "rick_debrief", "rick_tracker(action='export_markdown')"])

    # Position-specific recommendations
    if position:
        pivot_positions = {
            "linux_webserver",
            "windows_workstation",
            "windows_server",
            "container",
            "cloud_instance",
            "database_server",
            "network_device",
        }
        if position.lower().replace(" ", "_") in pivot_positions:
            recommendations.append(f"Dick sees you're on a {position}. Run rick_pivot_plan for immediate actions.")
            tools_to_use.append(f"rick_pivot_plan(position='{position.lower().replace(' ', '_')}')")

    # Extra findings analysis
    if extra_findings:
        result["additional_context"] = extra_findings
        recommendations.append("Dick sees new intel. Log it with rick_kill_chain(action='add_finding').")

    result["dick_says"] = recommendations
    result["recommended_tools"] = tools_to_use

    # Add the phase advice
    if active_phases:
        result["phase_guidance"] = _phase_advice(active_phases[0]["phase"])

    return _fmt(result, fmt, title=f"{CALLSIGN} Next Move — {eng_id}")


# ═══════════════════════════════════════════════════════════════
# Tool: rick_sitrep — Situation Report. Where are we.
# ═══════════════════════════════════════════════════════════════


async def rick_sitrep(params: SitrepInput) -> str:
    """Situation Report. One command, full tactical picture — kill chain, findings, mission log, recommendations."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    state = _load_state(eng_id)
    fmt = params.response_format

    if not state:
        return _fmt(
            {
                "error": f"No engagement '{eng_id}' found.",
                "suggestion": f"Start one: rick_full_auto(target='...', engagement_id='{eng_id}')",
            },
            fmt,
            title=f"{CALLSIGN} SITREP",
        )

    # Engagement identity
    target = state.get("target", "Unknown")
    target_type = state.get("target_type", "Unknown")
    created = state.get("created", "Unknown")
    objective = state.get("objective", "Not specified")

    # Kill chain analysis
    kill_chain = state.get("kill_chain", [])
    completed = [p for p in kill_chain if p.get("status") == "completed"]
    active = [p for p in kill_chain if p.get("status") == "active"]
    pending = [p for p in kill_chain if p.get("status") == "pending"]

    # Build progress bar
    completed_count = len(completed)
    progress_filled = "=" * (completed_count * 2)
    if active:
        progress_filled += ">"
    progress_empty = " " * ((7 - completed_count - len(active)) * 2)
    active_label = (
        f"Phase {active[0]['phase']}: {active[0]['name']}"
        if active
        else ("COMPLETE" if completed_count == 7 else "No active phase")
    )

    # Collect all findings across phases
    all_findings: list[dict[str, Any]] = []
    phase_summary: list[str] = []
    for p in kill_chain:
        findings = p.get("findings", [])
        status_icon = {"completed": "DONE", "active": "ACTIVE", "pending": "---"}.get(p["status"], "---")
        finding_count = f"({len(findings)} findings)" if findings else ""
        phase_summary.append(f"Phase {p['phase']}: {p['name']} — {status_icon} {finding_count}")
        for f in findings:
            all_findings.append({"phase": p["name"], "phase_num": p["phase"], **f})

    # Recent findings (last 5)
    recent_findings = sorted(all_findings, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
    recent_formatted = []
    for f in recent_findings:
        ts = f.get("timestamp", "")[:16].replace("T", " ")
        recent_formatted.append(f"[Phase {f['phase_num']}] {f.get('description', '?')} — {ts}")

    # Mission log (last 10)
    mission_log = state.get("mission_log", [])
    recent_log = mission_log[-10:]
    log_formatted = []
    for entry in reversed(recent_log):
        ts = entry.get("timestamp", "")[:16].replace("T", " ")
        log_formatted.append(f"{ts} — {entry.get('entry', '?')}")

    # Tool history (last 10)
    tool_history = state.get("tool_history", [])
    recent_tools = tool_history[-10:]
    tools_formatted = []
    for t in reversed(recent_tools):
        ts = t.get("timestamp", "")[:16].replace("T", " ")
        tools_formatted.append(f"{t.get('tool', '?')} — {ts}")

    # Notes
    notes = state.get("notes", [])

    # Tactical assessment
    assessment: list[str] = []
    if completed_count == 7:
        assessment.append("All phases complete. Time to write the report.")
        assessment.append("Use rick_report_template and rick_debrief to close out.")
    elif active:
        active_phase = active[0]
        phase_findings = len(active_phase.get("findings", []))
        if active_phase["phase"] == 1 and phase_findings < 3:
            assessment.append(f"Recon in progress — {phase_findings} findings. Keep digging before advancing.")
        elif active_phase["phase"] == 1 and phase_findings >= 3:
            assessment.append(f"Recon looks solid — {phase_findings} findings. Consider advancing to Weaponization.")
        elif phase_findings == 0:
            assessment.append(f"Phase {active_phase['phase']} ({active_phase['name']}) active but no findings yet.")
        else:
            assessment.append(
                f"Phase {active_phase['phase']} ({active_phase['name']}) in progress — {phase_findings} findings logged."
            )
    elif completed_count == 0:
        assessment.append("Engagement initialized but no phases active. Advance to Phase 1 to begin.")
    else:
        next_p = pending[0] if pending else None
        if next_p:
            assessment.append(f"Between phases. Next up: Phase {next_p['phase']} ({next_p['name']}).")

    result: dict[str, Any] = {
        "engagement": eng_id,
        "target": f"{target} ({target_type})",
        "objective": objective,
        "created": created,
        "progress": f"[{progress_filled}{progress_empty}] {completed_count}/7 — {active_label}",
        "kill_chain": phase_summary,
        "total_findings": len(all_findings),
    }
    if recent_formatted:
        result["recent_findings"] = recent_formatted
    if log_formatted:
        result["mission_log"] = log_formatted
    if tools_formatted:
        result["tool_activity"] = tools_formatted
    if notes:
        result["notes"] = notes
    result["tactical_assessment"] = assessment

    return _fmt(result, fmt, title=f"{CALLSIGN} SITREP — {eng_id}")


# ═══════════════════════════════════════════════════════════════
# Registration
# ═══════════════════════════════════════════════════════════════


def register(mcp):
    """Register Dick's tools on the MCP server."""
    mcp.tool(
        name="rick_full_auto",
        annotations={
            "title": "Full Auto — Complete Target Playbook",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_full_auto))
    mcp.tool(
        name="rick_kill_chain",
        annotations={
            "title": "Kill Chain Tracker",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_kill_chain))
    mcp.tool(
        name="rick_next_move",
        annotations={
            "title": "Next Move — Situational Awareness",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_next_move))
    mcp.tool(
        name="rick_sitrep",
        annotations={
            "title": "Situation Report",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_sitrep))
