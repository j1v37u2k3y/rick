---
name: engagement-checkin
description: >
  Single-cycle heartbeat for an active engagement. Reads current state via rick_sitrep +
  rick_kill_chain, formats a status snapshot, and updates the engagement note's `## Status
  (auto-updated …)` block if the operator has a vault configured. Designed to be invoked on a
  schedule via `/loop` (in-session) or `/schedule` (cross-session) so the engagement's readable
  artifact stays current without manual sync. Engagement-agnostic — works for any engagement_id
  tracked in rick_kill_chain (client engagements kicked off via /engagement-kickoff,
  CTF engagements via /htb-day, or anything else). Trigger phrases: "checkin <engagement>",
  "engagement status update", "refresh engagement note", "/engagement-checkin <id>". Not for
  active phase work (use /kill-chain-walk for that) or engagement startup (use
  /engagement-kickoff or /htb-day).
---

# Engagement Checkin

> Heartbeat. One cycle: read state, format snapshot, refresh the engagement note's Status block.
> Composes with `/loop` or `/schedule` to keep the readable artifact current without operator
> overhead. Single source of truth stays in `rick_kill_chain`; the vault note becomes the
> human-readable mirror.

---

## Prerequisites

`rick_mcp` MCP server connected. This skill calls:

- `mcp__rick_mcp__rick_sitrep` — current tactical picture
- `mcp__rick_mcp__rick_kill_chain` (action=`status`) — phase + findings state
- `mcp__rick_mcp__rick_timeline` *(optional)* — for last-N events in the snapshot
- `ReadMcpResourceTool` — pulls `vault://engagements/<codename>` to verify the note exists

Vault writes use direct file Edit against the standard path
`~/.rick_mcp/vault/Engagements/<codename>.md` (the documented convention). If no vault is
configured, the skill falls back to chat-only output — no filesystem writes.

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **`engagement_id`** — the kill-chain handle to check on. If not supplied, list active
   engagements via `rick_kill_chain({ action: "list" })` and let the operator pick.
2. **`include_timeline`** *(optional)* — `true` (default) adds the last 5 timeline events to
   the Status block. `false` keeps it lean (just phase + last finding).

---

## Workflow

### Step 1 — Read current state

In parallel:

```
mcp__rick_mcp__rick_sitrep({
  params: { engagement_id: "<id>", response_format: "markdown" }
})

mcp__rick_mcp__rick_kill_chain({
  params: { action: "status", engagement_id: "<id>", response_format: "markdown" }
})
```

If `include_timeline`:

```
mcp__rick_mcp__rick_timeline({
  params: { engagement_id: "<id>", response_format: "markdown" }
})
```

### Step 2 — Extract the snapshot fields

From the responses above, build a structured snapshot:

| Field              | Source                                                      |
|--------------------|-------------------------------------------------------------|
| `timestamp`        | Current ISO timestamp (e.g. `2026-05-17 14:32 UTC`)         |
| `current_phase`    | From `rick_kill_chain status` — number + name (e.g. `2 — Vulnerability Assessment`) |
| `findings_count`   | From kill-chain status                                      |
| `last_finding`     | Most recent finding text (truncate to ≤ 200 chars)          |
| `last_finding_at`  | Timestamp of the last finding                               |
| `next_move_hint`   | From `rick_sitrep` recommendation section                   |
| `timeline_tail`    | Last 5 events from timeline (if `include_timeline=true`)    |

### Step 3 — Try to read the vault note

```
ReadMcpResourceTool({ server: "rick_mcp", uri: "vault://engagements/<codename>" })
```

The `engagement_id` and the vault note's filename codename may differ. The MCP resource handler
accepts either; if it returns "not found" or "not configured," the vault path doesn't exist and
the skill falls back to chat-only output.

If the resource returns the note content, parse it to find the existing `## Status
(auto-updated …)` block (if any) so the update can replace it cleanly.

### Step 4 — Format the Status block

Build the markdown block to write:

```markdown
## Status (auto-updated <timestamp>)

- **Phase:** <current_phase>
- **Findings:** <findings_count>
- **Last finding** (<last_finding_at>): <last_finding>
- **Next move (rick_sitrep):** <next_move_hint>

<!-- if include_timeline=true -->
### Recent activity
- <event 1 timestamp> — <event 1 description>
- <event 2 timestamp> — <event 2 description>
- ...
```

Wrap body lines at ~120 chars per project formatting convention. Space-pad YAML inline arrays
if any frontmatter edits are needed.

