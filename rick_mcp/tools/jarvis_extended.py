"""JARVIS extended tools — engagement management, analysis, and safety rails.

rick_notes, rick_timeline, rick_compare, rick_scope_check, rick_export,
rick_checklist, rick_tag, rick_rollback.
"""

import copy
import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import (
    ChecklistInput,
    CompareInput,
    ExportInput,
    NotesInput,
    RollbackInput,
    ScopeCheckInput,
    TagInput,
    TimelineInput,
)
from rick_mcp.tools.jarvis_state import (
    _add_mission_log,
    _get_checklist_template,
    _load_state,
    _save_state,
    _validate_image_path,
    validate_mitre_id,
    validate_severity,
)

# ═══════════════════════════════════════════════════════════════
# Tool: rick_notes — Engagement notes with image attachments
# ═══════════════════════════════════════════════════════════════


async def rick_notes(params: NotesInput) -> str:
    """Add, list, search, or delete engagement notes. Supports image attachments."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    action = (_sanitize(params.action) or "list").lower().strip()
    fmt = params.response_format
    state = _load_state(eng_id)

    if not state:
        return _fmt(
            {
                "error": f"No engagement '{eng_id}' found.",
                "suggestion": "Create one with rick_full_auto or rick_kill_chain.",
            },
            fmt,
            title=f"{CALLSIGN} Notes",
        )

    if "notes" not in state:
        state["notes"] = []

    if action == "add":
        content = _sanitize(params.content) if params.content else None
        if not content:
            return "Error: content= is required for add action."
        note_entry: dict[str, Any] = {
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if params.image_path:
            try:
                validated = _validate_image_path(params.image_path)
                if validated:
                    note_entry["image_path"] = validated
            except ValueError as e:
                return f"Error: {e}"
        state["notes"].append(note_entry)
        _save_state(eng_id, state)
        _add_mission_log(eng_id, f"Note added: {content[:80]}")
        return _fmt(
            {
                "action": "NOTE ADDED",
                "content": content,
                "total_notes": len(state["notes"]),
                **({"image": note_entry.get("image_path", "")} if "image_path" in note_entry else {}),
            },
            fmt,
            title=f"{CALLSIGN} Note Added",
        )

    if action == "list":
        if not state["notes"]:
            return _fmt({"engagement": eng_id, "notes": "No notes yet."}, fmt, title=f"{CALLSIGN} Notes")
        formatted = []
        for i, note in enumerate(state["notes"]):
            if isinstance(note, str):
                formatted.append(f"[{i}] {note}")
            else:
                ts = note.get("timestamp", "")[:16].replace("T", " ")
                img = f" [IMG: {note['image_path']}]" if note.get("image_path") else ""
                formatted.append(f"[{i}] {note.get('content', '?')} — {ts}{img}")
        return _fmt(
            {"engagement": eng_id, "count": len(state["notes"]), "notes": formatted}, fmt, title=f"{CALLSIGN} Notes"
        )

    if action == "search":
        term = (_sanitize(params.search_term) or "").lower()
        if not term:
            return "Error: search_term= is required for search action."
        matches = []
        for i, note in enumerate(state["notes"]):
            text = note if isinstance(note, str) else note.get("content", "")
            if term in text.lower():
                matches.append(f"[{i}] {text}")
        return _fmt(
            {
                "engagement": eng_id,
                "search_term": term,
                "matches": len(matches),
                "results": matches or ["No matches found."],
            },
            fmt,
            title=f"{CALLSIGN} Note Search",
        )

    if action == "delete":
        idx = params.note_index
        if idx is None:
            return "Error: note_index= is required for delete action."
        if idx >= len(state["notes"]):
            return f"Error: note_index {idx} out of range (0-{len(state['notes']) - 1})."
        removed = state["notes"].pop(idx)
        _save_state(eng_id, state)
        desc = removed if isinstance(removed, str) else removed.get("content", "?")
        return _fmt(
            {"action": "NOTE DELETED", "index": idx, "content": desc[:80], "remaining": len(state["notes"])},
            fmt,
            title=f"{CALLSIGN} Note Deleted",
        )

    return f"Error: Unknown action '{action}'. Available: 'add', 'list', 'search', 'delete'"


# ═══════════════════════════════════════════════════════════════
# Tool: rick_timeline — Unified chronological event timeline
# ═══════════════════════════════════════════════════════════════


async def rick_timeline(params: TimelineInput) -> str:
    """Unified chronological timeline — findings, mission log, and tool history in one view. Filterable."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    fmt = params.response_format
    state = _load_state(eng_id)

    if not state:
        return _fmt({"error": f"No engagement '{eng_id}' found."}, fmt, title=f"{CALLSIGN} Timeline")

    events: list[dict[str, Any]] = []

    # Collect findings from kill chain
    for phase in state.get("kill_chain", []):
        for finding in phase.get("findings", []):
            events.append(
                {
                    "timestamp": finding.get("timestamp", ""),
                    "type": "finding",
                    "phase": phase["phase"],
                    "description": finding.get("description", "?"),
                }
            )

    # Collect mission log entries
    for entry in state.get("mission_log", []):
        events.append(
            {
                "timestamp": entry.get("timestamp", ""),
                "type": "log",
                "description": entry.get("entry", "?"),
            }
        )

    # Collect tool history
    for tool_entry in state.get("tool_history", []):
        events.append(
            {
                "timestamp": tool_entry.get("timestamp", ""),
                "type": "tool",
                "description": f"{tool_entry.get('tool', '?')}: {tool_entry.get('summary', '')}".strip(": "),
            }
        )

    # Apply filters
    if params.filter_phase is not None:
        events = [e for e in events if e.get("phase") == params.filter_phase]

    if params.filter_type:
        ft = params.filter_type.lower().strip()
        events = [e for e in events if e["type"] == ft]

    if params.since:
        events = [e for e in events if e["timestamp"] >= params.since]

    if params.until:
        events = [e for e in events if e["timestamp"] <= params.until]

    # Sort chronologically
    events.sort(key=lambda e: e.get("timestamp", ""))

    if not events:
        return _fmt({"engagement": eng_id, "events": "No events match the filter."}, fmt, title=f"{CALLSIGN} Timeline")

    formatted = []
    for e in events:
        ts = e["timestamp"][:16].replace("T", " ") if e["timestamp"] else "?"
        phase_str = f" [P{e['phase']}]" if "phase" in e else ""
        formatted.append(f"{ts} [{e['type'].upper()}]{phase_str} {e['description']}")

    return _fmt(
        {"engagement": eng_id, "total_events": len(formatted), "timeline": formatted},
        fmt,
        title=f"{CALLSIGN} Timeline — {eng_id}",
    )


