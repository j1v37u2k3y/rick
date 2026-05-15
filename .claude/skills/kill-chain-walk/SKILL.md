---
name: kill-chain-walk
description: >
  Phase-by-phase guided offensive operation. Reads stateful kill-chain position via
  rick_kill_chain, routes to the right rick_mcp tools for the current phase, asks
  AskUserQuestion at every decision point, logs each move via rick_kill_chain findings.
  Use this skill for active engagement work: "advance the kill chain", "what's next on
  <engagement>", "walk me through phase X", "continue <engagement>", "/kill-chain-walk", or
  any session that resumes work on an active engagement. Works for both client engagements
  (kicked off via /engagement-kickoff) and CTF/HTB engagements (via /htb-day). State persists
  in the MCP server across sessions — picks up where the last walk left off. Not for
  engagement startup (use /engagement-kickoff or /htb-day) or close-out (use
  /debrief-then-publish).
---

# Kill Chain Walk

> Seven phases — Reconnaissance, Vulnerability Assessment, Exploitation, Privilege
> Escalation, Lateral Movement, Documentation, Remediation Strategy. Each phase has its
> own toolset, decision points, and logging discipline. The skill orchestrates; the
> operator drives the keyboard. State persists in `rick_kill_chain` so the walk resumes
> clean across sessions.

---

## Prerequisites

`rick_mcp` MCP server connected. Engagement must already exist (kicked off via
`/engagement-kickoff` or `/htb-day`). Skill calls a wide tool surface — load schemas as
needed per phase:

**Always used:**
- `mcp__rick_mcp__rick_kill_chain` — state + findings (the spine)
- `mcp__rick_mcp__rick_sitrep` — current tactical picture
- `mcp__rick_mcp__rick_next_move` — phase-aware next action

**Per phase:**
- Phase 1: `rick_recon`, `rick_cve`, `rick_recon_handle`
- Phase 2: `rick_vuln_assess`, `rick_threat_model`
- Phase 3: `rick_payload_guide`, `rick_cheatsheet`, `rick_attack_chain`
- Phase 4: `rick_payload_guide` (privesc), `rick_next_move` with `current_position`
- Phase 5: `rick_pivot_plan`, `rick_cloud_attack_path`, `rick_attack_chain`
- Phase 6: `rick_report_template`, `rick_notes`, `rick_timeline`, `rick_export`
- Phase 7: `rick_hardening`, `rick_detection_rules`, `rick_rollback`

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **`engagement_id`** — the kill-chain handle. If not supplied, list active engagements via
   `rick_kill_chain({ action: "list" })` and let the operator pick.
2. **Walk mode** *(optional)*:
   - `resume` (default) — continue from current phase
   - `phase <N>` — jump to a specific phase (1–7), preserving prior findings
   - `replay` — re-walk the current phase from the top
3. **Session intent** *(optional, free text ≤ 200 chars)* — what the operator wants to
   accomplish this session. Feeds into `rick_next_move`.

---

## State model

Every walk step writes to the canonical surface:

**`rick_kill_chain` findings** — persists in the MCP server's state directory. Survives
sessions; any future operator picking up this `engagement_id` reads the live state.

Findings flow: action taken → result observed → `rick_kill_chain add_finding` with phase +
description. Never silent steps.

Phases (per the 7-phase methodology):

| # | Name                    | Primary tools                                          |
|---|-------------------------|--------------------------------------------------------|
| 1 | Reconnaissance          | rick_recon, rick_cve, rick_recon_handle                |
| 2 | Vulnerability Assessment| rick_vuln_assess, rick_threat_model                    |
| 3 | Exploitation            | rick_payload_guide(initial_access), rick_cheatsheet    |
| 4 | Privilege Escalation    | rick_payload_guide(persistence), rick_next_move        |
| 5 | Lateral Movement        | rick_pivot_plan, rick_cloud_attack_path, rick_attack_chain |
| 6 | Documentation           | rick_report_template, rick_notes, rick_timeline        |
| 7 | Remediation Strategy    | rick_hardening, rick_detection_rules                   |

---

## Workflow

### Step 0 — Load state

Resolve `engagement_id` (operator input or `rick_kill_chain action=list` picker).

```
mcp__rick_mcp__rick_sitrep({ params: { engagement_id: "<id>", response_format: "markdown" } })
```

Show the operator a tight summary: current phase, last finding, last action timestamp.
Confirm they want to proceed with the indicated phase, or pick a different phase.

### Step 1 — Phase router

Based on current phase (or operator-picked phase), jump to the matching sub-workflow below.
Every sub-workflow ends with the same close-out: write findings to `rick_kill_chain`, ask
whether to advance / pause / replay.

---

### Phase 1 — Reconnaissance

**Pre-check:** target_type determined? If not, `AskUserQuestion`: `web_app`, `network`,
`cloud_azure`, `cloud_aws`, `active_directory`, `api`, `container`, `mobile`.

```
mcp__rick_mcp__rick_recon({
  params: { target_type: "<picked>", scope_notes: "<engagement context>" }
})
```

For each recon technique: if it produces a concrete finding (port, endpoint, version banner,
public CVE), capture it. If a version is identified, call `rick_cve`.

**Decision point:** advance to Phase 2 / continue recon / pause.

### Phase 2 — Vulnerability Assessment

**Pre-check:** what vuln categories does recon suggest? Surface candidates.

```
mcp__rick_mcp__rick_vuln_assess({
  params: { vuln_category: "<one of 10>", context: "<target details>" }
})
```

