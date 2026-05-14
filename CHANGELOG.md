# Changelog

All notable changes to rick_mcp will be documented in this file.

## [3.11.0] - 2026-05-14

### Per-engagement MCP resource — `vault://engagements/{codename}`

Pulling a single engagement note by codename now works. Filesystem-resolved, consistent with
the existing `vault://engagements` list resource.

- **New resource** `vault://engagements/{codename}` (parameterized URI template) — reads
  `vault/Engagements/<codename>.md` directly. Returns:
  - File content when the codename matches a file stem.
  - A missing-codename stub listing available codenames as a hint when the codename doesn't match.
  - The standard "not available" stub when the vault is not configured.
- **Works for both engagement shapes:**
  - Proposal-shape notes (created by `rick_engagement_proposal`, named
    `<Client> - <Type Title> (<Date>).md`).
  - Tracker-shape notes (created by `rick_tracker create`, named `<ENG-ID>.md`).
- **Filesystem-canonical for the resource layer** — mirrors how `vault://engagements` (the
  list) already resolves. Proposal-shape notes have no native JSON state, so no backfill is
  manufactured. Tracker JSON at `~/.rick_mcp/engagements/<ENG-ID>.json` remains canonical for
  tracker-driven state mutations (findings, status); the vault file is the read surface.
- **No changes** to `rick_tracker` semantics, `vault://engagements` (list), or
  `rick_capabilities` output (the `{codename}` URI was already documented at
  `rick_mcp/tools/meta.py:570-571` — now accurate).
- **Tests**: 5 new cases in `tests/test_vault.py::TestVaultResources` covering unconfigured
  vault, missing codename, proposal-shape read, tracker-shape read, and not-found hint
  enumeration.

### Notes for future Claude

The original 2026-05-14 brief diagnosed yesterday's `Unknown resource` failures as a
tracker-JSON-vs-filesystem split needing a JSON backfill. Verify-premise step found the actual
root cause was simpler: `vault://engagements/{codename}` was never a registered resource (only
`vault://engagements` was). The list and capabilities count both already trusted the
filesystem and agreed — there was no split. Fixing the missing registration restored the pull
without manufacturing JSON for proposal-shape notes that have no native JSON state.

## [3.10.0] - 2026-05-09

### Vault Integration — Rick Becomes a Vault Contributor

Rick MCP now natively writes to the operator's Obsidian Second Brain at `~/.rick_mcp/vault/`.
When the vault is bootstrapped (detected by presence of `_CLAUDE.md`), engagement tools auto-write
Rick-voice AI-first notes to `vault/Engagements/`. Fork-friendly: tools degrade gracefully when no
vault is configured — text-only output, no errors, no surprises.

- **New module** `rick_mcp/vault.py` — parallel to `identity.py`. Zero internal imports, loads path
  config at import time, exposes module-level constants. `is_configured()` gates every behavior.
  Helpers:
  - `frontmatter(fields)` — builds AI-first YAML with space-padded inline arrays (`tags: [ a, b ]`)
    matching the operator's vault formatting preferences.
  - `preamble(text)` — builds the `## For future Claude` block.
  - `write_engagement(codename, ...)` — non-destructive by default; pass `overwrite=True` to refresh.
    Returns `(path, created)` tuple.
  - `append_engagement_section(codename, heading, body)` — appends a dated section to an existing
    engagement note.
  - `append_log_entry(action, description)` — chronological vault/log.md append.
  - `specialization_wikilink()` / `tools_wikilinks()` — engagement-type → vault Identity wikilinks.
  - `status()` — health view used by `rick_capabilities`.
- **Engagement tools wired** to vault writes:
  - `rick_engagement_proposal` — creates `vault/Engagements/<Client - Type (Date)>.md` anchor with
    Rick-voice body. Wikilinks to `[[Identity/Methodology]]`, `[[Identity/Specializations/...]]`,
    `[[Identity/Tools/...]]`. Non-destructive: existing note preserved on re-run.
  - `rick_debrief` — appends a `Debrief` section to the matching engagement note (best-effort match
    by client+type prefix). Falls through to text-only when no match.
  - `rick_roe` — appends a `Rules of Engagement` section.
  - `rick_client_onboarding` — appends a `Client Onboarding` section.
  - `rick_scoping` — logs calculator runs to `vault/log.md` (no client→note matching available
    from ScopingInput).
  - `rick_tracker` — projects engagement state to `vault/Engagements/<eng_id>.md`. The JSON state at
    `~/.rick_mcp/engagements/<eng_id>.json` remains canonical; the vault note is regenerated on
    every `create`, `add_finding`, and `update_finding` action via `overwrite=True`. Includes
    dynamic findings table + severity breakdown.