# ═══════════════════════════════════════════════════════════════
# Tool: rick_compare — Diff two engagements
# ═══════════════════════════════════════════════════════════════


async def rick_compare(params: CompareInput) -> str:
    """Compare two engagements side by side. Useful for retests — see what changed."""
    id_a = _sanitize(params.engagement_id_a) or params.engagement_id_a
    id_b = _sanitize(params.engagement_id_b) or params.engagement_id_b
    fmt = params.response_format
    state_a = _load_state(id_a)
    state_b = _load_state(id_b)

    errors = []
    if not state_a:
        errors.append(f"Engagement '{id_a}' not found.")
    if not state_b:
        errors.append(f"Engagement '{id_b}' not found.")
    if errors:
        return _fmt({"errors": errors}, fmt, title=f"{CALLSIGN} Compare")

    def _summarize(state: dict[str, Any]) -> dict[str, Any]:
        kc = state.get("kill_chain", [])
        completed = sum(1 for p in kc if p.get("status") == "completed")
        active = next((p for p in kc if p.get("status") == "active"), None)
        total_findings = sum(len(p.get("findings", [])) for p in kc)
        phase_findings = {p["name"]: len(p.get("findings", [])) for p in kc}
        return {
            "target": state.get("target", "Unknown"),
            "target_type": state.get("target_type", "Unknown"),
            "created": state.get("created", "Unknown"),
            "progress": f"{completed}/7",
            "active_phase": f"Phase {active['phase']}: {active['name']}"
            if active
            else ("COMPLETE" if completed == 7 else "None"),
            "total_findings": total_findings,
            "findings_by_phase": phase_findings,
            "notes_count": len(state.get("notes", [])),
            "log_entries": len(state.get("mission_log", [])),
        }

    summary_a = _summarize(state_a)
    summary_b = _summarize(state_b)

    # Build diff
    diff: list[str] = []
    for key in summary_a:
        val_a = summary_a[key]
        val_b = summary_b.get(key)
        if val_a != val_b:
            diff.append(f"{key}: {val_a} → {val_b}")

    result: dict[str, Any] = {
        f"engagement_a ({id_a})": summary_a,
        f"engagement_b ({id_b})": summary_b,
    }
    if diff:
        result["differences"] = diff
    else:
        result["differences"] = "No differences found."

    return _fmt(result, fmt, title=f"{CALLSIGN} Compare — {id_a} vs {id_b}")


