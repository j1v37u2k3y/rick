---
name: writeup-publish
description: >
  Take a completed engagement (CTF box or sanitized client engagement) and produce a public
  writeup README — redacted, structured, ready to publish. Pulls engagement data from
  rick_mcp via rick_export + rick_timeline + rick_writeups, applies redaction rules, formats
  per public-writeup conventions, and emits a structured markdown package. Use this skill
  when the operator wants to publish a writeup after rooting a box or closing an engagement:
  "writeup <engagement>", "publish <box>", "public writeup for <id>", "/writeup-publish". Not
  for client deliverables (use /debrief-then-publish — that's the formal report) or for
  active engagement work (use /kill-chain-walk).
---

# Writeup Publish

> Engagement done. Box rooted. Now turn the private kill chain into a public writeup —
> sanitized, structured, attributed. Different audience than the client report.

---

## Prerequisites

`rick_mcp` MCP server connected. Engagement must be substantially complete (Phase 5+ in
`rick_kill_chain`). This skill calls:

- `mcp__rick_mcp__rick_export` — full engagement export
- `mcp__rick_mcp__rick_timeline` — chronological event view
- `mcp__rick_mcp__rick_writeups` — public-writeup search + citation cross-reference
- `mcp__rick_mcp__rick_sitrep` — confirm engagement state

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **`engagement_id`** — completed engagement to publish.
2. **Audience** — `htb_style` (HTB writeup conventions), `vulnhub_style`, `blog_post`,
   `conference_talk`, `bug_bounty_disclosure`, or `other`.
3. **Sanitization level**:
   - `ctf_default` — minimal redaction (CTF infra is public)
   - `client_full` — full redaction (PII, internal hostnames, client name, IPs, creds, tokens)
   - `bug_bounty` — program-specific (redact per the program's disclosure policy)
4. **Output mode** — `print` (return markdown in chat) or `path_hint` (return markdown plus
   a suggested file path the operator can use to save it). Path hints follow public-writeup
   conventions; the skill does NOT write to the filesystem.

---

## Redaction rules

Based on sanitization level:

### `ctf_default`
- Box names, IPs, hostnames: KEEP (public)
- Tool output: KEEP
- Cred values that came from the box: KEEP (CTF flag-style only)
- Operator's real PII / API keys / personal paths: REDACT to `<REDACTED>`

### `client_full`
- Client name: REDACT to `[CLIENT]`
- Internal hostnames / IPs / domains: REDACT to `<INTERNAL>` or generalized class
- Cred values: REDACT to `<CREDENTIAL>`
- File paths inside client systems: GENERALIZE (e.g. `/home/admin/secrets/.env` → `/<user>/<env-file>`)
- Specific timestamps: GENERALIZE to date-only
- Operator's real PII: REDACT

### `bug_bounty`
- Program-specific. Ask operator for the program's disclosure policy first. Common rules:
  - Subdomain names: often REDACT
  - Exploit chain: PUBLISH (with the program's permission)
  - Payloads: PUBLISH
  - Internal IPs: REDACT

---

## Workflow

### Step 1 — Verify engagement state

```
mcp__rick_mcp__rick_sitrep({ params: { engagement_id: "<id>" } })
```

Confirm Phase 5+ reached. If earlier, surface to operator: publish anyway / advance phases
first / cancel.

### Step 2 — Pull full engagement data

```
mcp__rick_mcp__rick_export({ params: { engagement_id: "<id>", response_format: "json" } })
mcp__rick_mcp__rick_timeline({ params: { engagement_id: "<id>", response_format: "markdown" } })
```

The export gives structured data; the timeline gives narrative flow.

### Step 3 — Cross-reference public writeups

```
mcp__rick_mcp__rick_writeups({
  params: { query: "<box_name or vuln class>", response_format: "markdown" }
})
```

Pulls existing public writeups for citation / context (don't plagiarize — credit prior art
where relevant).

### Step 4 — Apply redaction

Walk through the export + timeline content. Apply the picked sanitization level. For each
redaction made, log it as a one-line bullet (the operator audits before publication).

### Step 5 — Structure the writeup

Public-writeup conventions vary by audience. Use this scaffold (HTB style; adapt for other
audiences):

```markdown
# <Box Name> — <Platform>

> **Difficulty:** <level>
> **OS:** <os>
> **Date Rooted:** <YYYY-MM-DD>
> **Tags:** <vuln-class>, <tools-used>

## Recon

<Phase 1 findings, narratively flowing>

## Vulnerability Assessment

<Phase 2 findings, focused on what mattered>

## Exploitation

<Phase 3 — the primary primitive + how it was exploited>

## Privilege Escalation

<Phase 4 — root flag path>

## Lessons / Takeaways

<3-5 bullets on what was learned, what was novel, what would be done differently>

## References

- <prior public writeups for this box, from rick_writeups>
- <related Knowledge entries if vault is configured>
```

Adapt for other audiences:
- `blog_post`: looser structure, more narrative, broader audience
- `conference_talk`: slide-friendly headers, bigger takeaways
- `bug_bounty_disclosure`: program template, severity rating, CVSS, repro steps

### Step 6 — Output

Single markdown response containing:

1. **Redacted writeup** — the structured markdown from Step 5
2. **Redactions applied** — bulleted audit log from Step 4
3. **Citations** — public writeups referenced from Step 3
4. **Suggested file path** *(if output_mode = path_hint)* — typically
   `writeups/<platform>/<slug>/README.md`. Operator decides where it actually lives.
5. **Next moves** — review the redactions, polish the prose, push to public repo / blog

---

## Acceptance criteria

- [ ] Sanitization level applied to every piece of content (no leak-by-omission)
- [ ] Redactions audit log enumerates every change
- [ ] Public writeup citations sourced from `rick_writeups` (no fabricated references)
- [ ] Structure matches the picked audience convention
- [ ] No real PII, API keys, internal hostnames slipped through under `client_full`

---

## Failure modes

- **Engagement isn't mature enough** — surface phase number, ask operator: publish anyway /
  advance / cancel.
- **Redaction rules ambiguous for a specific piece of content** — surface to operator via
  `AskUserQuestion`. Don't silently choose.
- **`rick_writeups` returns no citations** — note that the writeup may be novel; check
  manually for prior art before claiming first-publish.
- **Bug bounty program policy unknown** — block the publish; ask operator to provide the
  policy first.

---

## Voice

Public-facing material. Honest about what worked and what didn't. No bragging. No padded
"l33t hax0r" framing — let the technical depth speak. For voice / register shifts, invoke
the server-side persona prompts: `rick_mode(persona="be_rick")` for character,
`rick_mode(persona="evaluate")` for formal disclosure register.

---

## What this skill does NOT do

- Write to the filesystem — the skill returns markdown; operator decides where to save.
- Push to a public repo — operator drives git.
- Submit to a bug bounty program — operator submits.
- Sanitize beyond the picked level — if `ctf_default` is picked, client-style redaction is
  NOT applied. Be explicit about what level was chosen.

---

## Related skills

- `/kill-chain-walk` — produces the engagement data this skill publishes
- `/debrief-then-publish` — formal client report (different audience, different redaction)
- `/voice-check` — lint the writeup prose for voice drift before publishing
- `rick_mode(persona="evaluate")` — formal register for bug-bounty disclosures (server-side persona)