Categories: `injection`, `auth`, `xss`, `ssrf`, `idor`, `file_upload`, `deserialization`,
`misconfig`, `crypto`, `privesc`.

Log finding per category tested (positive or negative).

**Decision point:** found a primitive — Phase 3 / more categories.

### Phase 3 — Exploitation

```
mcp__rick_mcp__rick_attack_chain({
  params: { scenario: "<external_to_da | phishing_to_lateral | web_to_internal | cloud_to_onprem | insider_threat | supply_chain>", target_environment: "<details>" }
})

mcp__rick_mcp__rick_payload_guide({
  params: { payload_type: "initial_access" }
})
```

If a specific tool reference is needed, route to `/cheatsheet-build`.

Log every exploit attempt with payload + target + observed result. If a screenshot exists,
pass `image_path` to `rick_kill_chain add_finding`.

**Decision point:** foothold confirmed — Phase 4 / pivot to alternate vuln.

### Phase 4 — Privilege Escalation

**Pre-check:** `current_position` — `linux_webserver`, `windows_workstation`,
`windows_server`, `container`, `cloud_instance`, `database_server`, `network_device`, or free
text.

```
mcp__rick_mcp__rick_next_move({
  params: {
    engagement_id: "<id>",
    current_position: "<picked>",
    findings_so_far: "<concatenated phase 1-3 highlights, ≤ 2000 chars>"
  }
})

mcp__rick_mcp__rick_payload_guide({
  params: { payload_type: "persistence" }
})
```

**Decision point:** root/SYSTEM — Phase 5 / stuck — re-run with updated findings.

### Phase 5 — Lateral Movement

```
mcp__rick_mcp__rick_pivot_plan({ ... })
```

If cloud env:

```
mcp__rick_mcp__rick_cloud_attack_path({ ... })
```

Re-call `rick_attack_chain` if scope expanded (new subnet, hybrid cloud).

**Decision point:** mission objective met — Phase 6 / more lateral.

### Phase 6 — Documentation

```
mcp__rick_mcp__rick_timeline({ params: { engagement_id: "<id>" } })
mcp__rick_mcp__rick_report_template({ ... })
mcp__rick_mcp__rick_notes({ ... })
mcp__rick_mcp__rick_export({ ... })
```

Generate the deliverable scaffolding. Operator fills the prose.

**Decision point:** report drafted — Phase 7 / pause for review.

### Phase 7 — Remediation Strategy

```
mcp__rick_mcp__rick_hardening({ ... })
mcp__rick_mcp__rick_detection_rules({ ... })
mcp__rick_mcp__rick_rollback({ ... })
```

Per finding, generate hardening guidance, detection rules (Sigma/YARA), rollback procedures.

**Close-out:** Walk done. Route to `/debrief-then-publish` for engagement close-out.

---

## Logging discipline (every phase)

After each meaningful step:

```
mcp__rick_mcp__rick_kill_chain({
  params: {
    action: "add_finding",
    engagement_id: "<id>",
    phase: <N>,
    finding: "<concise description of action + result>",
    image_path: "<optional screenshot path>"
  }
})
```

No silent steps. Negative findings are still data — log them too.

---

## Decision-point pattern (reusable)

Every phase ends with a 3-way `AskUserQuestion`:

| Option            | Action                                                        |
|-------------------|---------------------------------------------------------------|
| **Advance**       | `rick_kill_chain action=advance phase=<N+1>`                  |
| **More in phase** | Stay; surface next sub-step via `rick_next_move`              |
| **Pause**         | Log session-end finding: "Session pause — resume from `rick_sitrep`" |

Never advance without explicit operator confirmation. Phase advances are load-bearing.

---

## Acceptance criteria (per walk session)

- [ ] `rick_sitrep` ran at session start to load state
- [ ] Every action taken got a `rick_kill_chain add_finding` (no silent steps)
- [ ] Phase advances are explicit operator choices, not silent
- [ ] At session pause / end, final finding written with timestamp

---

## Failure modes

- **`engagement_id` doesn't exist** — `rick_kill_chain` returns not-found. Surface to
  operator; offer `/engagement-kickoff` or `/htb-day` instead.
- **Tool call mid-phase fails** — log the failure as a finding (negative result is still
  data). Ask: retry / pivot to alternate tool / pause.
- **Operator wants something the skill can't route** (manual web request, custom script) —
  encourage it. Log the manual action as a finding with `manual:` prefix. The skill
  orchestrates; the operator drives.
- **Phase decision deadlock** — call `rick_sitrep` again, present what's been done, surface
  `rick_next_move` recommendation as a tiebreaker.

---

## Voice

Operational. Terse logging. Honest assessments at every decision point. If a finding is
weak, log it as weak. If a phase advance feels premature, say so via `AskUserQuestion`.
No padding to look busy. For character, route through `/be_rick`.

---

## What this skill does NOT do

- Stand up a new engagement — `/engagement-kickoff` or `/htb-day`.
- Generate the final deliverable report — Phase 6 scaffolds; `/debrief-then-publish`
  finalizes.
- Sanitize / redact for public writeup — `/writeup-publish`.
- Run any tool that fires shell commands or network traffic — operator drives the keyboard.

---

## Related skills

- `/engagement-kickoff`, `/htb-day` — engagement startup
- `/debrief-then-publish` — close-out at engagement end
- `/cheatsheet-build` — pocket references during active op
- `/arsenal-report` — pre-walk tool selection
