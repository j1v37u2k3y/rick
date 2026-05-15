---
name: cheatsheet-build
description: >
  Given a vuln class, attack stage, or target type, produce a one-page pocket reference fusing
  the relevant rick_mcp tool cheatsheet(s) + payload guide stage into a focused card. Use this
  skill when the operator is mid-op and needs a focused reference card, asks "cheatsheet for
  <topic>", "payload guide for <stage>", "one-pager on <vuln class>", "/cheatsheet-build", or
  anytime depth-on-demand beats reading the full methodology. Output is a consolidated
  markdown one-pager. Not for full methodology walkthroughs (use /kill-chain-walk) or for
  tool selection planning (use /arsenal-report).
---

# Cheatsheet Build

> Pocket reference for an active op. Fuses tool commands + payload methodology + adjacent
> knowledge into a one-pager you can scan with one hand on the keyboard.

---

## Prerequisites

`rick_mcp` MCP server connected. This skill calls:

- `mcp__rick_mcp__rick_cheatsheet` — tool-keyed reference (10 supported tools)
- `mcp__rick_mcp__rick_payload_guide` — stage-keyed methodology (4 stages: `initial_access`,
  `persistence`, `lateral_movement`, `exfil`)

---

## Inputs required

Ask via `AskUserQuestion` if missing:

1. **Topic** — vuln class, attack stage, or target type. Free-form string.
   Examples: "LFI", "AD kerberoasting", "lateral movement via WinRM", "SQLi blind boolean".

---

## Topic → tool / stage mapping

The cheatsheet tool knows 10 tools; payload guide knows 4 stages. The skill maps free-form
topics to the right combinations. Use this table as a starting heuristic; expand as new
topics arise.

| Topic                          | `rick_cheatsheet` tool(s)             | `rick_payload_guide` stage |
|--------------------------------|---------------------------------------|----------------------------|
| LFI / path traversal           | `ffuf`, `burp`                        | `initial_access`           |
| SQLi (any variant)             | `sqlmap`, `burp`                      | `initial_access`           |
| XSS / CSRF                     | `burp`                                | `initial_access`           |
| Directory / endpoint discovery | `ffuf`, `nmap`                        | `initial_access`           |
| Network recon                  | `nmap`                                | `initial_access`           |
| AD enumeration                 | `bloodhound`, `kerbrute`, `impacket`  | `lateral_movement`         |
| AD priv esc / kerberoasting    | `kerbrute`, `impacket`, `crackmapexec`| `lateral_movement`         |
| Lateral movement (Windows)     | `crackmapexec`, `impacket`            | `lateral_movement`         |
| Pivoting / tunneling           | `chisel`                              | `lateral_movement`         |
| Password cracking              | `hashcat`                             | `initial_access` (or n/a)  |
| Initial access (any)           | (skip cheatsheet)                     | `initial_access`           |
| Persistence (Linux/Windows)    | (skip cheatsheet)                     | `persistence`              |
| Exfiltration                   | `chisel`                              | `exfil`                    |

If the topic doesn't fit any row, ask via `AskUserQuestion` with the rows as options. Don't
guess. Skip the cheatsheet call entirely if no tool maps (still call payload guide).

Supported `rick_cheatsheet` tools: `nmap`, `burp`, `ffuf`, `hashcat`, `bloodhound`,
`impacket`, `crackmapexec`, `chisel`, `sqlmap`, `kerbrute`.

---

## Workflow

### Step 1 — Map the topic

Walk the table. Determine which tools + stage apply.

### Step 2 — Pull tool cheatsheets

For each mapped tool, in parallel:

```
mcp__rick_mcp__rick_cheatsheet({
  params: { tool: "<tool name>", response_format: "markdown" }
})
```

### Step 3 — Pull payload guide (if applicable)

```
mcp__rick_mcp__rick_payload_guide({
  params: { payload_type: "<stage>", response_format: "markdown" }
})
```

### Step 4 — Fuse into one-pager

Build a single markdown document. Sections in order:

1. **Topic** — restated
2. **TL;DR** — 2–3 sentences. What this attack/situation is, when it applies, the primary
   primitive.
3. **Tool commands** — concatenated cheatsheet output, deduplicated. Keep tool-specific
   subheaders (`### ffuf`, `### burp`).
4. **Payload methodology** — payload guide output, trimmed to relevance.
5. **Next move** — single concrete first command or step for the active op.

Target output length: ~1 page when rendered (rough: 60–100 lines).

### Step 5 — Output

Return the one-pager in the chat response.

---

## Acceptance criteria

- [ ] Topic mapped to at least one source (tool cheatsheet OR payload guide)
- [ ] One-pager fits roughly one page when rendered
- [ ] "Next move" is a single concrete command, not a paragraph
- [ ] Tool commands deduplicated (no overlap between tools listed multiple times)

---

## Failure modes

- **Topic doesn't map to any row** — `AskUserQuestion` with rows as options. Don't guess.
- **Cheatsheet tool returns 404 / not-found** — only 10 tools supported. Drop that tool from
  the fusion, continue with the rest.
- **Output exceeds 1 page** — trim the payload guide section first (often verbose), then
  consolidate tool commands.

---

## Voice

Pocket reference for an active op. No fluff. Each section earns its lines. Signal density
over prose. For character, route through `/be_rick`.

---

## What this skill does NOT do

- Run any of the commands — operator drives the keyboard.
- Generate exploits or POCs — `rick_payload_guide` provides methodology, not weaponized code.
- Replace the full kill-chain walkthrough — use `/kill-chain-walk` for stateful phase work.

---

## Related skills

- `/arsenal-report` — picks tools for a target; this skill goes deep on one
- `/kill-chain-walk` — stateful phase work using the cheatsheets as references
