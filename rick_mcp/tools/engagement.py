"""Engagement lifecycle tools — ROE, reports, proposals, onboarding, debrief, tracker.

When ~/.rick_mcp/vault/ is configured (proper Obsidian Second Brain bootstrap detected by
rick_mcp.vault.is_configured()), every engagement tool also writes a Rick-voice AI-first note
to vault/Engagements/. Proposal creates the anchor note. Debrief, scoping, roe, and
client_onboarding append their respective sections to the matching note (best-effort match by
client+type). Tracker maintains its eng_id-anchored vault note with findings table.

Fork-friendly: tools degrade gracefully to text-only when no vault is configured.
"""

import json
from datetime import datetime
from pathlib import Path

from rick_mcp import vault
from rick_mcp.constants import CALLSIGN, MISSION_PHASES
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize, logger
from rick_mcp.identity import MOTTO, NAME
from rick_mcp.models import (
    DebriefInput,
    OnboardInput,
    ProposalInput,
    ReportInput,
    ROEInput,
    ScopingInput,
    TrackerInput,
)

# ── Vault body builders (Rick voice, AI-first wikilinks) ────────────────────────────────────


def _bullet_list(items: list[str], indent: str = "") -> str:
    return "\n".join(f"{indent}- {item}" for item in items)


def _proposal_vault_body(
    *,
    client: str,
    engagement_type: str,
    type_title: str,
    scope_desc: str,
    test_type: str,
    techniques: list[str],
    days: int,
    recommended_days: int,
    special_requirements: str | None,
) -> str:
    """Build the Rick-voice markdown body for a proposal-anchored engagement note.

    Wikilinks methodology, specialization, and default toolset. Caller-supplied context lines
    (techniques, scope_desc) are preserved verbatim from the proposal generator.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    spec_link = vault.specialization_wikilink(engagement_type)
    tool_links = vault.tools_wikilinks(engagement_type)
    operator_link = f"[[Identity/{NAME}]]"
    methodology_link = "[[Identity/Methodology]]"

    sections = [
        f"# {client} — {type_title}",
        "",
        "> **Status:** scoping",
        f"> **Prepared by:** {operator_link}",
        f"> **Date:** {today}",
        f"> **Recommended duration:** {recommended_days} business days",
        f"> **Requested duration:** {days} business days",
        "",
        "## Summary",
        "",
        f"{type_title} for {client}. {days} business days. PTES + OWASP + MITRE ATT&CK methodology, "
        f"applied with manual depth — scanner output is a starting point, not a finding.",
        "",
        "## Scope",
        "",
        f"- **Type:** {test_type}",
        f"- **Description:** {scope_desc}",
        "- **In-scope:** _[TBD — finalize in ROE]_",
        "- **Out-of-scope:** _[TBD — finalize in ROE]_",
        "",
        "## Methodology",
        "",
        f"Rick's 7-phase pipeline ({methodology_link}) layered on PTES + OWASP + MITRE ATT&CK. "
        f"Builder-to-breaker discipline — understand how the system was built before swinging the hammer.",
        "",
        "**Techniques:**",
        "",
        _bullet_list(techniques),
        "",
    ]

    if spec_link:
        sections += [
            "## Specialization",
            "",
            spec_link,
            "",
        ]

    if tool_links:
        sections += [
            "## Default Toolset",
            "",
            _bullet_list(tool_links),
            "",
        ]

    # Phase tracking — anchored to Rick's 7-phase methodology
    phase_lines = [
        "- Phase 1 — Reconnaissance: pending",
        "- Phase 2 — Vulnerability Assessment: pending",
        "- Phase 3 — Exploitation: pending",
        "- Phase 4 — Privilege Escalation: pending",
        "- Phase 5 — Lateral Movement: pending",
        "- Phase 6 — Documentation: pending",
        "- Phase 7 — Remediation Strategy: pending",
    ]
    sections += [
        "## Phase Tracking",
        "",
        "> Updated by `rick_tracker`, `rick_debrief`, and other engagement tools as work progresses.",
        "",
        *phase_lines,
        "",
    ]

    # Timeline — derive same way the proposal tool does
    sections += [
        f"## Timeline ({days} business days)",
        "",
        f"- **Recon:** {max(1, days // 5)}d",
        f"- **Testing:** {max(1, int(days * 0.5))}d",
        f"- **Exploitation:** {max(1, int(days * 0.2))}d",
        f"- **Reporting:** {max(1, int(days * 0.2))}d",
        "",
        "## Deliverables",
        "",
        _bullet_list(
            [
                "Executive Summary",
                "Technical Report",
                "Remediation Roadmap",
                "Evidence Package",
                "Debrief Presentation",
            ]
        ),
        "",
        "## Terms",
        "",
        "- **Authorization:** Written required",
        "- **Scope:** Authorized only",
        "- **Data handling:** PoC-level, securely deleted",
        "- **Escalation:** 1 hour for critical findings",
        "",
    ]

    if special_requirements:
        sections += [
            "## Special Requirements",
            "",
            special_requirements,
            "",
        ]

    sections += [
        "## Findings",
        "",
        "> Severity-sorted. Updated by `rick_tracker(action='add_finding')`.",
        "",
        "| Severity | Title | Status |",
        "|----------|-------|--------|",
        "| _(no findings yet)_ |  |  |",
        "",
        "## Key Decisions",
        "",
        "> Append directional decisions made during the engagement.",
        "",
        "## Debrief",
        "",
        "> Populated by `rick_debrief` post-engagement.",
        "",
        "---",
        "",
        f"*Generated by `rick_engagement_proposal` on {today}. Voice: Rick. Built like Rick's name is on it.*",
        "",
        f"> Recommended: {recommended_days}d. Requested: {days}d. Thorough > fast. Measure twice, cut once.",
        "> ",
        f"> — {operator_link}",
        "",
    ]

    return "\n".join(sections)


def _tracker_vault_body(eng_data: dict) -> str:
    """Build the Rick-voice body for a tracker-anchored engagement note (eng_id codename).

    Dynamic findings table is built from eng_data['findings']. Designed to be regenerated on
    every tracker write — the JSON state at ~/.rick_mcp/engagements/<eng_id>.json is canonical;
    this body is the human-readable vault projection of it.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    eng_id = eng_data.get("id", "[ENG-ID]")
    client = eng_data.get("client", "[CLIENT]")
    eng_type = eng_data.get("type", "pentest")
    eng_status = eng_data.get("status", "active")
    created_at = eng_data.get("created_at", today)
    type_title = eng_type.replace("_", " ").title()
    operator_link = f"[[Identity/{NAME}]]"
    methodology_link = "[[Identity/Methodology]]"
    spec_link = vault.specialization_wikilink(eng_type)
    tool_links = vault.tools_wikilinks(eng_type)

    sections = [
        f"# {eng_id} — {client}",
        "",
        f"> **Engagement ID:** `{eng_id}`",
        f"> **Type:** {type_title}",
        f"> **Status:** {eng_status}",
        f"> **Operator:** {operator_link}",
        f"> **Created:** {created_at}",
        "",
        "## Summary",
        "",
        f"Tracker-anchored engagement record for {client}. Findings, status, and timeline persist via "
        f"`rick_tracker`. Methodology: {methodology_link} (7-phase). This note mirrors the JSON state at "
        f"`~/.rick_mcp/engagements/{eng_id}.json` — JSON is canonical, vault is the human-readable "
        f"projection. Regenerated on every tracker write.",
        "",
    ]

    if spec_link:
        sections += ["## Specialization", "", spec_link, ""]
    if tool_links:
        sections += ["## Default Toolset", "", _bullet_list(tool_links), ""]

    findings = eng_data.get("findings", [])
    sections += [
        "## Findings",
        "",
        "> Updated by `rick_tracker(action='add_finding')`. JSON state in `~/.rick_mcp/engagements/`.",
        "",
        "| ID | Title | Severity | Status |",
        "|----|-------|----------|--------|",
    ]
    if findings:
        for f in findings:
            fid = f.get("id", "—")
            title = f.get("title", "—")
            sev = f.get("severity", "—")
            st = f.get("status", "—")
            sections.append(f"| {fid} | {title} | {sev} | {st} |")
    else:
        sections.append("| _(no findings yet)_ |  |  |  |")
    sections.append("")

    # Severity breakdown (only if findings exist)
    if findings:
        sev_counts: dict[str, int] = {}
        for f in findings:
            s = f.get("severity", "unknown")
            sev_counts[s] = sev_counts.get(s, 0) + 1
        sections += [
            "**Severity breakdown:** " + " · ".join(f"{s}={c}" for s, c in sorted(sev_counts.items())),
            "",
        ]

    sections += [
        "## Key Decisions",
        "",
        "## Debrief",
        "",
        "---",
        "",
        f"*Tracker-anchored engagement note. Last refreshed by `rick_tracker` on {today}.*",
        "",
    ]
    return "\n".join(sections)


