---
type: vault-manual
ai-first: true
---

## For future Claude

This is the **vault operating manual** — the first file Claude (or any AI) should read when
operating against this vault. It defines folder semantics, frontmatter conventions, and the
AI-first rule that governs note creation.

This file is a **stub example** that ships with `soul-example/vault/`. When a forker copies
the example, this file becomes their starting `_CLAUDE.md`. They evolve it as their vault
grows; the `obsidian-second-brain` skill can regenerate / extend it.

# Vault Operating Manual

This Obsidian vault is the operator's Second Brain. The rick_mcp server reads from it via
`vault://` resources and writes engagement notes into `Engagements/` via the engagement
tools (proposal, ROE, onboarding, debrief, tracker).

## Folder semantics

- `Identity/` — operator identity surface: hub file (`<NAME>.md` or `Operator.md`),
  plus bridge stubs for soul, values, methodology, mantras, and the father-son frame
  (`Rick.md`). The hub aggregates; the stubs point at canonical sources outside the vault
  (`~/.rick_mcp/soul/`, `~/.rick_mcp/profiles/`).
- `Engagements/` — one note per engagement. Two shapes:
  - **Proposal-shape**: named `<Client> - <Type Title> (<YYYY-MM-DD>).md`, written by
    `rick_engagement_proposal`. ROE, onboarding, and debrief sections append to the same
    file.
  - **Tracker-shape**: named `<ENG-ID>.md`, written by `rick_tracker create`. JSON state
    lives at `~/.rick_mcp/engagements/<ENG-ID>.json`; the vault file is the human-readable
    mirror.
- `Templates/` — Obsidian templater templates for fast note creation.
- `index.md` — vault catalog, organized by folder.
- `log.md` — chronological activity log (bootstrap, structural changes, ingests).

## AI-first rule

Every note in this vault is written for **future Claude retrieval**, not human reading.
That means:

1. **`## For future Claude` preamble** — top of every note. 10-second orientation: what is
   this, why does it exist, where does the canonical content live.
2. **Rich frontmatter** — at minimum: `type`, `ai-first: true`. Type-specific fields per
   the note's shape (`date` for daily, `status` for tasks, `canonical-source` for bridge
   stubs).
3. **Mandatory `[[wikilinks]]`** — every person, project, concept gets a wikilink. The
   graph is the index.
4. **Sources preserved verbatim** — quoted blocks with URLs inline. Don't paraphrase
   external claims.
5. **Recency markers** — date-stamp every claim that could go stale.

## What lives where (read-side resources)

- `vault://manual` → this file
- `vault://index` → `index.md`
- `vault://log` → `log.md`
- `vault://identity/hub` → `Identity/<NAME>.md` (falls back to `Identity/Operator.md`)
- `vault://identity/soul` / `values` / `methodology` / `mantras` / `rick` → bridge stubs
- `vault://engagements` → JSON list of engagement notes
- `vault://engagements/{codename}` → single engagement note by filename stem
- `vault://templates/engagement` → `Templates/Engagement.md`
- `vault://status` → vault health (JSON)
