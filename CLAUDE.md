# CLAUDE.md — Instructions for Claude Code

## What This Is

rick_mcp is a forkable MCP (Model Context Protocol) server for security professionals. It's a machine-readable identity
platform with offensive / defensive security tools, identity resources (profile + docs + resume + vault), persona
prompts,
and forkable Claude Code skills. Built with FastMCP + Pydantic v2.

Live counts (tool / resource / skill / test totals + version) live in two places only: runtime via `rick_capabilities`,
and the README headline (auto-synced by `scripts/refresh_counts.py`). Don't hardcode counts here or in other internal
docs.

## MCP Tool Usage

When working with rick_mcp or jarvis projects, ALWAYS use the available MCP tools first (e.g., for
profile/identity/family queries) instead of falling back to Grep/Read on raw files. Check ToolSearch/ReadMcpResourceTool
before file-based exploration.

## Workflow

### Planning & Approval

For any non-trivial task (new feature, refactor, multi-file changes), present a brief plan and wait for approval BEFORE
editing or building. Do not start backend work, scaffolding, or exploratory builds without explicit confirmation.

## Architecture

```
rick_mcp.py              → Entry point (thin wrapper)
rick_mcp/
  server.py              → FastMCP instance, registration, banner
  identity.py            → Loads operator identity from ~/.rick_mcp/identity.yaml (zero internal imports)
  constants.py           → MISSION_PHASES, ResponseFormat enum
  formatting.py          → _fmt(), _sanitize(), _safe_tool(), _read_md(), _read_data()
  logging_config.py      → Structured logging setup
  prompts.py             → 7 prompt builders (be_rick, dick_mode, jarvis, pentest, mentor, evaluate, engagement)
  models/inputs.py       → Pydantic input models for all tools
  tools/
    offensive.py         → rick_recon, rick_vuln_assess, rick_tool_recommend
    offensive_chains.py  → rick_attack_chain, rick_pivot_plan (also registers offensive_tradecraft)
    offensive_extended.py → rick_c2_compare, rick_cloud_attack_path, rick_payload_guide, rick_wireless
    offensive_tradecraft.py → rick_cheatsheet, rick_threat_model
    defensive.py         → rick_hardening, rick_incident_response, rick_detection_rules, rick_log_analysis
    engagement.py        → rick_roe, rick_engagement_proposal, rick_client_onboarding, rick_report_template, rick_scoping, rick_debrief, rick_tracker
    career.py            → rick_compatibility_check, rick_cover_letter, rick_mentorship
    cve.py               → rick_cve (NVD API, 24hr file cache)
    recon_handle.py      → rick_recon_handle (GitHub/CTFTime/HTB OSINT, 24hr file cache)
    writeups.py          → rick_writeups (writeup search + citation cross-referencing)
    meta.py              → rick_status, rick_health, rick_demo, rick_mode, rick_mantra, rick_capabilities
    jarvis_state.py      → Shared state persistence layer (load/save, snapshots, image validation, checklist templates)
    jarvis.py            → rick_full_auto, rick_kill_chain, rick_next_move, rick_sitrep (core intelligence layer)
    jarvis_extended.py   → rick_notes, rick_timeline, rick_compare, rick_scope_check, rick_export, rick_checklist, rick_tag, rick_rollback
  resources/
    profile.py           → profile:// resources (operator identity surface)
    resume.py            → resume:// resources (machine-readable resume)
    docs.py              → doc:// resources (reads from ~/.rick_mcp/soul/ first, fallback to project root)
    vault.py             → vault:// resources (Obsidian Second Brain projection, optional)
  data/
    profiles/            → 11 markdown files (generic templates, overridden by ~/.rick_mcp/)
    resume/              → 4 markdown files
    docs/                → war_stories.md
.claude/skills/          → forkable Claude Code skills (auto-discover when launched from repo root)
  engagement-kickoff/    → Stand up a new client engagement (SOW → ROE → onboarding → tracker)
  htb-day/               → CTF / HTB kickoff variant (no SOW, just kill-chain)
  kill-chain-walk/       → Phase-by-phase guided op with state tracking — the daily driver
  debrief-then-publish/  → Engagement close-out: debrief + report scaffolds + timeline + export
  writeup-publish/       → Engagement → sanitized public writeup
  voice-check/           → Lint markdown for voice drift (sugar-coat, hedges, padding)
  arsenal-report/        → Target description → ordered tool plan by 7-phase methodology
  cheatsheet-build/      → Vuln class / attack stage → one-page pocket reference
  resume-tailor/         → Job posting → fit assessment + cover letter + resume tweaks
  SKILLS.md              → Catalog + composition patterns (read first when working on skills)
  SKILL_TEMPLATE.md      → Scaffold for new skills (copy into <skill-name>/SKILL.md)
```

## Key Patterns

- **Registration**: Each tool/resource module has a `register(mcp)` function called from `__init__.py`
- **Input models**: All tool inputs use Pydantic with `ConfigDict(str_strip_whitespace=True, extra="forbid")`
- **Output formatting**: Use `_fmt(data_dict, ResponseFormat, title=...)` for consistent output
- **Tool wrapping**: All tools are wrapped with `_safe_tool()` for error handling
- **Identity**: `rick_mcp/identity.py` loads from `~/.rick_mcp/identity.yaml`. Use `is_configured()` to check if custom
  identity exists. All prompts/tools must work with generic defaults (no identity.yaml).