def _refresh_tracker_vault_note(eng_data: dict) -> str | None:
    """Refresh the vault projection for a tracker-anchored engagement note.

    Always overwrites — the JSON state is canonical, the vault note is the projection.
    Returns the vault-relative path (str) on success, or None if vault is not configured.
    """
    if not vault._is_configured():
        return None
    eng_id = eng_data.get("id", "ENG-UNKNOWN")
    client = str(eng_data.get("client", "[CLIENT]"))
    eng_type = str(eng_data.get("type", "pentest"))
    body = _tracker_vault_body(eng_data)
    result = vault.write_engagement(
        eng_id,
        client=client,
        engagement_type=eng_type,
        body=body,
        status=str(eng_data.get("status", "active")),
        overwrite=True,
    )
    if result is None:
        return None
    written_path, _ = result
    return vault.relative_path(written_path)


def _debrief_vault_section(params: DebriefInput, findings_list: list[str]) -> str:
    """Build the Debrief section body for appending to an existing engagement note."""
    operator_link = f"[[Identity/{NAME}]]"
    sections = [
        f"**Engagement type:** {params.engagement_type.replace('_', ' ').title()}",
        f"**Operator:** {operator_link}",
        f"**Closing voice:** {MOTTO + '. ' if MOTTO else ''}_The work isn't done until the fixes are verified._",
        "",
        "### Key Findings",
        "",
        _bullet_list(findings_list),
        "",
        "### Lessons Learned",
        "",
        "**What worked:** _[techniques/tools that landed; client controls that held]_",
        "",
        "**What didn't:** _[detected/blocked techniques; scope or access friction]_",
        "",
        "**Surprises:** _[unexpected findings — good or bad]_",
        "",
        "### Remediation Priorities",
        "",
        "- **Immediate (0-7d):** Critical findings requiring emergency response",
        "- **Short-term (7-30d):** High findings with clear remediation paths",
        "- **Medium-term (30-90d):** Medium findings + hardening",
        "- **Strategic (90d+):** Architectural changes",
        "",
        "### Retest",
        "",
        "Recommended 90 days after remediation of critical/high findings. Focused retest on remediated "
        "findings + regression. Verify fixes are effective and haven't introduced new issues.",
        "",
    ]
    return "\n".join(sections)


