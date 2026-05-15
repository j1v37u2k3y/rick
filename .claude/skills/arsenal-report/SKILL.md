---
name: arsenal-report
description: >
  Given a target description (host, application, network, cloud env, AD domain, etc.), recommend
  exactly which rick_mcp tools and resources to fire, in what order, mapped to the 7-phase
  methodology (PTES + OWASP + MITRE ATT&CK). Solves the "many tools, which one fits this op?"
  problem. Use this skill when the operator describes a target and wants a curated tool
  roadmap, asks "what should I run against X", "what tools for <target type>", "arsenal for
  <scenario>", "/arsenal-report", or anytime an engagement is about to start phase 1 recon
  and needs a prioritized plan instead of a flat list. Not for handle OSINT (use
  rick_recon_handle directly) or for vuln-class one-pagers (use /cheatsheet-build).
---

# Arsenal Report

> Pick the right tools for the target in front of you. Order them by phase. Builder's eye on
> the toolbox.

---

## Prerequisites

`rick_mcp` MCP server connected. This skill calls:

- `mcp__rick_mcp__rick_tool_recommend` — scenario-aware curation
- `mcp__rick_mcp__rick_capabilities` — full tool map (for cross-reference)

---

## Inputs required

If missing, ask via `AskUserQuestion`:

1. **Target description** — string, 5–500 chars. Be specific: protocol, tech stack, exposure
   surface, what's known. Bad: "a web app." Good: "external Apache 2.4 site, PHP backend,
   login form + REST API at /api/v2, behind Cloudflare WAF."
2. **Phase scope** *(optional)* — `all` (default), `recon_only`, `vuln_to_priv_esc`,
   `post_compromise`, `report_only`.
3. **Constraint flags** *(optional)* — `no_active_scan`, `no_auth_brute`, `safe_mode`,
   `red_team_evasive`. Feed into the scenario string so recommendations match the ROE.

---

## Workflow

### Step 1 — Build the scenario string

Compose a 5–500 char string capturing target + phase scope + constraints. Example:

```
External Apache 2.4 web app, PHP backend, login form + REST API /api/v2, Cloudflare WAF.
Recon + vuln assessment only. No auth bruteforce. Safe mode.
```

### Step 2 — Call `rick_tool_recommend`

```
mcp__rick_mcp__rick_tool_recommend({
  params: { scenario: "<built string>", response_format: "markdown" }
})
```

Capture the curated tool selections with rationale.

### Step 3 — Cross-reference with capabilities

```
mcp__rick_mcp__rick_capabilities({})
```

Use the full map to surface any rick_mcp tools the recommendation missed that fit the phase
scope. Add with a note: `_(not in initial recommendation, surfaced from capabilities scan)_`.

### Step 4 — Map to the 7-phase methodology

Group recommended + surfaced tools by phase:

```markdown
## Phase 1 — Reconnaissance
- <tool 1>: <one-line rationale>
- <tool 2>: <one-line rationale>

## Phase 2 — Vulnerability Assessment
...
```

Methodology phases:

1. Reconnaissance
2. Vulnerability Assessment
3. Exploitation
4. Privilege Escalation
5. Lateral Movement
6. Documentation
7. Remediation Strategy

Skip phases the operator excluded.

### Step 5 — Surface adjacent resources

Suggest 2–4 relevant MCP resources to pull for deeper context. Examples:

- `profile://methodology` — full phase walkthrough
- `profile://stack` — tool ecosystem context
- `doc://war_stories` — pattern matches from past ops
- `resume://evidence` — engagement evidence map

Reference real resources only. Check `rick_capabilities` output for the resource list.

### Step 6 — Output

Single markdown block. Sections in order:

1. **Target** — restated for confirmation
2. **Scenario string used** — full text passed to the tool (for traceability)
3. **Constraints applied** — flags + effect
4. **Tools by phase** — grouped list with rationale
5. **Resources to pull** — adjacent `profile://`, `doc://`, `resume://` entries
6. **Recommended first move** — single concrete next action

Keep tight. The operator reads this before an op — no preamble.

---

## Acceptance criteria

- [ ] Scenario string ≤ 500 chars
- [ ] Tools grouped by phase, no phase has > 5 tools (signal of imprecision if it does)
- [ ] Every tool has a one-line rationale tied to the target
- [ ] Resources reference real MCP URIs, not fabricated
- [ ] Recommended first move is a single concrete command, not a paragraph

---

## Failure modes

- **`rick_tool_recommend` returns generic suggestions** — scenario string was too vague.
  Ask the operator for more specifics (tech stack, known versions, exposure).
- **No tools match the phase scope** — phase scope was too narrow. Widen via `AskUserQuestion`.
- **Conflicting constraints** — e.g. `red_team_evasive` + `safe_mode` are different doctrines.
  Surface the conflict; ask which wins.

---

## Voice

Honest assessments. If the target description is thin, say so. If a tool is overkill, say
that. No checkbox compliance. For character, route through `/be_rick`.

---

## What this skill does NOT do

- Run any of the recommended tools — planning skill only.
- Generate exploits or payloads — use `/cheatsheet-build` for pocket refs.
- OSINT a hacker handle — `rick_recon_handle` is the direct tool.
- Decide whether to take the engagement — use `rick_compatibility_check`.

---

## Related skills

- `/engagement-kickoff` — stand up a new engagement
- `/kill-chain-walk` — execute the recommended plan phase by phase
- `/cheatsheet-build` — pocket reference for a specific vuln class