# ═══════════════════════════════════════════════════════════════
# Tool: rick_scope_check — Safety rail
# ═══════════════════════════════════════════════════════════════


async def rick_scope_check(params: ScopeCheckInput) -> str:
    """Check targets and actions against stored scope/ROE. Safety rail — know your boundaries."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    fmt = params.response_format
    state = _load_state(eng_id)

    if not state:
        return _fmt({"error": f"No engagement '{eng_id}' found."}, fmt, title=f"{CALLSIGN} Scope Check")

    if "scope" not in state:
        state["scope"] = []
    if "scope_roe" not in state:
        state["scope_roe"] = ""

    modified = False

    # Add scope items
    if params.add_scope:
        new_items = [s.strip() for s in params.add_scope.split(",") if s.strip()]
        for item in new_items:
            sanitized = _sanitize(item) or item
            if sanitized not in state["scope"]:
                state["scope"].append(sanitized)
        modified = True
        _add_mission_log(eng_id, f"Scope updated: added {len(new_items)} item(s)")

    # Set ROE notes
    if params.set_roe:
        state["scope_roe"] = _sanitize(params.set_roe) or params.set_roe
        modified = True
        _add_mission_log(eng_id, "ROE notes updated")

    if modified:
        _save_state(eng_id, state)

    result: dict[str, Any] = {"engagement": eng_id}

    # Check target against scope
    if params.target:
        target = (_sanitize(params.target) or params.target).lower()
        if not state["scope"]:
            result["target_check"] = {
                "target": params.target,
                "verdict": "UNKNOWN",
                "reason": "No scope defined. Use add_scope= to define the engagement scope first.",
            }
        else:
            in_scope = False
            matched_rule = None
            for scope_item in state["scope"]:
                si = scope_item.lower()
                # Substring/prefix match — covers IPs, hostnames, wildcards
                if target in si or si in target or (si.startswith("*.") and target.endswith(si[1:])):
                    in_scope = True
                    matched_rule = scope_item
                    break
            result["target_check"] = {
                "target": params.target,
                "verdict": "IN SCOPE" if in_scope else "OUT OF SCOPE",
                **({"matched_rule": matched_rule} if matched_rule else {}),
                "warning": "" if in_scope else "DO NOT PROCEED. Target is outside authorized scope.",
            }

    # Check action against ROE
    if params.action:
        action_text = _sanitize(params.action) or params.action
        if not state["scope_roe"]:
            result["action_check"] = {
                "action": action_text,
                "verdict": "UNKNOWN",
                "reason": "No ROE defined. Use set_roe= to define rules of engagement.",
            }
        else:
            result["action_check"] = {
                "action": action_text,
                "roe": state["scope_roe"],
                "verdict": "REVIEW ROE",
                "guidance": "Check this action against the ROE above. When in doubt, don't.",
            }

    # If no check requested, show current scope
    if not params.target and not params.action and not params.add_scope and not params.set_roe:
        result["scope"] = state["scope"] or ["No scope defined."]
        result["scope_roe"] = state["scope_roe"] or "No ROE defined."
        result["scope_count"] = len(state["scope"])

    return _fmt(result, fmt, title=f"{CALLSIGN} Scope Check — {eng_id}")


# ═══════════════════════════════════════════════════════════════
# Tool: rick_export — Export engagement state
# ═══════════════════════════════════════════════════════════════


async def rick_export(params: ExportInput) -> str:
    """Export engagement state to markdown, JSON, or CSV."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    fmt = params.response_format
    export_fmt = (params.export_format or "markdown").lower().strip()
    state = _load_state(eng_id)

    if not state:
        return _fmt({"error": f"No engagement '{eng_id}' found."}, fmt, title=f"{CALLSIGN} Export")

    if export_fmt == "json":
        return json.dumps(state, indent=2, default=str)

    if export_fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["phase", "phase_name", "description", "timestamp", "severity", "category", "mitre_id", "image_path"]
        )
        for phase in state.get("kill_chain", []):
            for finding in phase.get("findings", []):
                writer.writerow(
                    [
                        phase["phase"],
                        phase["name"],
                        finding.get("description", ""),
                        finding.get("timestamp", ""),
                        finding.get("severity", ""),
                        finding.get("category", ""),
                        finding.get("mitre_id", ""),
                        finding.get("image_path", ""),
                    ]
                )
        return output.getvalue()

    # Default: markdown
    sections: list[str] = []
    sections.append(f"# Engagement Report: {eng_id}")
    sections.append("")
    sections.append(f"**Target:** {state.get('target', 'Unknown')}")
    sections.append(f"**Type:** {state.get('target_type', 'Unknown')}")
    sections.append(f"**Created:** {state.get('created', 'Unknown')}")
    sections.append(f"**Objective:** {state.get('objective', 'Not specified')}")
    sections.append("")

    # Scope
    scope = state.get("scope", [])
    if scope:
        sections.append("## Scope")
        for s in scope:
            sections.append(f"- {s}")
        sections.append("")

    roe = state.get("scope_roe", "")
    if roe:
        sections.append("## Rules of Engagement")
        sections.append(roe)
        sections.append("")

    # Kill chain
    sections.append("## Kill Chain Progress")
    for phase in state.get("kill_chain", []):
        icon = {"completed": "DONE", "active": "ACTIVE", "pending": "---"}.get(phase["status"], "---")
        sections.append(f"### Phase {phase['phase']}: {phase['name']} — {icon}")
        findings = phase.get("findings", [])
        if findings:
            for f in findings:
                sev = f" [{f['severity'].upper()}]" if f.get("severity") else ""
                mitre = f" ({f['mitre_id']})" if f.get("mitre_id") else ""
                img = f" [IMG: {f['image_path']}]" if f.get("image_path") else ""
                sections.append(f"- {f.get('description', '?')}{sev}{mitre}{img}")
        else:
            sections.append("- No findings")
        sections.append("")

    # Notes
    notes = state.get("notes", [])
    if notes:
        sections.append("## Notes")
        for note in notes:
            if isinstance(note, str):
                sections.append(f"- {note}")
            else:
                img = f" [IMG: {note['image_path']}]" if note.get("image_path") else ""
                sections.append(f"- {note.get('content', '?')}{img}")
        sections.append("")

    # Checklist
    checklist = state.get("checklist", [])
    if checklist:
        sections.append("## Checklist")
        for item in checklist:
            check = "x" if item.get("checked") else " "
            sections.append(f"- [{check}] [P{item.get('phase', '?')}] {item.get('item', '?')}")
        sections.append("")

    return "\n".join(sections)