def _scoping_vault_section(params: ScopingInput, total_hours: int, total_days: int, total_estimate: int) -> str:
    """Build the Scoping section body."""
    return "\n".join(
        [
            f"**Engagement type:** {params.engagement_type.replace('_', ' ').title()}",
            f"**Targets:** {params.target_count}",
            f"**Complexity:** {(params.complexity or 'medium')}",
            f"**Estimated hours:** {total_hours}",
            f"**Estimated days:** {total_days}",
            f"**Estimated cost:** ${total_estimate:,} (senior pentester day rate)",
            "",
            "_Estimates only. Pad 20% for the unexpected. The builder who underestimates the foundation pays for it on the roof._",
            "",
            "Source: `rick_scoping` calculator.",
        ]
    )


def _roe_vault_section(params: ROEInput) -> str:
    """Build the ROE section body."""
    return "\n".join(
        [
            f"**Engagement type:** {params.engagement_type.replace('_', ' ').title()}",
            f"**Client:** {params.client_name}",
            f"**Duration:** {params.duration_days} business days",
            "",
            "**Authorization:** Written required before testing. Detailed scope signed by both parties. "
            "24/7 emergency contact required.",
            "",
            "**Rules:**",
            "",
            _bullet_list(
                [
                    "Testing confined to authorized scope",
                    "No DoS without written approval",
                    "No social engineering of non-approved targets",
                    "No modification of production data",
                    "PoC-level data handling only",
                    "All findings documented with timestamps",
                    "Critical findings reported immediately",
                    "Testing paused if unintended impact",
                ]
            ),
            "",
            "**Standards:** PTES, OWASP Testing Guide, NIST SP 800-115.",
            "",
            "Source: `rick_roe`. Scope is legal protection. No ambiguity. Measure twice, cut once.",
        ]
    )


def _onboarding_vault_section(client: str, engagement_type: str) -> str:
    """Build the Onboarding section body."""
    return "\n".join(
        [
            f"**Client:** {client}",
            f"**Engagement type:** {engagement_type.replace('_', ' ').title()}",
            "",
            "**Authorization checklist:** Signed SOW · Written authorization letter · Scope agreed · Get-out-of-jail "
            "letter (if on-site)",
            "",
            "**Technical checklist:** Target list (URLs/IPs/domains) · Credentials (if gray/white) · VPN/connectivity "
            "· Architecture diagrams · Previous reports · Fragile/off-limits systems",
            "",
            "**Contacts:** Technical POC · Executive escalation · Emergency contact · Preferred comms channel",
            "",
            "**Scheduling:** Testing window confirmed · Blackout periods · Kick-off scheduled · Report delivery date",
            "",
            "Source: `rick_client_onboarding`. Good onboarding sets the tone. Preparation prevents poor performance.",
        ]
    )


def _find_matching_engagement(client: str, engagement_type: str) -> str | None:
    """Best-effort lookup: find an existing vault engagement codename matching client+type prefix.

    Returns the codename (filename stem) of the most recent match, or None if no vault / no match.
    Pattern: '<Client> - <Type Title> (<Date>).md'
    """
    if not vault._is_configured():
        return None
    type_title = engagement_type.replace("_", " ").title()
    prefix = f"{client} - {type_title}"
    candidates = [p for p in vault.list_engagements() if p.stem.startswith(prefix)]
    if not candidates:
        return None
    # Sort by mtime desc — most recent first
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0].stem


async def rick_roe(params: ROEInput) -> str:
    """Generate ROE documents. Scope, authorization, escalation, deliverables."""
    ts = datetime.now().strftime("%Y-%m-%d")
    roe = {
        "header": {
            "title": f"ROE — {params.engagement_type.replace('_', ' ').title()}",
            "client": _sanitize(params.client_name),
            "prepared_by": CALLSIGN,
            "date": ts,
            "duration": f"{params.duration_days} business days",
        },
        "authorization": {
            "requirement": "Written authorization before testing",
            "scope": "Detailed scope signed by both parties",
            "emergency": "24/7 emergency contact required",
        },
        "rules": [
            "Testing confined to authorized scope",
            "No DoS without written approval",
            "No social engineering of non-approved targets",
            "No modification of production data",
            "PoC-level data handling only",
            "All findings documented with timestamps",
            "Critical findings reported immediately",
            "Testing paused if unintended impact",
        ],
        "escalation": {
            "critical": "Notify tech POC within 1 hour",
            "impact": "Halt testing, notify all contacts",
            "data_exposure": "Document, do not exfiltrate, notify",
        },
        "deliverables": [
            "Executive Summary",
            "Technical Report",
            "Remediation Roadmap",
            "Evidence Package",
            "Debrief Presentation",
        ],
        "standards": "PTES, OWASP Testing Guide, NIST SP 800-115",
        "rick_note": f"{params.duration_days} days planned. Build in 20% buffer for documentation. Thorough > fast.",
    }

    # ── Vault integration: append ROE section to matching engagement note ────────────────
    if vault._is_configured():
        client_str = _sanitize(params.client_name) or "Client"
        codename = _find_matching_engagement(client_str, params.engagement_type)
        if codename:
            written = vault.append_engagement_section(
                codename, section_heading="Rules of Engagement", section_body=_roe_vault_section(params)
            )
            if written is not None:
                roe["vault_path"] = vault.relative_path(written)
                roe["vault_status"] = "ROE appended"
                vault.append_log_entry("roe", f"Appended to [[Engagements/{codename}]] (client: {client_str})")
        else:
            roe["vault_status"] = "no matching engagement note found — text-only output"
    return _fmt(roe, params.response_format, title=f"{CALLSIGN} Rules of Engagement")


