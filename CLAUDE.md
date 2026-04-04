# CLAUDE.md — Instructions for Claude Code

## What This Is

rick_mcp is a forkable MCP (Model Context Protocol) server for security professionals. It's a machine-readable identity
platform with 43 offensive/defensive security tools, 24 identity resources, and 7 persona modes. Built with FastMCP +
Pydantic v2.

## Architecture

```
rick_mcp.py              → Entry point (thin wrapper)
rick_mcp/
  server.py              → FastMCP instance, registration, banner
  identity.py            → Loads operator identity from ~/.rick_mcp/identity.yaml (zero internal imports)
  constants.py           → MISSION_PHASES, ResponseFormat enum
  formatting.py          → _fmt(), _sanitize(), _safe_tool(), _read_md(), _read_data()
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
    meta.py              → rick_status, rick_health, rick_demo, rick_mode, rick_capabilities
    jarvis_state.py      → Shared state persistence layer (load/save, snapshots, image validation, checklist templates)
    jarvis.py            → rick_full_auto, rick_kill_chain, rick_next_move, rick_sitrep (core intelligence layer)
    jarvis_extended.py   → rick_notes, rick_timeline, rick_compare, rick_scope_check, rick_export, rick_checklist, rick_tag, rick_rollback
  resources/
    profile.py           → 11 profile:// resources
    resume.py            → 4 resume:// resources
    docs.py              → 9 doc:// resources (reads from ~/.rick_mcp/soul/ first, fallback to project root)
  data/
    profiles/            → 11 markdown files (generic templates, overridden by ~/.rick_mcp/)
    resume/              → 4 markdown files
    docs/                → war_stories.md
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
make test        # Run 439 tests
make coverage    # Tests with 80% coverage minimum
make typecheck   # mypy rick_mcp.py --ignore-missing-imports --no-strict-optional
make fix         # Auto-fix lint and format
make smoke       # Fire every tool once
make setup       # Install deps, pre-commit hooks, create ~/.rick_mcp/
```

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
