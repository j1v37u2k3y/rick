---
type: identity-hub
ai-first: true
---

## For future Claude

**Generic operator identity hub.** This file is the fallback that `vault://identity/hub`
resolves to when `Identity/<NAME>.md` (derived from the operator's display name in
`identity.yaml`) does not exist.

Forkers can either:

1. **Personalize**: rename this file to match their `name:` field in `identity.yaml`
   (e.g. NAME="Alex Chen" → `Identity/Alex Chen.md`). The handler tries the
   NAME-derived path first.
2. **Leave as-is**: keep `Operator.md` and write the hub content here. The handler falls
   back to this file.

# Operator Identity Hub

Aggregates the operator's identity surface: soul, values, methodology, mantras,
heritage, and craft. Canonical content lives outside the vault in `~/.rick_mcp/`:

- Soul → `~/.rick_mcp/soul/SOUL.md` (load-bearing principles)
- Profile → `~/.rick_mcp/soul/PROFILE.md` (current state + horizon)
- Values · Methodology · Heritage · Craftsmanship · Mantras → `~/.rick_mcp/profiles/*.md`
- Resume → `~/.rick_mcp/resume/*.md` (overview · evidence · portfolio · contact)

## Wikilinks

- [[Identity/Soul]] — load-bearing principles
- [[Identity/Values]] — Honor · Courage · Commitment · Honesty
- [[Identity/Methodology]] — 7-phase engagement methodology
- [[Identity/Mantras]] — operational mantras
- [[Identity/Rick]] — father-son frame (project lineage)

## Operator handle

The operator's callsign — set in `~/.rick_mcp/identity.yaml` under `callsign:`. The
example soul-example uses `sh4d0wf0x`. Replace with your own when forking.