- **`rick_capabilities`** gains a `vault_integration` section surfacing vault status (configured,
  path, engagement count) and the auto-write tool list.
- **New `vault://` MCP resources** (11):
  - `vault://manual` — `_CLAUDE.md`
  - `vault://index` — vault catalog
  - `vault://log` — chronological activity log
  - `vault://identity/tom` / `methodology` / `values` / `soul` / `rick` — identity stubs
  - `vault://engagements` — JSON list of all engagement notes
  - `vault://templates/engagement` — Templater-based engagement template
  - `vault://status` — JSON health view
- **Test isolation** — new `tests/conftest.py` with autouse fixture patching `Path.home()` to a
  fresh `tmp_path` for every test. Prevents tools that write to `~/.rick_mcp/{vault,engagements,
  dick}` from polluting the operator's real home during test runs. Catches a real leak that was
  silently writing to `~/.rick_mcp/vault/log.md` when engagement tools ran in tests.
- **Tests** — new `tests/test_vault.py` (64 tests) covering the vault module, AI-first frontmatter
  helpers, write/append primitives, find-by-prefix lookup, and all 11 vault:// resources.
  `tests/test_extended.py::TestEngagementVaultIntegration` adds 10 tests covering each engagement
  tool's vault behavior (write, append, no-match fallback, tracker findings refresh).
- **Architectural rule** documented in `vault.py`: vault references bedrock (`soul/`, `profiles/`,
  `resume/`, `identity.yaml`); bedrock is never duplicated in the vault. If a stub diverges from
  canonical, canonical wins.
- **Voice**: when `is_configured()` is true (custom identity loaded), vault note bodies carry Rick's
  voice — first person, builder metaphors, USMC precision, dry humor. AI-first structural rules
  (preamble, frontmatter, wikilinks, recency markers) apply regardless of voice.
- **Zero new dependencies.** Uses stdlib `pathlib` + existing `pyyaml`.

---

## [3.9.0] - 2026-05-07

### Philosophy-Aware Tool Output — Decision Tree Framework