async def rick_report_template(params: ReportInput) -> str:
    """Generate pentest report section templates. PlexTrac-compatible."""
    sev = {
        "critical": "RED CRITICAL",
        "high": "ORANGE HIGH",
        "medium": "YELLOW MEDIUM",
        "low": "BLUE LOW",
        "informational": "INFO",
    }
    tmpl: dict[str, dict[str, object]] = {
        "executive_summary": {
            "section": "Executive Summary",
            "structure": [
                "Engagement Overview",
                "Scope Summary",
                "Key Findings (critical/high + business impact)",
                "Overall Risk Rating",
                "Top 3-5 Recommendations",
                "Positive Observations",
            ],
            "rick_note": "C-suite only. No jargon. Business impact, not technical show-off.",
        },
        "finding": {
            "section": "Finding",
            "title": params.finding_title or "[TITLE]",
            "severity": sev.get((params.severity or "").lower(), "[SEVERITY]"),
            "template": {
                "title": params.finding_title or "[Title]",
                "severity_cvss": "[X.X]",
                "cwe": "[CWE-XXX]",
                "asset": "[URL/IP]",
                "description": params.description or "[Explanation]",
                "business_impact": "[What attacker could DO]",
                "poc": "[Steps + screenshots]",
                "remediation": "[Actionable fix]",
                "references": "[OWASP, CVE]",
            },
            "rick_note": "Every finding needs PoC and actionable remediation. Report like a building inspector — severity, location, impact, fix.",
        },
        "methodology": {
            "section": "Methodology",
            "phases": MISSION_PHASES,
            "standards": ["OWASP v4", "PTES", "NIST 800-115", "OWASP API Top 10", "MITRE ATT&CK"],
            "rick_note": "Shows structured, repeatable process. Craftsmanship is visible in methodology.",
        },
        "scope": {
            "section": "Scope",
            "template": {
                "in_scope": "[Targets]",
                "out_of_scope": "[Exclusions]",
                "window": "[Start-End+TZ]",
                "type": "[Black/Gray/White]",
                "credentials": "[Y/N]",
                "restrictions": "[Specific]",
                "contacts": "[Tech+Emergency]",
            },
            "rick_note": "Scope is legal protection. No ambiguity. Measure twice, cut once.",
        },
        "remediation": {
            "section": "Remediation Roadmap",
            "tiers": {
                "immediate_0_30d": "Critical+High",
                "short_30_90d": "Medium+Hardening",
                "long_90d_plus": "Strategic+Architectural",
                "quick_wins": "Low-effort high-impact",
            },
            "prioritization": "Severity x Exploitability x Business Impact",
            "rick_note": "This is where you provide real value. Don't just say it's broken — hand them the blueprint.",
        },
        "appendix": {
            "section": "Appendix",
            "contents": [
                "Tool list+versions",
                "Scanner output (sanitized)",
                "Screenshots/evidence",
                "Network diagrams",
                "Tested endpoints",
                "Credential handling docs",
                "Glossary",
            ],
            "rick_note": "Evidence chain of custody. Courts care about this. Military-grade documentation.",
        },
    }
    s = params.section.lower().strip()
    t = tmpl.get(s)
    if not t:
        return f"Error: Unknown section '{s}'. Available: {', '.join(tmpl.keys())}"
    return _fmt(t, params.response_format, title=f"{CALLSIGN} Report Template")  # type: ignore[arg-type]


