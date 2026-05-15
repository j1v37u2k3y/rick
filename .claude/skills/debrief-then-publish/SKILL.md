---
name: debrief-then-publish
description: >
  Engagement close-out orchestration. Runs the post-engagement debrief, generates the report
  template scaffolds, builds a unified timeline, and exports the engagement data — readying
  the deliverable package for the operator to finalize. Use this skill when an engagement is
  done and the operator wants to wrap it: "close out <engagement>", "debrief MonitorsFour",
  "wrap the engagement", "generate the report", "/debrief-then-publish". Closes the loop from
  /kill-chain-walk Phase 7. Not for active testing (use /kill-chain-walk) or public writeup
  publication (use /writeup-publish — that's the sanitization-and-publish pipeline).
---

# Debrief → Publish

> Engagement done. Four MCP tools fire to assemble the deliverable scaffolding: debrief +
> report templates + timeline + export. Operator reviews, polishes, ships.

---

## Prerequisites

`rick_mcp` MCP server connected. Engagement must have completed phase 6 in
`/kill-chain-walk`. This skill calls:

- `mcp__rick_mcp__rick_debrief` — post-engagement lessons learned template
- `mcp__rick_mcp__rick_report_template` — section templates (executive summary, findings,
  methodology, scope, remediation, appendix)
- `mcp__rick_mcp__rick_timeline` — unified chronological event view
- `mcp__rick_mcp__rick_export` — engagement data export
- `mcp__rick_mcp__rick_kill_chain` — finalize phase state

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **`engagement_id`** — handle to close out.
2. **`engagement_type`** — for `rick_debrief`: `pentest`, `red_team`, `vuln_assessment`,
   `cloud_audit`, `app_security`. Should match the kickoff type; ask if ambiguous.
3. **`client_name`** *(optional)* — overrides default `[CLIENT]` placeholder in debrief.
4. **Top findings** *(optional, ≤ 1000 chars)* — comma-separated key findings. If not
   supplied, derive from `rick_kill_chain action=status` + `rick_timeline`.
5. **Finding severities to template** *(optional)* — list of severities to generate
   per-finding report sections for (`critical`, `high`, `medium`, `low`, `info`).

---

## Workflow

### Step 1 — Confirm engagement is ready to close

```
mcp__rick_mcp__rick_sitrep({ params: { engagement_id: "<id>", response_format: "markdown" } })
mcp__rick_mcp__rick_kill_chain({ params: { action: "status", engagement_id: "<id>" } })
```

If current phase < 6, ask the operator: close out anyway / advance phases first / cancel.
Phase 6 (Documentation) should be reached before debriefing.

### Step 2 — Derive key findings (if not supplied)

```
mcp__rick_mcp__rick_timeline({
  params: { engagement_id: "<id>", filter_type: "finding", response_format: "markdown" }
})
```

Extract the highest-severity / most-load-bearing findings. Surface them to the operator for
confirmation before feeding to the debrief.

### Step 3 — Generate debrief

```
mcp__rick_mcp__rick_debrief({
  params: {
    client_name: "<client_name or default>",
    engagement_type: "<from kickoff>",
    key_findings: "<comma-separated, ≤ 1000 chars>",
    response_format: "markdown"
  }
})
```

Captures: what worked, what didn't, lessons learned, recommendations for next cycle.

### Step 4 — Generate report scaffolds

Run in parallel for each section needed:

```
mcp__rick_mcp__rick_report_template({ params: { section: "executive_summary" } })
mcp__rick_mcp__rick_report_template({ params: { section: "methodology" } })
mcp__rick_mcp__rick_report_template({ params: { section: "scope" } })
mcp__rick_mcp__rick_report_template({ params: { section: "remediation" } })
mcp__rick_mcp__rick_report_template({ params: { section: "appendix" } })
```

For each finding the operator wants documented (use the severities list):

```
mcp__rick_mcp__rick_report_template({
  params: {
    section: "finding",
    finding_title: "<finding title>",
    severity: "<critical|high|medium|low|info>",
    description: "<finding details from timeline>"
  }
})
```

### Step 5 — Export engagement data

```
mcp__rick_mcp__rick_export({
  params: { engagement_id: "<id>", response_format: "json" }
})
```

Captures the structured engagement record for archival or import into PlexTrac / other
reporting platforms.

### Step 6 — Output

Single response bundling:

1. **Engagement summary** — client, type, duration, final phase, top findings
2. **Debrief** — from Step 3
3. **Report scaffolds** — all sections generated in Step 4, grouped
4. **Timeline** — full chronological event view from Step 2
5. **Export** — JSON dump from Step 5 (or note where it was saved if the MCP server
   persists it)
6. **Next moves** — concrete bullet list:
   - Polish report scaffolds and import into reporting platform
   - Schedule debrief call with client
   - Run `/writeup-publish` if a public/sanitized writeup is wanted
   - Mark engagement complete in any tracking system

---

## Acceptance criteria

- [ ] All 4 primary MCP tools called successfully
- [ ] Debrief includes at least 1 key finding (not just a generic template)
- [ ] Report scaffolds cover every section in: exec summary, methodology, scope, remediation,
      appendix, + finding templates for every claimed finding
- [ ] Timeline shows the full event sequence (no truncation)
- [ ] Export returned a valid structured payload
- [ ] Next-moves section has at least 3 concrete actions

---

## Failure modes

- **Engagement is mid-phase** — surface to operator. Don't close out a half-done op.
- **No findings recorded in `rick_kill_chain`** — debrief will be empty. Ask operator to
  recall and inject key findings manually before generating.
- **`rick_export` returns malformed data** — log the issue, return debrief + report
  scaffolds without the export. Operator can re-run export separately.
- **Engagement-type mismatch between kickoff and debrief** — `rick_debrief` only supports 5
  types (different from kickoff vocab). Map:
  - kickoff `web_app_pentest` / `api_security` → debrief `app_security`
  - kickoff `network_pentest` / `ad_review` / `full_scope` → debrief `pentest`
  - kickoff `red_team` → debrief `red_team`
  - kickoff `cloud_audit` → debrief `cloud_audit`

---

## Voice

Close-out is formal-leaning. Honest debrief — what didn't work matters as much as what
worked. No padded claims. No inflated severity. For formal report-writing register, invoke
the server-side persona prompt via `rick_mode(persona="evaluate")` before / during the polish
pass.

---

## What this skill does NOT do

- Polish the report prose — operator writes the actual paragraphs over the scaffolds.
- Send the report to the client — operator delivers.
- Sanitize for public publication — `/writeup-publish` handles redaction + public framing.
- Archive the engagement to long-term storage — operator's call.

---

## Related skills

- `/kill-chain-walk` — must complete phase 6 before this skill runs cleanly
- `/writeup-publish` — public/sanitized writeup pipeline (different audience than the report)
- `/engagement-kickoff` — start of the loop this skill closes
- `rick_mode(persona="evaluate")` — formal voice register for the polish pass (server-side persona)