- **Private content**: Soul files load from `~/.rick_mcp/soul/` first, project root second, then fallback string
- **JARVIS state**: Kill chain + mission log persists to `~/.rick_mcp/dick/` as JSON files

## Commands

```bash
make check       # Full pipeline: lint + format + typecheck + file-length + tests
make test        # Run the test suite
make coverage    # Tests with 80% coverage minimum
make typecheck   # mypy rick_mcp.py --ignore-missing-imports --no-strict-optional
make fix         # Auto-fix lint and format
make smoke       # Fire every tool once
make setup       # Install deps, pre-commit hooks, create ~/.rick_mcp/
```

## Python / Environment

Always use the project's venv (not global pip) in scripts like `start.sh`. Verify Python version compatibility (e.g.,
librosa requires <3.14) before installing audio/ML deps.

## Rules

- **Version**: Single source of truth in `__version__.py`. Tests should reference it dynamically, not hardcode.
- **File length**: Max 1500 lines per Python file. Enforced by pre-commit hook.
- **Pre-commit hooks**: trailing-whitespace, end-of-file, yaml/json check, large files, private keys, merge conflicts,
  ruff lint+format, mypy, pytest. All must pass.
- **New features get fresh version bumps**, not amends to previous releases.
- **Tests**: Every tool needs tests covering valid inputs, error cases, and both output formats. New tool files go in
  separate test files if `test_rick_mcp.py` would exceed 1500 lines.
- **Coverage**: 80% minimum enforced. New tools must include tests.
- **No hardcoded identity**: All personal data comes from identity.yaml or soul files. Python source stays generic.
- **Async**: All tools and resources are async functions.

## Claude Code Skills

Skills live at `.claude/skills/<skill-name>/SKILL.md`. They auto-discover when Claude Code launches in this repo. Skills
are committed and forkable — anyone who clones rick_mcp gets them. The catalog lives at `.claude/skills/SKILLS.md`; the
template scaffold for new skills lives at `.claude/skills/SKILL_TEMPLATE.md`.

### Authoring rules

- **Naming**: `kebab-case` directory names (`engagement-kickoff`, not `engagement_kickoff`). The `name` field in
  frontmatter matches the directory.
- **Frontmatter**: `name` (kebab-case, matches dir) + `description` (multi-line `>`-folded, includes trigger phrases).
  The description powers natural-language matching — be specific about purpose, triggers, and out-of-scope cases.
  Mention adjacent skills the user might also be thinking of so the matcher routes correctly.
- **Generic, not personal**: Skills must work for any user who forks rick_mcp. No `~/.rick_mcp/` hardcodes, no
  operator-specific wikilinks, no vault-frontmatter conventions baked in. Personal content (identity, vault, mantras)
  loads via the `rick_mcp/identity.py` `is_configured()` pattern.
- **Pure orchestration**: Skills call MCP tools and return content to chat. Do not write to the operator's filesystem.
  State persistence happens inside the MCP server (`rick_kill_chain`, `rick_notes`, `rick_tracker`).
- **Voice via composition**: Skills stay in operational voice. Voice / register shifts live in the MCP server's persona
  prompts (`prompts.py`), not in skills. Invoke them via `rick_mode(persona="be_rick" | "mentor" | "evaluate" | ...)`.
  One source of truth for voice, no drift between channels.
- **Decision points**: Non-trivial skills use `AskUserQuestion` at every config decision point. Plan-first cadence
  applies to skills too.

### Skill body structure (recommended order)

1. Prerequisites (MCP tools / external deps)
2. Inputs required (with `AskUserQuestion` defaults)
3. Workflow (numbered steps with concrete tool calls)
4. Acceptance criteria
5. Failure modes
6. Voice rules (if applicable)
7. What this skill does NOT do
8. Related skills

### Adding a new skill

1. Copy `.claude/skills/SKILL_TEMPLATE.md` into `.claude/skills/<skill-name>/SKILL.md` and fill in the placeholders.
2. Append a row to `.claude/skills/SKILLS.md` under the appropriate category with the trigger phrases.
3. Run `make check` to confirm nothing else broke.
4. Commit (no `Co-Authored-By` trailer per project convention).

## File Editing

When asked to clear or reset JSON/data files, use Write to produce a proper rewritten file rather than Edit to blank
contents. Respect intentionally-separated files (e.g., personal vs shared mantras) — do not merge them unless explicitly
told to.

## Git / Commit Conventions

Do NOT add Claude co-author lines or "Generated with Claude" footers to commit messages. Keep commits clean and
attributed only to the user.

## Adding a Tool

1. Create Pydantic input model (in the tool file or `models/inputs.py`)
2. Write the async tool function
3. Add `register(mcp)` entry with annotations (title, readOnlyHint, etc.)
4. Wire into `tools/__init__.py` (import + register_all + __all__)
5. Add tests
6. Update `rick_capabilities` in `meta.py`
7. Update README tool table
8. Update CHANGELOG.md
9. Bump version in `__version__.py`

## Project Identity

- The server is called `rick_mcp`, not `tom_mcp`
- Rick is the father, jiveturkey is the son. The MCP is Rick.
- Dick is the alter ego — elite tradecraft, 1337, opens all the doors
- The soul (SOUL.md) governs everything — honor, courage, commitment, do no harm