- **New data file** `rick_mcp/data/philosophy.yaml` — operator-facing philosophy as data, not code. Three top-level sections:
  - `core_principles` — 7 soul values (Do No Harm, Integrity First, Continuous Improvement, Teach What You Know, Measure Twice Hack Once, Accountability, The Craft) with operational meanings.
  - `decision_filters` — 9 active constraints (Thorough > Fast, Manual > Scanner, Honesty above all, Builder's eye first, Cycle breaker, No checkbox compliance, Chain over isolation, Builder metaphor, Mantras when stuck) with trigger keywords for keyword-based matching.
  - `validation_rules` — 5 RoE rules (authorized targets, 1hr critical escalation, severity+PoC+impact+remediation, reproducibility, no-DoS-without-approval).
- **Override path** — `~/.rick_mcp/philosophy.yaml` overrides the bundled defaults, mirroring the `identity.yaml` pattern. Philosophy stays out of Python source.
- **New module** `rick_mcp/philosophy.py` — YAML loader + structural dispatch tables. Loads override → bundled → minimal-baseline. Code-side (not data) tables stay in Python because they're framework code-shape, not operator philosophy:
  - `METHODOLOGY_GATE_KEYWORDS` — scenario keywords → MISSION_PHASES name.
  - `ARSENAL_CHAIN` — situation → next-tool chain (mirrors the JARVIS arsenal table at `prompts.py:686-700`).
  - `STRIDE_PRINCIPLE_ANCHORS` + `STRIDE_FILTER_MAP` — STRIDE pillar → governing principles + filters (slug references into the YAML).
  - `chain_validation` — STRIDE → chain-framing prose.
- **`rick_tool_recommend` upgraded** — output now carries `decision_filters_applied`, `methodology_gate`, `validation_checklist`, and `chain_to`, all derived from the philosophy module instead of being implicit in prose.
- **`rick_threat_model` upgraded** — every STRIDE category now ships with `decision_filters`, `chain_validation`, and `core_principle_anchors`. The architecture is no longer a flat lookup; each pillar declares the soul values, the filters, and the chain-framing note that govern its branches.
- **Tests** — new `tests/test_philosophy.py` (~50 tests) covering YAML loading + override precedence, the module's data shape, helper functions (`apply_filters`, `infer_methodology_gate`, `chain_for`, `principle_anchors`, `chain_validation`, `filters_for_stride`), and end-to-end wiring into both tools across markdown + JSON formats.
- **Out of scope this release**: wiring filters into `rick_attack_chain`, `rick_kill_chain`, `rick_next_move`, `rick_vuln_assess`. Follow-up bump.

---

## [3.8.0] - 2026-05-02

### Operator Philosophy Layer — Prompts That Reason Like Tom

- **`build_jarvis()` expanded** — JARVIS now reasons *like* the operator, not just *about* them. Adds two new sections to the prompt:
  - **Operator Philosophy** — embeds 6 profile files (`values`, `craftsmanship`, `heritage`, `human`, `mantras`, `rick_and_jiveturkey`) as the lenses every recommendation must pass through. Previously only `summary`, `stack`, `methodology` were loaded.
  - **Decision Filters** — translates philosophy into prescriptive JARVIS rules: *Thorough > Fast*, *Manual depth > Scanner output*, *Honesty above all*, *Builder's eye first*, *Three boys watching*, *Cycle breaker*, *No checkbox compliance*, *Chain over single-vuln framing*, *Builder metaphors as native register*, *Mantras surface when stuck*.
- **`build_be_rick()` and `build_mentor_mode()`** also gain the **Operator Philosophy** section, so the foundation and the mentorship voice carry the same distilled principles JARVIS uses. Decision Filters stay JARVIS-only — they're tactical rules, not voice.
- **New shared helper** `_operator_philosophy_section()` keeps the 6 reads in one place, used by all three builders.
- **Other prompts unchanged** — `dick_mode`, `pentest_mode`, `evaluate_fit`, `engagement_ops` deliberately skip the section (tactical or evaluative contexts where the structured philosophy doesn't fit).
- **No new dependencies.** Reuses existing `_read_data()`. Backward-compatible — generic fallback path still works without `~/.rick_mcp/profiles/` overrides.
- **Tests**: new `tests/test_prompts.py` (23 tests) covering JARVIS philosophy + filters, be_rick philosophy + no-filters guard, mentor_mode philosophy + no-filters guard, and explicit "still untouched" guards for dick_mode/pentest_mode/evaluate_fit/engagement_ops.

---

## [3.7.0] - 2026-04-26

### Handle Reconnaissance Tool

- **New tool**: `rick_recon_handle` — OSINT against a hacker handle. Returns a structured JSON profile from public sources. Default response format is JSON (machine-readable, chain-friendly).
- **GitHub** (load-bearing wall): real REST API fetch for `/users/{h}`, `/users/{h}/repos`, and `/users/{h}/events/public` — profile fields, top 5 starred non-fork repos, top 5 languages, recent activity count. Optional `github_token` raises rate limit 60/hr → 5000/hr.
- **CTFTime**: optional `ctftime_id` triggers direct enrichment via `/api/v1/users/{id}/` (team, ranking). Without an ID, returns a search URL — CTFTime's API requires numeric IDs, not handles.
- **HackTheBox**: returns the public profile URL with a note that programmatic enrichment requires an API token.
- **Search pivots** (URLs only, no scraping): HackerOne, Bugcrowd, Mastodon (infosec.exchange), Google dorks for blogs and conference talks, LinkedIn search.
- **Cache**: 24hr file cache at `~/.rick_mcp/handle_cache/` (sha256-keyed by URL), mirroring `rick_cve`'s pattern.
- **Soul-bounded**: `authorization` field on every output, public sources only, no email harvesting, no doxxing, no paid OSINT brokers, graceful degrade when sources fail.
- 46 tools total (up from 45).

---

## [3.6.0] - 2026-04-16

### Writeups as Reference Material

- **New action**: `rick_writeups(action='index')` — corpus intelligence. Scans all write-ups, extracts top 20 tools mentioned, CVEs (regex `CVE-YYYY-NNNNN`), MITRE technique IDs (regex `T\d{4}`), and Linux/Windows OS breakdown. Cached to `.index.json` with 24hr TTL.
- **Cross-referencing**: 6 existing tools now cite your writeups alongside theoretical guidance:
  - `rick_cheatsheet` — "Seen in your writeups: [paths]" cites boxes where you used the tool
  - `rick_recon` — cites writeups matching the target type (AD, cloud, web, etc.)
  - `rick_vuln_assess` — cites writeups demonstrating the vulnerability category
  - `rick_attack_chain` — cites writeups showing the scenario's techniques
  - `rick_pivot_plan` — cites writeups matching the compromised position
  - `rick_tool_recommend` — cites writeups featuring the top recommended tool
- **New exported helper**: `cite_writeups(term, limit=5)` — used by any tool that wants citation support. Silent when no writeups exist (generic output unchanged).
- Citation uses ripgrep for speed, falls back to pure-Python grep. Dedupes by file so the same writeup isn't cited twice.

---

## [3.5.0] - 2026-04-15

### Operator Writeups Tool

- **New tool**: `rick_writeups` — browse, read, and keyword search operator write-ups from `~/.rick_mcp/writeups/`
- **Actions**: `list` (enumerate by category), `read` (fetch one file), `search` (ripgrep with Python fallback)
- Nested directory support — organize by `htb/`, `ctf/`, `engagements/`, or any category structure
- Path traversal hardening — `resolve()` + `is_relative_to()` rejects escape attempts
- Search uses ripgrep for speed, falls back to pure-Python when `rg` is unavailable
- **Soul example**: added `writeups/` directory with HTB and CTF examples
- 45 tools total (up from 44)

---

## [3.4.0] - 2026-04-10

### Random Mantra Tool

- **New tool**: `rick_mantra` — pulls a random mantra from the operator's stored mantras. One per call. Reads from `~/.rick_mcp/profiles/mantras.md` at runtime.
- 44 tools total (up from 43)

---

## [3.3.0] - 2026-04-02

### JARVIS Intelligence Layer Expansion

- **8 new tools**: `rick_notes`, `rick_timeline`, `rick_compare`, `rick_scope_check`, `rick_export`, `rick_checklist`, `rick_tag`, `rick_rollback`
- **Image attachments**: `rick_notes` and `rick_kill_chain` add_finding support image path references (png, jpg, gif, svg, pdf, webp)
- **Scope safety rail**: `rick_scope_check` stores in-scope targets and ROE, validates before you touch anything
- **Engagement comparison**: `rick_compare` diffs two engagements side by side for retests
- **Export**: markdown, JSON, CSV — report-ready output from any engagement
- **Phase checklists**: auto-generated by target type with 8 environment-specific templates
- **Finding tags**: severity, category, MITRE ATT&CK technique IDs on any finding
- **State rollback**: automatic snapshots before mutations, undo with `rick_rollback`
- **Architecture**: split `jarvis.py` into `jarvis_state.py` (shared persistence), `jarvis.py` (core 4 tools), `jarvis_extended.py` (8 new tools)
- **Input models**: all JARVIS models moved to `models/inputs.py` — consistent with project convention
- 43 tools total (up from 35)
- 512 tests total (up from 449)

---

## [3.2.0] - 2026-03-23

### JARVIS — The Intelligence Layer

- **New mode**: `jarvis` — master prompt that turns Claude into a proactive orchestrator with automatic tool chaining, kill chain tracking, and situational awareness
- **New tool**: `rick_sitrep` — Situation Report. One command, full tactical picture: kill chain progress, findings, mission log, tool history, tactical assessment
- **Enhanced state model**: engagement JSON now tracks `mission_log`, `tool_history`, `notes`, and `objective`
- Three new state helpers: `_add_mission_log()`, `_add_tool_history()`, `_add_note()`
- `rick_full_auto` now auto-populates mission log and tool history on engagement creation
- `rick_kill_chain` add_finding and advance now auto-log to mission log
- JARVIS prompt embeds operator identity (soul, summary, stack, methodology) for full context from activation
- 7 modes total (added `jarvis`)
- 35 tools total (added `rick_sitrep`)
- 449 tests total

---

## [3.1.0] - 2026-03-22

### Dick Mode + JARVIS Tools — The Alter Ego

- **New persona**: `dick_mode` — elite tradecraft alter ego with 1337 principles, full arsenal, zero hesitation
- **New tool**: `rick_full_auto` — give a target, get the complete playbook (recon → vuln → attack chain → tools →
  pivot) chained automatically
- **New tool**: `rick_kill_chain` — stateful 7-phase kill chain tracker, persisted to `~/.rick_mcp/dick/`, survives
  across conversations
- **New tool**: `rick_next_move` — JARVIS-level situational awareness, analyzes position + findings + kill chain state,
  recommends next actions
- 6 modes (added `dick_mode` to `AVAILABLE_MODES` and `MODE_BUILDERS`)
- 34 tools total (up from 31)
- `rick_capabilities` updated with new `dick_mode_tools` category
- mypy added to pre-commit hooks — type errors can no longer slip through
- `types-PyYAML` added to dev dependencies
- `test_dick.py` — 33 new tests covering all Dick tools, helpers, and input validation
- `test_be_rick_mode` fixed to work without `identity.yaml` (CI-safe)
- 439 tests total (up from 406)

---

## [3.0.0] - 2026-03-22

### Identity Extraction — Rick Becomes a Platform

- **BREAKING**: All personal identity extracted from codebase
- New `rick_mcp/identity.py` — loads operator identity from `~/.rick_mcp/identity.yaml`
- `constants.py` imports identity dynamically (CALLSIGN, CERTIFICATIONS, etc.)
- All prompts, tools, and resources use identity config with generic fallbacks
- `_read_data()` checks `~/.rick_mcp/` first for private content, bundled data as fallback
- All 16 data markdown files replaced with generic placeholders
- `soul-example/` directory with 21 template files for identity setup
- Server banner dynamically built from identity config
- New dependency: `pyyaml>=6.0`
- Zero personal data in Python source — confirmed via grep audit
- 406 tests pass with generic defaults (no identity.yaml required)
- Rick works out of the box. Identity makes it yours.

---

## [2.0.1] - 2026-03-22

### Quality of Life

- `rick_demo` updated to showcase v2 tools (C2 compare, IR, detection rules, log analysis, scoping)
- `rick_demo` now fires 13 tools across all categories (up from 8)
- All hardcoded tool/resource counts in Python replaced with dynamic `tool_count()` / `resource_count()`
- `make setup` — one-command dev environment (deps, pre-commit hooks, private content directory)
- README updated with soul file setup instructions and full v2 tool tables
- Pre-commit YAML fixed for file-length hook compatibility

---

## [2.0.0] - 2026-03-22

### The Full Build — 31 Tools, 25 Resources, 406 Tests

#### New Offensive Tools

- `rick_c2_compare` — C2 framework comparison (Cobalt Strike, Sliver, Mythic, Havoc)
- `rick_payload_guide` — Payload methodology guide mapped to MITRE ATT&CK
- `rick_cloud_attack_path` — Cloud-specific attack paths for Azure, AWS, GCP
- `rick_wireless` — Wireless attack playbooks (WiFi, Bluetooth, RFID)

#### New Defensive Tools

- `rick_incident_response` — IR playbooks for 5 incident types
- `rick_detection_rules` — Sigma/YARA rule templates for 6 attack patterns
- `rick_log_analysis` — Log review methodology for 6 log sources

#### New Engagement Tool

- `rick_scoping` — Engagement scoping calculator (hours, team size, rate card, timeline)

#### New Resources

- `doc://war-stories` — Anonymized engagement narratives from the field
- `profile://timeline` — Career timeline from USMC barracks to offensive security

#### Code Quality

- Type annotations for `_fmt()` — `dict[str, Any]`
- CVE caching — file-based 24-hour TTL cache for NVD API responses
- Tracker export formats — `export_csv` and `export_markdown` actions

#### Testing & CI

- Integration tests — MCP protocol-level tool invocation (tests/test_integration.py)
- Hypothesis fuzz tests — property-based testing on input models (tests/test_fuzz.py)
- Docker build verification in CI pipeline
- Dockerfile fixed to include full package directory
- 406 tests total (up from 285)

---

## [1.0.0] - 2026-03-16

### Initial Public Release

- 22 functional tools covering the full pentest lifecycle
- 22 identity resources (profile, resume, docs)
- 5 MCP prompts — `be_rick`, `pentest_mode`, `mentor_mode`, `evaluate_fit`, `engagement_ops`
- `rick_mode` tool — prompt content accessible in Claude Code
- `rick_demo` tool — guided tour fires 8 tools in one command
- `rick_health` with self-healing — `fix=True` creates missing dirs, quarantines corrupt JSON
- `rick_cve` — Live NVD CVE lookup
- `rick_tracker` — Stateful engagement tracker (create, findings, export)
- Content served from markdown data files — no hardcoded strings in Python
- Private content support (`~/.rick_mcp/soul/`) for sensitive files
- 285 tests, full CI/CD pipeline (GitHub Actions, pre-commit, ruff, mypy)
- Dockerfile for containerized deployment
- Modular package architecture (`rick_mcp/`)

---

*I'm still building. Are you?*