async def rick_engagement_proposal(params: ProposalInput) -> str:
    """Generate SOW/proposal for 7 engagement types. Scope, methodology, timeline, deliverables."""
    ts = datetime.now().strftime("%Y-%m-%d")
    et = params.engagement_type.lower().strip()
    dm: dict[str, dict[str, object]] = {
        "web_app_pentest": {
            "t": "Web App Pentest",
            "s": "Web application auth, session, input validation, business logic, APIs.",
            "tech": ["OWASP methodology", "Burp Suite manual testing", "BOLA/IDOR testing", "Business logic analysis"],
            "rd": 10,
            "tt": "Gray Box",
        },
        "network_pentest": {
            "t": "Network Pentest",
            "s": "Internal/external network infrastructure.",
            "tech": [
                "Full port scanning",
                "Service enumeration",
                "Exploitation + lateral movement",
                "Credential harvesting",
            ],
            "rd": 10,
            "tt": "Black/Gray Box",
        },
        "ad_review": {
            "t": "AD Security Review",
            "s": "Active Directory config, GPOs, trusts, privesc paths.",
            "tech": ["BloodHound", "Kerberoasting/AS-REP", "ADCS (ESC1-ESC8)", "Trust analysis"],
            "rd": 8,
            "tt": "Gray Box",
        },
        "cloud_audit": {
            "t": "Cloud Security Assessment",
            "s": "Azure/AWS IAM, storage, network, compliance.",
            "tech": ["IAM analysis", "Storage permissions", "Network config", "CIS benchmarks"],
            "rd": 8,
            "tt": "Gray Box",
        },
        "red_team": {
            "t": "Red Team Engagement",
            "s": "Adversary simulation across full attack lifecycle.",
            "tech": ["MITRE ATT&CK ops", "Initial access development", "C2 infrastructure", "Purple team debrief"],
            "rd": 20,
            "tt": "Black Box",
        },
        "api_security": {
            "t": "API Security Assessment",
            "s": "REST/GraphQL auth, authorization, input validation, business logic.",
            "tech": ["OWASP API Top 10", "BOLA/IDOR", "Auth analysis", "Rate limiting"],
            "rd": 7,
            "tt": "Gray Box",
        },
        "full_scope": {
            "t": "Full-Scope Assessment",
            "s": "Web apps + network + AD + cloud.",
            "tech": ["Network testing", "Web assessment", "AD review", "Cloud audit"],
            "rd": 25,
            "tt": "Gray Box",
        },
    }
    d = dm.get(et)
    if not d:
        return f"Error: Unknown type '{et}'. Available: {', '.join(dm.keys())}"
    default_days = d["rd"]
    assert isinstance(default_days, int)
    days: int = params.estimated_days or default_days
    p = {
        "header": {"title": f"Proposal: {d['t']}", "client": _sanitize(params.client_name), "by": CALLSIGN, "date": ts},
        "summary": f"{d['t']} for {params.client_name}, {days} business days, PTES/OWASP/ATT&CK methodology.",
        "scope": {"description": d["s"], "type": d["tt"], "in_scope": "[TBD]", "out_of_scope": "[TBD]"},
        "methodology": {
            "framework": "PTES + OWASP + MITRE ATT&CK",
            "phases": [m["name"] for m in MISSION_PHASES],
            "techniques": d["tech"],
        },
        "timeline": {
            "total": f"{days}d",
            "recon": f"{max(1, days // 5)}d",
            "testing": f"{max(1, int(days * 0.5))}d",
            "exploitation": f"{max(1, int(days * 0.2))}d",
            "reporting": f"{max(1, int(days * 0.2))}d",
        },
        "deliverables": ["Executive Summary", "Technical Report", "Remediation Roadmap", "Evidence Package", "Debrief"],
        "terms": {"auth": "Written required", "scope": "Authorized only", "data": "PoC-level", "escalation": "1 hour"},
    }
    if params.special_requirements:
        p["special_requirements"] = params.special_requirements
    p["rick_note"] = f"Recommended: {d['rd']}d. Requested: {days}d. Thorough > fast. Measure twice, cut once."

    # ── Vault integration: write the engagement note when vault is configured ─────────────
    if vault._is_configured():
        client_str = _sanitize(params.client_name) or "Client"
        codename = vault.codename_for(client_str, et, date=ts)
        body = _proposal_vault_body(
            client=client_str,
            engagement_type=et,
            type_title=str(d["t"]),
            scope_desc=str(d["s"]),
            test_type=str(d["tt"]),
            techniques=list(d["tech"]),  # type: ignore[call-overload]
            days=days,
            recommended_days=int(default_days),
            special_requirements=params.special_requirements,
        )
        result = vault.write_engagement(codename, client=client_str, engagement_type=et, body=body, status="scoping")
        if result is not None:
            written_path, created = result
            p["vault_path"] = vault.relative_path(written_path)
            p["vault_status"] = "created" if created else "preserved (existing note untouched)"
            if created:
                vault.append_log_entry(
                    "engagement",
                    f"Proposal anchor created: [[Engagements/{codename}]] (client: {client_str}, type: {et}, {days}d)",
                )
    return _fmt(p, params.response_format, title=f"{CALLSIGN} Proposal")


async def rick_client_onboarding(params: OnboardInput) -> str:
    """Generate client onboarding packet. Checklists, ground rules, FAQ, comms protocol."""
    pk = {
        "header": {
            "engagement": f"Onboarding — {params.client_name}",
            "type": (params.engagement_type or "pentest").replace("_", " ").title(),
            "assessor": CALLSIGN,
        },
        "checklist_authorization": [
            "Signed SOW",
            "Written authorization letter",
            "Scope document agreed",
            "Get-out-of-jail letter (if on-site)",
        ],
        "checklist_technical": [
            "Target list (URLs, IPs, domains)",
            "Credentials (if gray/white box)",
            "VPN/connectivity",
            "Architecture diagrams",
            "Previous reports",
            "Fragile/off-limits systems",
        ],
        "checklist_contacts": ["Technical POC", "Executive escalation", "Emergency contact", "Preferred comms channel"],
        "checklist_scheduling": [
            "Testing window confirmed",
            "Blackout periods",
            "Kick-off scheduled",
            "Report delivery date",
        ],
        "communication": {
            "cadence": "Kick-off > milestones > critical alerts > report delivery",
            "approach": "7-phase methodology, automated + manual",
            "reporting": "Executive briefs + technical findings + remediation roadmaps",
        },
        "ground_rules": {
            "scope": "Authorized only",
            "data": "PoC-level, securely deleted",
            "availability": "No DoS without approval",
            "findings": "Honest, not inflated",
            "confidentiality": "All findings confidential",
        },
        "faq": {
            "duration": "Web: 7-10d, Network: 8-12d, Full: 20-30d",
            "impact": "Zero production impact goal",
            "critical": "Immediate notification",
            "scope_changes": "Documented before expanding",
        },
        "next_steps": [
            "1. Complete checklists",
            "2. Schedule kick-off",
            "3. Provide access",
            "4. Confirm window",
            f"5. Execute. {MOTTO + '.' if MOTTO else 'Get after it.'}",
        ],
        "rick_note": "Good onboarding sets the tone. Preparation prevents poor performance. Measure twice, cut once.",
    }

    # ── Vault integration: append Onboarding section to matching engagement note ──────────
    if vault._is_configured():
        client_str = _sanitize(params.client_name) or "Client"
        eng_type = params.engagement_type or "pentest"
        codename = _find_matching_engagement(client_str, eng_type)
        if codename:
            written = vault.append_engagement_section(
                codename,
                section_heading="Client Onboarding",
                section_body=_onboarding_vault_section(client_str, eng_type),
            )
            if written is not None:
                pk["vault_path"] = vault.relative_path(written)
                pk["vault_status"] = "onboarding appended"
                vault.append_log_entry("onboarding", f"Appended to [[Engagements/{codename}]] (client: {client_str})")
        else:
            pk["vault_status"] = "no matching engagement note found — text-only output"
    return _fmt(pk, params.response_format, title=f"{CALLSIGN} Client Onboarding")