# ═══════════════════════════════════════════════════════════════
# Tool: rick_checklist — Phase-specific checklists
# ═══════════════════════════════════════════════════════════════


async def rick_checklist(params: ChecklistInput) -> str:
    """Phase-specific checklists auto-populated by target type. Generate, check, uncheck, or view status."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    action = (_sanitize(params.action) or "status").lower().strip()
    fmt = params.response_format
    state = _load_state(eng_id)

    if not state:
        return _fmt({"error": f"No engagement '{eng_id}' found."}, fmt, title=f"{CALLSIGN} Checklist")

    if "checklist" not in state:
        state["checklist"] = []

    if action == "generate":
        phase = params.phase
        if not phase:
            # Generate for current active phase
            active = next((p for p in state.get("kill_chain", []) if p.get("status") == "active"), None)
            if active:
                phase = active["phase"]
            else:
                return "Error: No active phase. Specify phase= to generate checklist for."

        target_type = state.get("target_type", "web_app")
        new_items = _get_checklist_template(target_type, phase)
        if not new_items:
            return _fmt(
                {"phase": phase, "message": "No checklist template available for this phase/target combination."},
                fmt,
                title=f"{CALLSIGN} Checklist",
            )
        state["checklist"].extend(new_items)
        _save_state(eng_id, state)
        _add_mission_log(eng_id, f"Checklist generated for Phase {phase} ({len(new_items)} items)")
        return _fmt(
            {
                "action": "GENERATED",
                "phase": phase,
                "new_items": len(new_items),
                "total_items": len(state["checklist"]),
            },
            fmt,
            title=f"{CALLSIGN} Checklist Generated",
        )

    if action in ("check", "uncheck"):
        idx = params.item_index
        if idx is None:
            return "Error: item_index= is required for check/uncheck."
        if idx >= len(state["checklist"]):
            return f"Error: item_index {idx} out of range (0-{len(state['checklist']) - 1})."
        state["checklist"][idx]["checked"] = action == "check"
        _save_state(eng_id, state)
        item = state["checklist"][idx]
        return _fmt(
            {"action": action.upper(), "index": idx, "item": item["item"], "checked": item["checked"]},
            fmt,
            title=f"{CALLSIGN} Checklist Updated",
        )

    if action == "status":
        if not state["checklist"]:
            return _fmt(
                {"engagement": eng_id, "checklist": "No checklist items. Use action='generate' to create one."},
                fmt,
                title=f"{CALLSIGN} Checklist",
            )
        total = len(state["checklist"])
        checked = sum(1 for item in state["checklist"] if item.get("checked"))
        items_formatted = []
        for i, item in enumerate(state["checklist"]):
            check = "x" if item.get("checked") else " "
            items_formatted.append(f"[{i}] [{check}] [P{item.get('phase', '?')}] {item.get('item', '?')}")
        return _fmt(
            {"engagement": eng_id, "progress": f"{checked}/{total} complete", "items": items_formatted},
            fmt,
            title=f"{CALLSIGN} Checklist — {eng_id}",
        )

    return f"Error: Unknown action '{action}'. Available: 'generate', 'check', 'uncheck', 'status'"


# ═══════════════════════════════════════════════════════════════
# Tool: rick_tag — Tag findings with metadata
# ═══════════════════════════════════════════════════════════════


async def rick_tag(params: TagInput) -> str:
    """Tag findings with severity, category, and MITRE ATT&CK technique IDs."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    fmt = params.response_format
    state = _load_state(eng_id)

    if not state:
        return _fmt({"error": f"No engagement '{eng_id}' found."}, fmt, title=f"{CALLSIGN} Tag")

    kc = state.get("kill_chain", [])
    phase_idx = params.phase - 1
    if phase_idx >= len(kc):
        return f"Error: Phase {params.phase} not found."

    findings = kc[phase_idx].get("findings", [])
    if params.finding_index >= len(findings):
        return f"Error: Finding index {params.finding_index} out of range (0-{len(findings) - 1})."

    finding = findings[params.finding_index]
    updated: list[str] = []

    if params.severity:
        try:
            finding["severity"] = validate_severity(params.severity)
            updated.append(f"severity={finding['severity']}")
        except ValueError as e:
            return f"Error: {e}"

    if params.category:
        finding["category"] = _sanitize(params.category) or params.category
        updated.append(f"category={finding['category']}")

    if params.mitre_id:
        try:
            finding["mitre_id"] = validate_mitre_id(params.mitre_id)
            updated.append(f"mitre_id={finding['mitre_id']}")
        except ValueError as e:
            return f"Error: {e}"

    if not updated:
        return "Error: Provide at least one of severity=, category=, or mitre_id= to tag."

    _save_state(eng_id, state)
    _add_mission_log(eng_id, f"Tagged finding in Phase {params.phase}: {', '.join(updated)}")

    return _fmt(
        {
            "action": "TAGGED",
            "phase": f"Phase {params.phase}: {kc[phase_idx]['name']}",
            "finding": finding.get("description", "?"),
            "tags_applied": updated,
            "current_tags": {k: finding[k] for k in ("severity", "category", "mitre_id") if k in finding},
        },
        fmt,
        title=f"{CALLSIGN} Finding Tagged",
    )