### Step 5 — Update the vault note

Construct the absolute path: `$HOME/.rick_mcp/vault/Engagements/<codename>.md` where
`<codename>` matches the note filename from Step 3.

Use the `Edit` tool to replace the existing `## Status (auto-updated …)` block, OR insert a
new one after the frontmatter `---` close and before the `## For future Claude` section.

**Replacement strategy:**
- If a `## Status (auto-updated` heading already exists, match from that heading through the
  next `## ` heading (exclusive) — replace that span.
- If no Status block exists, insert immediately after the frontmatter close (the second `---`
  line in the file).

The `Edit` tool requires reading the file first; the MCP resource read in Step 3 satisfies
that — but Claude must also Read the file via the filesystem Read tool before any Edit (the
harness tracks Read state per filesystem path, distinct from MCP resource reads).

### Step 6 — Output to chat

Return a tight summary regardless of whether the vault was updated:

```
Engagement checkin: <codename>
- Phase: <current_phase>
- Findings: <findings_count> (last: <last_finding_at>)
- Next move: <next_move_hint>
- Vault note: <updated | not configured | not found>
```

---

## Invocation patterns

The skill is designed to be invoked on a schedule. Two recommended modes:

### `/loop` — in-session heartbeat

```
/loop 10m /engagement-checkin <engagement_id>
```

Runs every 10 minutes during the current Claude Code session. Stops when the session ends.
Best for active work sessions where the operator is in Claude Code.

Adjust the interval per engagement intensity:
- `5m` — active exploit phase, fast-moving findings
- `10m` — typical kill-chain work
- `30m` — reading / methodology phases, slower cadence
- `1h` — long client engagements with sparse activity

### `/schedule` — cross-session heartbeat

```
/schedule create "*/15 * * * *" /engagement-checkin <engagement_id>
```

Creates a persistent scheduled agent that fires on a cron schedule even when the operator
isn't in Claude Code. Best for long engagements that span days. Remove with
`/schedule delete <id>` when the engagement closes.

### Manual one-shot

```
/engagement-checkin <engagement_id>
```

Single cycle, no loop. Useful for ad-hoc "what's my current state?" checks.

---

## Acceptance criteria

- [ ] Snapshot reflects state from `rick_kill_chain` at the moment of invocation (no stale data)
- [ ] Status block timestamp is the current invocation time, not the last finding time
- [ ] If vault is configured + note exists: existing Status block replaced, not duplicated
- [ ] If vault is configured + note missing: skill reports "not found," does NOT create the file
- [ ] If vault is unconfigured: skill reports "not configured," falls back to chat output
- [ ] Output to chat is ≤ 10 lines (heartbeat should be quiet)
- [ ] Idempotent — re-running with no state change produces an updated timestamp but identical
      body content

---

## Failure modes

- **`engagement_id` doesn't exist** — `rick_kill_chain` returns not-found. Surface to operator;
  skip the vault write.
- **Vault note exists but has no closing `---` for frontmatter** — malformed note; surface a
  warning, append the Status block at the end of the file rather than after frontmatter.
- **MCP resource times out** — skill logs the failure as a single chat line, leaves vault
  unchanged. Next loop iteration retries.
- **Loop running on a closed engagement** — operator forgot to stop the loop. The checkin
  still runs (state is fixed); the operator should stop the loop manually (`/loop` provides
  controls).

---

## Voice

Operational. Heartbeats are quiet — the chat output is one short block, not a paragraph. The
Status block content is terse: facts, no padding. For character / mantra, route through
`/be_rick` or the `rick_mantra` MCP tool — this skill stays in operations voice.

---

## What this skill does NOT do

- Drive phase advancement — that's `/kill-chain-walk` (decision-point pattern).
- Add new findings — operators add findings via `rick_kill_chain action=add_finding` during
  the walk. The checkin only reads state.
- Create engagement notes — if the vault note is missing, the checkin doesn't create one;
  that's the engagement-kickoff skill's job.
- Commit anything to git — the vault file edit happens on the filesystem; the operator
  decides when to commit.

---

## Related skills

- `/engagement-kickoff` — stand up a client engagement (the Status block tracks it)
- `/htb-day` — stand up a CTF engagement (same)
- `/kill-chain-walk` — phase-by-phase active work; pair this checkin with it via `/loop`
- `/debrief-then-publish` — close-out; stop the heartbeat loop before running this

---

**Mantra:** Single source of truth in the tracker. The vault is the mirror. The heartbeat keeps
the mirror honest.
