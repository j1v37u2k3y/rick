---
name: htb-day
description: >
  CTF / HackTheBox / VulnHub engagement kickoff variant. No SOW, no ROE, no client onboarding —
  just spin up a kill-chain handle, name the box, set the target, and start Phase 1 recon.
  Use this skill when the operator is starting a CTF box and wants to track findings + phase
  progress through rick_mcp. Trigger phrases: "start <boxname>", "htb day", "ctf kickoff",
  "begin <ctf box>", "/htb-day". The companion to /engagement-kickoff but tuned for CTF
  practice / training engagements rather than paid client work. After this skill, route to
  /kill-chain-walk for phase-by-phase execution.
---

# HTB Day

> CTF kickoff. No paperwork. Just a kill-chain handle and a recon plan. Start the clock.

---

## Prerequisites

`rick_mcp` MCP server connected. This skill calls:

- `mcp__rick_mcp__rick_tracker` (action=`create`) — initialize engagement record
- `mcp__rick_mcp__rick_kill_chain` (action=`status`) — verify the handle persists
- `mcp__rick_mcp__rick_recon` — Phase 1 starter
- Optionally: `mcp__rick_mcp__rick_cve` if a version banner is known up-front

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **Platform** — `htb`, `vulnhub`, `tryhackme`, `kaizen`, `sans`, or `other`. Used for the
   codename prefix.
2. **Box name** — string, e.g. `MonitorsFour`, `Lame`, `Sauna`. Max 100 chars.
3. **Target** — IP or hostname. E.g. `10.10.10.100` or `monitorsfour.htb`.
4. **Difficulty** *(optional)* — `easy`, `medium`, `hard`, `insane`.
5. **OS hint** *(optional)* — `linux`, `windows`, `bsd`, `unknown`. Feeds the recon
   target_type pick.

---

## Workflow

### Step 1 — Build the codename

Format: `<PLATFORM> - <BoxName> (<YYYY-MM-DD>)`. Examples:

- `HTB - MonitorsFour (2026-05-09)`
- `VulnHub - Kioptrix 2014 (2026-05-15)`
- `Kaizen - Crypto Challenge 3 (2026-05-15)`

### Step 2 — Seed the tracker

```
mcp__rick_mcp__rick_tracker({
  params: {
    action: "create",
    data: '{"client": "<PLATFORM>", "engagement_type": "ctf", "target": "<target>", "box_name": "<box>", "difficulty": "<level>", "os_hint": "<os>", "status": "active"}',
    response_format: "markdown"
  }
})
```

Capture the returned `engagement_id`. This is the kill-chain handle for the rest of the
walk. Surface it to the operator clearly — they'll need it for any future
`/kill-chain-walk` session.

### Step 3 — Verify the kill chain initialized

```
mcp__rick_mcp__rick_kill_chain({
  params: { action: "status", engagement_id: "<id>", response_format: "markdown" }
})
```

Confirm phase is at 1 (Reconnaissance). If not, surface to operator.

### Step 4 — Pick target_type for Phase 1 recon

Map the operator's input to a `rick_recon` target_type:

| Box context                                  | target_type        |
|----------------------------------------------|--------------------|
| Web app focus / login page exposed           | `web_app`          |
| Network-only box / multiple services         | `network`          |
| AD lab / Windows domain                      | `active_directory` |
| AWS-flavored CTF                             | `cloud_aws`        |
| Azure-flavored CTF                           | `cloud_azure`      |
| API-focused (e.g. REST/GraphQL CTF)          | `api`              |
| Container / Docker / K8s CTF                 | `container`        |
| Mobile / APK challenge                       | `mobile`           |

If unclear from the inputs, `AskUserQuestion`. Don't guess.

### Step 5 — Fire Phase 1 recon

```
mcp__rick_mcp__rick_recon({
  params: {
    target_type: "<picked>",
    scope_notes: "<box_name> on <PLATFORM>, target <target>, difficulty <level>, os hint <os>"
  }
})
```

Surface the recon methodology to the operator.

### Step 6 — Optional CVE quick-scan

If the operator already knows a service version (e.g. from a prior `nmap` run), call:

```
mcp__rick_mcp__rick_cve({ params: { query: "<service version>", response_format: "markdown" } })
```

Skip if no version is known yet — that's a Phase 1 result, not a Phase 0 input.

### Step 7 — Log the first finding

```
mcp__rick_mcp__rick_kill_chain({
  params: {
    action: "add_finding",
    engagement_id: "<id>",
    phase: 1,
    finding: "Engagement initialized. Target <target>. Box <box_name>. Recon methodology loaded for target_type <type>."
  }
})
```

### Step 8 — Report and route

Tight summary:

```
CTF engagement kicked off:
- Codename: <PLATFORM> - <BoxName> (<YYYY-MM-DD>)
- Engagement ID: <id>
- Target: <target>
- Phase: 1 (Reconnaissance)
- Next move: execute the recon checklist; capture findings via /kill-chain-walk
```

Then recommend invoking `/kill-chain-walk` with the engagement_id to drive Phase 1 execution.

---

## Acceptance criteria

- [ ] Codename matches the format `<PLATFORM> - <BoxName> (<YYYY-MM-DD>)`
- [ ] `engagement_id` captured and surfaced
- [ ] Phase 1 status confirmed in `rick_kill_chain`
- [ ] At least one finding logged (the kickoff record)
- [ ] Operator routed to `/kill-chain-walk` for next steps

---

## Failure modes

- **`rick_tracker create` fails** — surface error; retry once; if persistent, fall back to
  manual `rick_kill_chain` init.
- **Platform doesn't fit any row** — pick `other`; operator can override the codename prefix.
- **target_type unclear** — `AskUserQuestion`. Don't guess between `web_app` and `api` for
  ambiguous inputs.
- **CVE lookup hits rate limit / network failure** — skip Step 6, continue. CVE is optional.

---

## Voice

CTF energy. Builder metaphors land naturally — "framing the wall" of a new box. Per the
configured operator persona. Honest difficulty assessment (don't pretend an Insane box is
Easy). For character, route through `/be_rick`.

---

## What this skill does NOT do

- Generate a SOW / ROE / onboarding packet — that's `/engagement-kickoff` (client work).
- Execute Phase 1 recon — that's `/kill-chain-walk`. This skill just sets up the handle and
  loads the methodology.
- Sanitize for public writeup — `/writeup-publish` handles that after the box is rooted.
- Persist any private notes outside the MCP server's state.

---

## Related skills

- `/kill-chain-walk` — next step after this skill
- `/engagement-kickoff` — paid client variant (formal SOW + ROE)
- `/cheatsheet-build` — pocket references during the op
- `/writeup-publish` — close the loop with a public writeup after the box is rooted