# ═══════════════════════════════════════════════════════════════
# Tool: rick_rollback — Undo last state change
# ═══════════════════════════════════════════════════════════════


async def rick_rollback(params: RollbackInput) -> str:
    """Undo the last kill chain state change. Requires confirm=True. Uses state snapshots."""
    eng_id = _sanitize(params.engagement_id) or params.engagement_id
    fmt = params.response_format
    state = _load_state(eng_id)

    if not state:
        return _fmt({"error": f"No engagement '{eng_id}' found."}, fmt, title=f"{CALLSIGN} Rollback")

    snapshots = state.get("snapshots", [])
    if not snapshots:
        return _fmt(
            {
                "error": "No snapshots available to rollback to.",
                "suggestion": "Snapshots are created automatically when state is modified with snapshot=True.",
            },
            fmt,
            title=f"{CALLSIGN} Rollback",
        )

    if not params.confirm:
        latest = snapshots[-1]
        return _fmt(
            {
                "warning": "Rollback requires confirm=True.",
                "snapshot_timestamp": latest["timestamp"],
                "preview": f"Will restore state from {latest['timestamp']}",
                "snapshots_available": len(snapshots),
            },
            fmt,
            title=f"{CALLSIGN} Rollback Preview",
        )

    # Restore
    latest = snapshots.pop()
    restored = copy.deepcopy(latest["state"])
    restored["snapshots"] = snapshots  # Preserve remaining snapshots
    _save_state(eng_id, restored)
    _add_mission_log(eng_id, f"State rolled back to snapshot from {latest['timestamp']}")

    return _fmt(
        {
            "action": "ROLLED BACK",
            "restored_from": latest["timestamp"],
            "remaining_snapshots": len(snapshots),
        },
        fmt,
        title=f"{CALLSIGN} Rollback Complete",
    )


# ═══════════════════════════════════════════════════════════════
# Registration
# ═══════════════════════════════════════════════════════════════


def register(mcp):
    """Register JARVIS extended tools on the MCP server."""
    mcp.tool(
        name="rick_notes",
        annotations={
            "title": "Engagement Notes",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_notes))
    mcp.tool(
        name="rick_timeline",
        annotations={
            "title": "Engagement Timeline",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_timeline))
    mcp.tool(
        name="rick_compare",
        annotations={
            "title": "Compare Engagements",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_compare))
    mcp.tool(
        name="rick_scope_check",
        annotations={
            "title": "Scope Check — Safety Rail",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_scope_check))
    mcp.tool(
        name="rick_export",
        annotations={
            "title": "Export Engagement",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_export))
    mcp.tool(
        name="rick_checklist",
        annotations={
            "title": "Phase Checklist",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_checklist))
    mcp.tool(
        name="rick_tag",
        annotations={
            "title": "Tag Finding",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_tag))
    mcp.tool(
        name="rick_rollback",
        annotations={
            "title": "Rollback State",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_rollback))