async def rick_debrief(params: DebriefInput) -> str:
    """Post-engagement debrief template. Lessons learned, what worked, what didn't, recommendations for next cycle."""
    ts = datetime.now().strftime("%Y-%m-%d")
    findings_list = (
        [f.strip() for f in params.key_findings.split(",")]
        if params.key_findings
        else ["[Finding 1]", "[Finding 2]", "[Finding 3]"]
    )

    debrief = {
        "header": {
            "title": f"Post-Engagement Debrief — {params.engagement_type.replace('_', ' ').title()}",
            "client": _sanitize(params.client_name),
            "assessor": CALLSIGN,
            "date": ts,
        },
        "executive_summary": {
            "engagement_type": params.engagement_type.replace("_", " ").title(),
            "overall_risk": "[Critical / High / Medium / Low]",
            "total_findings": "[Count by severity]",
            "key_findings": findings_list,
            "positive_observations": "[What the client does well — always acknowledge good security]",
        },
        "attack_narrative": {
            "description": "Tell the story of the engagement — how the attack unfolded",
            "structure": [
                "Initial access — how we got in (or couldn't)",
                "Escalation path — how we moved from foothold to objective",
                "Critical chains — the finding combinations that create real risk",
                "What stopped us — controls that worked",
                "Time to compromise — how long each phase took",
            ],
        },
        "lessons_learned": {
            "what_worked": [
                "[Techniques/tools that were effective]",
                "[Client controls that were strong]",
                "[Communication that went well]",
            ],
            "what_didnt": [
                "[Techniques that were detected/blocked]",
                "[Scope issues or access problems]",
                "[Time constraints]",
            ],
            "surprises": "[Unexpected findings — good or bad]",
            "methodology_improvements": "[What we'd do differently next time]",
        },
        "remediation_priorities": {
            "immediate_0_7d": "Critical findings requiring emergency response",
            "short_term_7_30d": "High findings with clear remediation path",
            "medium_term_30_90d": "Medium findings and hardening improvements",
            "strategic_90d_plus": "Architectural changes and long-term security improvements",
        },
        "retest_recommendations": {
            "when": "Recommended 90 days after remediation of critical/high findings",
            "scope": "Focused retest on remediated findings + regression testing",
            "approach": "Verify fixes are effective and haven't introduced new issues",
        },
        "next_engagement": {
            "recommendations": [
                "Areas not covered in this engagement that should be tested",
                "New attack surfaces identified during testing",
                "Purple team exercise to validate detection capabilities",
                "Specific technology deep-dives based on findings",
            ],
        },
        "closing": f"Engagement complete. Findings documented. Remediation roadmap delivered. Standing by for questions and retest scheduling. {MOTTO + '. ' if MOTTO else ''}— {CALLSIGN}",
        "rick_note": "The debrief is where you prove you're a partner, not just a tester. Tell the story. Acknowledge what they do well. Make the remediation actionable. And always recommend a retest — the work isn't done until the fixes are verified.",
    }

    # ── Vault integration: append Debrief section to matching engagement note ────────────
    if vault._is_configured():
        client_str = _sanitize(params.client_name) or "Client"
        codename = _find_matching_engagement(client_str, params.engagement_type)
        if codename:
            section_body = _debrief_vault_section(params, findings_list)
            written = vault.append_engagement_section(codename, section_heading="Debrief", section_body=section_body)
            if written is not None:
                debrief["vault_path"] = vault.relative_path(written)
                debrief["vault_status"] = "debrief appended"
                vault.append_log_entry("debrief", f"Appended to [[Engagements/{codename}]] (client: {client_str})")
        else:
            debrief["vault_status"] = "no matching engagement note found — text-only output"
    return _fmt(debrief, params.response_format, title=f"{CALLSIGN} Debrief")


