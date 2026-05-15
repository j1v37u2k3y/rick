# The Build Story

## How Rick MCP Came to Be

It started with a question: *What if a resume could talk back?*

Not a PDF. Not a webpage. Not a profile that sits there waiting to be scrolled past. Something alive. Something
an AI could query, reason about, and use as a tool. Something that proves every claim it makes — not by listing skills,
but by demonstrating them.

Rick MCP was born in March 2026. A platform built on the idea that craft speaks louder than credentials.

## The Build

The first version was a single Python file. 3,800 lines of craft. FastMCP + Pydantic v2. 15 tools covering the full
pentest lifecycle — recon to debrief. 15 identity resources telling a professional story.

194 tests. 99% coverage. All passing in under a second.

Then it grew. The single file became a package. 15 tools became 22. Resources multiplied. A persona system emerged —
Rick stopped being a vending machine and became a presence. MCP prompts that pull live from structured content at
call time. Update the content, update Rick's voice.

Then came the intelligence layer. JARVIS. 22 tools became 38. Stateful 7-phase kill-chain tracking that persists
across conversations. Engagement notes with image evidence. Unified timelines. Phase-specific checklists. Rollback for
when the move was wrong. Rick stopped answering questions in isolation and started knowing where you were.

The engagement lifecycle filled in. Proposal → ROE → onboarding → tracker → debrief → report scaffolds — chainable,
all of it. Scope checks as safety rails. CVE lookups with NVD caching. Compatibility checks against job postings.
Cover letters tuned to three tones. Mentorship paths for 9 topics. The MCP became a working operator, not a reference.

Operator philosophy moved from Python literals into structured YAML. Decision trees in `rick_tool_recommend` and
`rick_threat_model` pull from the operator's values now, not hardcoded heuristics. Fork the philosophy without
touching code.

The vault came online. v3.10 — Rick became a contributor to an Obsidian Second Brain at `~/.rick_mcp/vault/`.
Engagement tools auto-write Rick-voice AI-first notes. Filesystem-canonical for the projection layer; JSON-canonical
for tracker state. Without the vault, every tool still works — writes gate on `vault.is_configured()` and degrade
silently. Fork-friendly to the bone. v3.11 added per-engagement read by codename with defense-in-depth path
containment.

v3.12 added the orchestration layer. Project-local Claude Code skills at `.claude/skills/` — engagement-kickoff,
kill-chain-walk, writeup-publish, voice-check, resume-tailor, and more. Each skill chains multiple MCP tools into
a higher-level workflow. They auto-discover when Claude Code launches from the repo. They're forkable. They're pure
orchestration — state lives in the server, not the playbook. Voice and register shifts stay server-side in the
persona prompts (`be_rick`, `mentor`, `evaluate`) — one source of truth, no skill-vs-server drift.

Pre-commit hooks blocking bad commits. GitHub Actions CI across Python 3.10, 3.12, and 3.14. mypy with zero errors.
ruff with security rules. Dependabot keeping deps fresh. `make check` — one command, full pipeline, green.

## What Rick Became

A webpage sits there and waits to be read. Rick responds.

Rick is a living system that an AI can query, reason about, and use as a tool. An LLM asks Rick for identity data
and gets structured results back. It queries values, methodology, and capabilities — all as resources an AI can
reason over. Dozens of functional tools *do things* — generate ROE docs, model threats, look up CVEs, track stateful
kill chains across sessions, project engagements into an Obsidian vault, compare C2 frameworks, generate cloud
attack paths, write detection rules, plan pivots, recommend tools, and write cover letters matched to job postings.

Claude Code skills chain those tools into workflows. Kick off an engagement and the SOW, ROE, onboarding packet,
and tracker handle land in one orchestrated pass. Walk the kill chain phase by phase with state persisting between
sessions. Publish writeups from completed engagements. Lint your prose for voice drift before shipping.

Most people send a PDF resume. Rick MCP is a running server that proves every claim it makes. `make check` and it
all lights up green.

See [CHANGELOG.md](CHANGELOG.md) for version-by-version details.

## The Numbers

Run `rick_capabilities` for live counts (tools, resources, skills, persona prompts) and the README headline for the
current totals at a glance. What matters more than the integers:

- Full CI/CD pipeline with Docker verification
- Integration tests through MCP protocol layer
- Property-based fuzz testing on all input models
- Content in markdown, not Python strings
- Private content support for sensitive files
- 24-hour CVE response cache
- Zero hardcoded secrets

## The Philosophy

The server IS the resume. The code IS the craft. The tests ARE the proof.

*Still building.*
