---
name: engagement-kickoff
description: >
  One-shot orchestration for standing up a new client offensive-security engagement. Generates
  the SOW/proposal, the rules of engagement, the client onboarding packet, and seeds the
  engagement tracker — four rick_mcp tools fired in sequence with no intermediate context loss.
  Use this skill when the operator wants to kick off a new paid engagement, generate a
  proposal, draft ROE, onboard a client, or start tracking a new engagement. Trigger phrases
  include "kickoff an engagement", "new engagement", "start engagement for <client>", "spin up
  <client> pentest", "/engagement-kickoff". Skip for CTF/HTB engagements — those have no formal
  SOW; use `/htb-day` instead.
---

# Engagement Kickoff

> Four MCP tools fire in sequence. One engagement walks out scoped, authorized, onboarded, and
> tracked. Get the foundation right before any drywall.

---

## Prerequisites

The `rick_mcp` MCP server must be connected. This skill calls four of its tools:

- `mcp__rick_mcp__rick_engagement_proposal`
- `mcp__rick_mcp__rick_roe`
- `mcp__rick_mcp__rick_client_onboarding`
- `mcp__rick_mcp__rick_tracker` (action=`create`)

---

## Inputs required

If the operator hasn't supplied these, **ask via `AskUserQuestion` before firing any tool**
(plan-first cadence; ask at config decision points):

1. **`client_name`** — string, max 100 chars.
2. **`engagement_type`** — pick from the vocabulary table below (proposal and ROE tools take
   different strings — this skill maps for you).
3. **`estimated_days`** — integer 1–90. Default 10.
4. **`special_requirements`** *(optional)* — string ≤500 chars. Compliance, off-hours, specific
   exclusions. Goes into the proposal only.

---

## Engagement-type vocabulary mapping

The proposal tool and ROE tool ship with **different vocabularies**. Known seam. Translate:

| Operator intent  | `rick_engagement_proposal` | `rick_roe`        |
|------------------|----------------------------|-------------------|
| Web app pentest  | `web_app_pentest`          | `app_security`    |
| Network pentest  | `network_pentest`          | `pentest`         |
| AD review        | `ad_review`                | `pentest`         |
| Cloud audit      | `cloud_audit`              | `cloud_audit`     |
| Red team         | `red_team`                 | `red_team`        |
| API security     | `api_security`             | `app_security`    |
| Full scope       | `full_scope`               | `pentest`         |
| Phishing only    | `full_scope` (closest)     | `phishing`        |
| Vuln assessment  | `network_pentest` (closest)| `vuln_assessment` |

If the operator's intent doesn't fit a row, ask via `AskUserQuestion`. Don't guess.

---

## Workflow

Run sequentially.

### Step 1 — Generate the SOW/proposal

```
mcp__rick_mcp__rick_engagement_proposal({
  params: {
    client_name: "<client_name>",
    engagement_type: "<proposal vocab>",
    estimated_days: <int>,
    special_requirements: "<text or null>",
    response_format: "markdown"
  }
})
```

### Step 2 — Generate the Rules of Engagement

```
mcp__rick_mcp__rick_roe({
  params: {
    client_name: "<client_name>",
    engagement_type: "<roe vocab>",
    duration_days: <same as estimated_days>,
    response_format: "markdown"
  }
})
```

### Step 3 — Generate the client onboarding packet

```
mcp__rick_mcp__rick_client_onboarding({
  params: {
    client_name: "<client_name>",
    engagement_type: "<roe vocab — same string as Step 2>",
    response_format: "markdown"
  }
})
```

### Step 4 — Seed the tracker

```
mcp__rick_mcp__rick_tracker({
  params: {
    action: "create",
    data: '{"client": "<client_name>", "engagement_type": "<vocab>", "duration_days": <int>, "status": "scoping"}',
    response_format: "markdown"
  }
})
```

Capture the returned `engagement_id` — canonical handle for any later `rick_tracker` or
`rick_kill_chain` operations.

### Step 5 — Report

Return a tight summary to the operator. Format:

```
Engagement kicked off:
- Client: <client_name>
- Type: <engagement_type>
- Duration: <estimated_days> days
- Tracker ID: <engagement_id>
- Status: scoping
- Next move: schedule kickoff call + deliver onboarding packet
```

Include the full proposal / ROE / onboarding markdown in the response so the operator can
copy-paste into their own systems (PlexTrac, Notion, vault, etc.).

---

## Acceptance criteria

- [ ] All 4 MCP tool calls returned successfully (no errors, no truncation)
- [ ] `engagement_id` captured and returned to the operator
- [ ] Engagement-type mapping was explicit (no silent guess)
- [ ] Summary shows next concrete move

---

## Failure modes

- **Tool call fails / times out** — do NOT proceed to the next step. Surface the error;
  ask whether to retry or roll back.
- **`engagement_type` doesn't fit any vocabulary row** — `AskUserQuestion` with the table rows
  as options. Don't guess.
- **Tracker create returns no `engagement_id`** — surface; offer to retry or proceed
  without tracker (degrade gracefully).

---

## Voice

Skill output is operational. Honest scope, no padded estimates. If the operator wants
character, route through `/be_rick` or the `rick_mcp` persona prompts — this skill stays
in operations voice.

---

## What this skill does NOT do

- Run recon, vuln assessment, or any active testing — that's `/kill-chain-walk`.
- Generate final reports — that's `/debrief-then-publish`.
- Handle CTF/HTB engagements — those skip proposal/ROE/onboarding. Use `/htb-day`.
- Persist to any vault — orchestration only. Tracker JSON state lives in the MCP server's
  configured state directory; engagement notes are the operator's call.

---

## Related skills

- `/kill-chain-walk` — phase-by-phase guided op once an engagement is kicked off
- `/debrief-then-publish` — close-out sequence at engagement end
- `/htb-day` — CTF/HTB variant of this kickoff
- `/arsenal-report` — pick the right rick_mcp tools for a given target type