async def rick_tracker(params: TrackerInput) -> str:
    """Track engagements and findings. Create, update, and export engagement data."""

    data_dir = Path.home() / ".rick_mcp" / "engagements"
    data_dir.mkdir(parents=True, exist_ok=True)

    action = (_sanitize(params.action) or "").lower()
    engagement_id = _sanitize(params.engagement_id)

    if action == "create":
        # Parse engagement data
        try:
            eng_data = json.loads(params.data or "{}")
        except json.JSONDecodeError:
            return "Error: Invalid JSON in data field."

        eng_id = eng_data.get("id") or datetime.now().strftime("ENG-%Y%m%d-%H%M%S")
        engagement = {
            "id": eng_id,
            "client": _sanitize(eng_data.get("client", "[CLIENT]")),
            "type": eng_data.get("type", "pentest"),
            "start_date": eng_data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
            "end_date": eng_data.get("end_date", "TBD"),
            "status": "active",
            "findings": [],
            "created_at": datetime.now().isoformat(),
        }

        eng_file = data_dir / f"{eng_id}.json"
        eng_file.write_text(json.dumps(engagement, indent=2))
        logger.info(f"Engagement created: {eng_id}")

        response: dict = {"engagement_created": eng_id, **engagement}

        # ── Vault projection: write/refresh the eng_id-anchored note ──────────────
        vault_path = _refresh_tracker_vault_note(engagement)
        if vault_path:
            response["vault_path"] = vault_path
            vault.append_log_entry(
                "tracker", f"Engagement created: [[Engagements/{eng_id}]] (client: {engagement['client']})"
            )

        return _fmt(response, params.response_format, title=f"{CALLSIGN} Engagement Created")

    elif action == "add_finding":
        if not engagement_id:
            return "Error: engagement_id required for add_finding."

        eng_file = data_dir / f"{engagement_id}.json"
        if not eng_file.exists():
            return f"Error: Engagement '{engagement_id}' not found."

        try:
            finding_data = json.loads(params.data or "{}")
        except json.JSONDecodeError:
            return "Error: Invalid JSON in data field."

        engagement = json.loads(eng_file.read_text())
        finding = {
            "id": f"F-{len(engagement['findings']) + 1:03d}",
            "title": _sanitize(finding_data.get("title", "[UNTITLED]")),
            "severity": finding_data.get("severity", "medium"),
            "status": finding_data.get("status", "open"),
            "added_at": datetime.now().isoformat(),
        }
        engagement["findings"].append(finding)
        eng_file.write_text(json.dumps(engagement, indent=2))
        logger.info(f"Finding added to {engagement_id}: {finding['id']}")

        response = {
            "finding_added": finding,
            "engagement": engagement_id,
            "total_findings": len(engagement["findings"]),
        }

        # ── Vault projection: refresh the eng_id-anchored note with new finding ──
        vault_path = _refresh_tracker_vault_note(engagement)
        if vault_path:
            response["vault_path"] = vault_path
            vault.append_log_entry(
                "tracker",
                f"Finding {finding['id']} added to [[Engagements/{engagement_id}]] (severity: {finding['severity']})",
            )

        return _fmt(response, params.response_format, title=f"{CALLSIGN} Finding Added")

    elif action == "update_finding":
        if not engagement_id:
            return "Error: engagement_id required for update_finding."

        eng_file = data_dir / f"{engagement_id}.json"
        if not eng_file.exists():
            return f"Error: Engagement '{engagement_id}' not found."

        try:
            update_data = json.loads(params.data or "{}")
        except json.JSONDecodeError:
            return "Error: Invalid JSON in data field."

        finding_id = update_data.get("finding_id")
        if not finding_id:
            return "Error: finding_id required in data."

        engagement = json.loads(eng_file.read_text())
        updated = False
        for finding in engagement["findings"]:
            if finding["id"] == finding_id:
                if "status" in update_data:
                    finding["status"] = update_data["status"]
                if "severity" in update_data:
                    finding["severity"] = update_data["severity"]
                if "title" in update_data:
                    finding["title"] = _sanitize(update_data["title"])
                finding["updated_at"] = datetime.now().isoformat()
                updated = True
                break

        if not updated:
            return f"Error: Finding '{finding_id}' not found in engagement '{engagement_id}'."

        eng_file.write_text(json.dumps(engagement, indent=2))
        logger.info(f"Finding updated in {engagement_id}: {finding_id}")

        response = {"finding_updated": finding_id, "engagement": engagement_id}

        # ── Vault projection: refresh the eng_id-anchored note ──────────────────
        vault_path = _refresh_tracker_vault_note(engagement)
        if vault_path:
            response["vault_path"] = vault_path

        return _fmt(response, params.response_format, title=f"{CALLSIGN} Finding Updated")

    elif action == "status":
        if not engagement_id:
            # List all engagements
            engagements = []
            for f in sorted(data_dir.glob("*.json")):
                eng = json.loads(f.read_text())
                severity_counts: dict[str, int] = {}
                for finding in eng.get("findings", []):
                    sev = finding.get("severity", "unknown")
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1
                engagements.append(
                    {
                        "id": eng["id"],
                        "client": eng.get("client", "Unknown"),
                        "type": eng.get("type", "Unknown"),
                        "status": eng.get("status", "Unknown"),
                        "findings": len(eng.get("findings", [])),
                        "severity_breakdown": severity_counts,
                    }
                )

            if not engagements:
                return "No engagements found. Use action='create' to start one."

            return _fmt(
                {"engagements": engagements, "total": len(engagements)},
                params.response_format,
                title=f"{CALLSIGN} Engagement Overview",
            )

        eng_file = data_dir / f"{engagement_id}.json"
        if not eng_file.exists():
            return f"Error: Engagement '{engagement_id}' not found."

        engagement = json.loads(eng_file.read_text())
        severity_counts = {}
        status_counts: dict[str, int] = {}
        for finding in engagement.get("findings", []):
            sev = finding.get("severity", "unknown")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            st = finding.get("status", "unknown")
            status_counts[st] = status_counts.get(st, 0) + 1

        return _fmt(
            {
                **engagement,
                "finding_count": len(engagement.get("findings", [])),
                "severity_breakdown": severity_counts,
                "status_breakdown": status_counts,
            },
            params.response_format,
            title=f"{CALLSIGN} Engagement Status",
        )

    elif action == "export":
        if not engagement_id:
            return "Error: engagement_id required for export."

        eng_file = data_dir / f"{engagement_id}.json"
        if not eng_file.exists():
            return f"Error: Engagement '{engagement_id}' not found."

        return eng_file.read_text()

    elif action == "export_csv":
        if not engagement_id:
            return "Error: engagement_id required for export_csv."

        eng_file = data_dir / f"{engagement_id}.json"
        if not eng_file.exists():
            return f"Error: Engagement '{engagement_id}' not found."

        eng = json.loads(eng_file.read_text())
        findings = eng.get("findings", [])
        lines = ["id,title,severity,status,added_at"]
        for f in findings:
            lines.append(
                f"{f.get('id', '')},{f.get('title', '')},{f.get('severity', '')},{f.get('status', '')},{f.get('added_at', '')}"
            )
        return "\n".join(lines)

    elif action == "export_markdown":
        if not engagement_id:
            return "Error: engagement_id required for export_markdown."

        eng_file = data_dir / f"{engagement_id}.json"
        if not eng_file.exists():
            return f"Error: Engagement '{engagement_id}' not found."

        eng = json.loads(eng_file.read_text())
        findings = eng.get("findings", [])
        lines = [
            f"# Engagement Report: {eng.get('id', engagement_id)}",
            f"**Client**: {eng.get('client', '[CLIENT]')}",
            f"**Status**: {eng.get('status', 'unknown')}",
            f"**Created**: {eng.get('created_at', 'N/A')}",
            "",
            "## Findings",
            "",
            "| ID | Title | Severity | Status |",
            "|----|-------|----------|--------|",
        ]
        for f in findings:
            lines.append(
                f"| {f.get('id', '')} | {f.get('title', '')} | {f.get('severity', '')} | {f.get('status', '')} |"
            )
        if not findings:
            lines.append("| — | No findings recorded | — | — |")
        lines.append("")
        lines.append(f"**Total findings**: {len(findings)}")
        return "\n".join(lines)

    else:
        return f"Error: Unknown action '{action}'. Available: create, add_finding, update_finding, status, export, export_csv, export_markdown"


async def rick_scoping(params: ScopingInput) -> str:
    """Engagement scoping calculator. Hours, team size, rate card, timeline — the business side of breaking things."""
    base_hours = {
        "web_app_pentest": {"base": 40, "description": "Web Application Penetration Test"},
        "network_pentest": {"base": 60, "description": "Network Infrastructure Penetration Test"},
        "ad_review": {"base": 80, "description": "Active Directory Security Review"},
        "cloud_audit": {"base": 60, "description": "Cloud Security Audit"},
        "red_team": {"base": 160, "description": "Red Team Engagement"},
        "api_security": {"base": 30, "description": "API Security Assessment"},
        "full_scope": {"base": 240, "description": "Full Scope Penetration Test"},
    }
    complexity_factors = {"low": 0.75, "medium": 1.0, "high": 1.5}

    et = params.engagement_type.lower().strip()
    scope = base_hours.get(et)
    if not scope:
        return f"Error: Unknown engagement type '{et}'. Available: {', '.join(base_hours.keys())}"

    complexity = (params.complexity or "medium").lower().strip()
    factor = complexity_factors.get(complexity, 1.0)

    base = scope["base"]
    total_hours = int(base * params.target_count * factor)  # type: ignore[operator]
    team_size = max(1, total_hours // 80)  # ~80 hours per person per engagement
    day_rate = 2400  # industry standard for senior pentester
    total_days = max(1, total_hours // 8)
    total_estimate = total_days * day_rate

    result = {
        "engagement_type": scope["description"],
        "targets": params.target_count,
        "complexity": complexity,
        "estimated_hours": total_hours,
        "estimated_days": total_days,
        "team_size": f"{team_size} operator{'s' if team_size > 1 else ''}",
        "rate_card": {
            "day_rate": f"${day_rate:,}/day (senior pentester)",
            "total_estimate": f"${total_estimate:,}",
            "note": "Rates are estimates — final pricing depends on scope specifics, travel, and tooling requirements.",
        },
        "deliverable_timeline": {
            "kickoff": "Day 1 — Scope validation, credential handoff, comms setup",
            "testing": f"Days 2-{max(2, total_days - 5)} — Active testing phase",
            "draft_report": f"Day {max(3, total_days - 4)} — Draft report delivery",
            "client_review": f"Days {max(4, total_days - 3)}-{max(5, total_days - 1)} — Client review period",
            "final_report": f"Day {total_days} — Final report with remediation guidance",
            "debrief": f"Day {total_days + 3} — Executive debrief and technical walkthrough",
        },
        "phases_breakdown": [
            {"phase": p["name"], "allocation": f"{int(total_hours * w)}h"}
            for p, w in zip(
                MISSION_PHASES,
                [0.15, 0.20, 0.25, 0.10, 0.10, 0.10, 0.10],
                strict=False,
            )
        ],
        "rick_note": "These are estimates, not bids. Every engagement is different — complexity, target maturity, and scope creep all affect the final number. Always pad 20% for the unexpected. The builder who underestimates the foundation pays for it on the roof.",
    }

    # ── Vault integration: log calculator run (no client→note matching available here) ──
    if vault._is_configured():
        vault.append_log_entry(
            "scoping",
            f"Calculator run — type: {et}, targets: {params.target_count}, complexity: {complexity}, "
            f"hours: {total_hours}, days: {total_days}, est: ${total_estimate:,}",
        )
        result["vault_status"] = "calculator run logged to vault/log.md"
    return _fmt(result, params.response_format, title=f"{CALLSIGN} Engagement Scoping")


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_roe",
        annotations={
            "title": "Rules of Engagement Generator",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_roe))
    mcp.tool(
        name="rick_report_template",
        annotations={
            "title": "Report Template Generator",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_report_template))
    mcp.tool(
        name="rick_engagement_proposal",
        annotations={
            "title": "Engagement Proposal Generator",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_engagement_proposal))
    mcp.tool(
        name="rick_client_onboarding",
        annotations={
            "title": "Client Onboarding Packet",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_client_onboarding))
    mcp.tool(
        name="rick_debrief",
        annotations={
            "title": "Post-Engagement Debrief",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_debrief))
    mcp.tool(
        name="rick_tracker",
        annotations={
            "title": "Engagement Tracker",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_tracker))
    mcp.tool(
        name="rick_scoping",
        annotations={
            "title": "Engagement Scoping Calculator",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_scoping))
