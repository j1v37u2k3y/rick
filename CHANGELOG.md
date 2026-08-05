# Changelog

All notable changes to rick_mcp will be documented in this file.

## [3.14.3] - 2026-08-05

### Fix: cap `mcp` below 2.0.0 — fresh installs were silently broken

`requirements.txt` pinned `mcp[cli]>=1.28.1` with no upper bound, so a fresh dependency resolve pulled
**mcp 2.0.0**, which removed the bundled `mcp.server.fastmcp` module that `rick_mcp/server.py` imports. The
result was a `ModuleNotFoundError` on import — breaking server startup, `pytest` collection, and any new
`make setup` or fork. `main`'s CI stayed green only because its last run predated the 2.0.0 release.

- **Capped `mcp[cli]>=1.28.1,<2.0.0`.** Resolves to mcp 1.x, which still ships the bundled FastMCP 1.x the
  server imports — restoring clean collection and startup. No source changes.
- Migrating the server onto standalone **FastMCP 2.x** (to take mcp 2.x and drop the cap) is tracked in #81.

## [3.14.2] - 2026-07-11

### Bug fixes surfaced by the behavioral-verification pass (epic #35)

Three defects the verification campaign caught that the unit tests were green on — the audit
judged tool *behavior* against real inputs, not just structure.

- **`rick_scope_check` now does CIDR matching (#61).** A target IP inside an authorized CIDR
  (e.g. `10.10.10.99` in `10.10.10.0/24`) was flagged OUT OF SCOPE — matching was
  substring/wildcard only. Added IP/network-aware membership via `ipaddress`, falling back to the
  existing hostname/wildcard logic; a bare-IP scope item is treated as `/32` (no substring bleed).
- **`rick_rollback` actually works now (#60).** Nothing ever created a snapshot, so rollback
  always reported "No snapshots available." Every `rick_kill_chain` mutation (`advance`,
  `add_finding`, `reset`) now captures a pre-mutation snapshot, so rollback restores prior state.
- **`rick_demo` no longer mutates the vault (#58).** The guided tour fired `rick_scoping`, which
  logged to `vault/log.md` on every run. Demo now runs under a `suppress_vault_writes` context so
  it shows live output without writing to the operator's Second Brain.

## [3.14.1] - 2026-06-26

### `rick_code_review` rubric is now overridable data

The review rubric (scoring dimensions + language notes) moves out of a Python literal into a
bundled YAML data file with a `~/.rick_mcp/` override path — the same two-layer pattern
`rick_mcp/philosophy.py` already uses for operator philosophy. A fork can now retune the
rubric (add language notes, adjust inspect/flag lists) by dropping in a
`~/.rick_mcp/code_review.yaml` instead of editing source.

- **`rick_code_review`** — `_DIMENSIONS` and `_LANGUAGE_NOTES` now load from
  `rick_mcp/data/code_review.yaml` (override → bundled → minimal-baseline fallback, with a
  pyyaml-missing guard). Default output is byte-identical to before (the rubric was ported
  verbatim); with no override present, the bundled file is the source of truth. The tool
  function stays pure — the load happens once at import, not per call.
- **Voice stays in code.** The voiced scales (severity / verdict / scoring / inspection
  method / closing note) remain Python literals — voice register, not rubric data. No
  fleet-wide voice extraction.

## [3.14.0] - 2026-06-21

### `rick_cognitive_appraisal` tool — defense-first cognitive-appraisal scaffold

A clean-room, defense-first cognitive-appraisal **reasoning scaffold** built entirely from
public-domain appraisal theory — owing nothing to any copyleft source. Be clear on what it
is: like `rick_code_review`, it does not analyze on its own. It echoes the in-scope input,
lays out the framework, and imposes a structure the caller (a person or the model) fills in.
The tool's deterministic work is the structure, the mode gate, and an input short-circuit;
the reasoning quality is the filler's.

- **`rick_cognitive_appraisal`** — for a `(subject, situation)` pair it emits a per-concern
  scaffold: the published appraisal checks (relevance · congruence · agency/blame ·
  certainty · coping potential) → a predicted response tendency. The output **contract**
  requires every concern to cite its evidence span, every line to carry a confidence level
  (`stated / high / medium / speculation`), and every prediction to carry a refutation
  condition — requirements the scaffold imposes on the filler, not properties the tool can
  verify after the fact.
- **Defense-first, with an operator-set red-team gate.** `mode="defense"` (default) emits
  the defensive brief (lever exposed + detection / hardening). `mode="redteam"` emits a
  pretext-*design* contract — not a ready-to-send lure — and only when the named engagement
  carries a non-empty scope (the same `rick_scope_check` flag). This is **deliberate
  friction and an intent signal, not access control**: the scope flag lives in a local file
  the operator controls and can set themselves. No scope → defense-only + a one-line reason.
- **What the tool actually enforces (code + tests):** the mode gate; a fabrication
  short-circuit that returns "insufficient evidence" when the input has no real content (so
  it can't be coaxed into inventing an entire appraisal from nothing); deterministic output
  structure; statelessness (nothing stored or profiled); and **no** benchmark / SOTA claim
  anywhere — the lens makes no capability claim by design.
- **What it relies on the caller to honor:** sourcing each concern to a genuine span (the
  tool cannot confirm a cited span is real), and the hard-refusal policy (named
  non-consenting individuals, vulnerable populations, coercion/harm of real people). A
  coarse keyword tripwire downgrades the red-team path to defense-only on obvious
  coercion/vulnerable terms — a speed bump, easily reworded around, not a real filter.
- **Basis:** Ortony/Clore/Collins (1988, OCC), Lazarus (1991), Scherer (Component Process
  Model). Public theory, our own vocabulary. New `cognitive_appraisal` category in
  `rick_capabilities`.
- **Tests** — new `tests/test_appraisal.py`: input validation, the gating matrix
  (unauthorized → defense-only; scoped engagement → pretext path; coercion/vulnerable terms
  → downgraded), the insufficient-evidence short-circuit, presence of the
  confidence/refutation contract, deterministic structure, both output formats, and the
  no-benchmark / clean-room-vocabulary checks. The tests cover the deterministic plumbing —
  they do not (and cannot) grade the quality of a filled-in appraisal.

## [3.13.0] - 2026-06-07

### `rick_code_review` tool + `/rick-review` skill — point Rick at a codebase

Rick can now give an honest, builder's-eye verdict on a codebase — craftsmanship, security, and
architecture — in his own voice. Split the way every other capability here is split: a pure-function
tool exposes the standard, a skill does the agentic work.

- **`rick_code_review`** — the builder's-eye **scoring & verdict rubric**. Three dimensions
  (craftsmanship / security / architecture), a severity scale (🔴/🟡/🟢), a verdict scale
  (Ship it → Redesign the foundation), the builder-to-breaker inspection method, and language-specific
  notes. A pure function: it emits the standard, it does not read files. `focus` lens + optional
  `language` hint; markdown / JSON output. New `code_review` category in `rick_capabilities`.
- **`/rick-review`** skill — a **hybrid orchestrator + voice layer**, not a from-scratch analyzer.
  If there's a diff or PR, it delegates the heavy analysis to Claude Code's built-in `code-review`
  (bugs + reuse/simplification/efficiency) and `security-review`, then re-prioritizes and re-voices
  the findings through the rubric. If it's a cold repo, Rick walks the load-bearing files himself.
  Security depth via `rick_vuln_assess` / `rick_threat_model`; voice via
  `rick_mode(persona="be_rick")`. Advisory only — recommends fixes, never auto-applies; never
  auto-runs the billed `ultra` pass.
- **Tests** — new `tests/test_code_review.py`: validation, every focus lens, both output formats,
  narrow-lens filtering, the `None`-focus path, clean markdown rendering, and the `_safe_tool`
  wrapper. Shared-formatter coverage extended in `tests/test_rick_mcp.py`.
- **`_fmt` rendering** — the shared markdown formatter (`rick_mcp/formatting.py`) now renders nested
  dicts recursively at **arbitrary depth** (depth-aware indentation) via a single helper, instead of
  leaking a raw Python dict repr past two levels. Fixes `rick_code_review`'s dimensions and, as a
  bonus, the nested sections of `rick_capabilities` and `rick_threat_model`; collapses three
  duplicated render branches into one.

## [3.12.0] - 2026-05-15

### Claude Code skills landed — 9 forkable orchestration playbooks + catalog + template

The repo now ships project-local Claude Code skills at `.claude/skills/`. They auto-discover
when Claude Code launches from the repo root, so anyone who clones rick_mcp gets the full
suite. Skills are pure orchestration — they chain `rick_mcp` MCP tools into higher-level
workflows and return content to chat; they do not write to the operator's filesystem.

- **9 skills (~1,786 lines):**
    - *Engagement lifecycle* — `/engagement-kickoff`, `/htb-day`, `/kill-chain-walk`,
      `/debrief-then-publish`
    - *Content production* — `/writeup-publish`, `/voice-check`
    - *Operations support* — `/arsenal-report`, `/cheatsheet-build`
    - *Career* — `/resume-tailor`
- **Catalog** — `.claude/skills/SKILLS.md` — categorized index, trigger phrases,
  composition patterns (engagement and CTF lifecycles, pre-publish QA).
- **Template** — `.claude/skills/SKILL_TEMPLATE.md` — runnable scaffold mirroring the
  reference shape (`engagement-kickoff`): frontmatter, elevator pitch, Prerequisites, Inputs,
  optional skill-specific section, Workflow with concrete MCP call blocks, Acceptance,
  Failure modes, Voice, NOT-does, Related skills.
- **Authoring conventions** — codified in `CLAUDE.md` § Claude Code Skills: kebab-case
  naming, generic-not-personal (`is_configured()` pattern, no `~/.rick_mcp/` hardcodes,
  no operator-personal wikilinks), pure orchestration, `AskUserQuestion` at every config
  decision.
- **Voice / register shifts stay server-side.** Persona prompts live in `rick_mcp/prompts.py`
  and are invoked via `rick_mode(persona="be_rick" | "mentor" | "evaluate" | ...)`. Skills
  do not duplicate voice instructions — one source of truth, no drift between channels.
- **No tool changes** — skills are workflow primitives on top of the existing 46 tools and
  36 resources. Test count unchanged from 3.11.1 (721 tests).

### Single source of truth for counts (no more drift across docs)

Tool / resource / skill / test counts and version previously appeared hardcoded in ~14
spots across 5 markdown files. Every feature change cost a multi-file cleanup, and a
brittle substring check in `rick_health` had already proven the drift was load-bearing.
Reworked the docs to a two-surface model:

- **`scripts/refresh_counts.py`** — computes counts at runtime from `__version__.py`,
  regex over `rick_mcp/tools/*.py` and `rick_mcp/resources/*.py`, the `.claude/skills/`
  directory, and `pytest --collect-only`. Rewrites HTML-comment-tagged regions in target
  files. Supports `--check` (exit 1 on drift, for CI) and `--skip-tests` (faster path).
- **`make refresh-counts`** + **`make check-counts`** — Makefile targets wrap the script.
- **README.md and `.claude/skills/SKILLS.md`** are the only two files with tagged counts;
  the script keeps them synced.
- **CLAUDE.md, ACHIEVEMENTS.md** no longer hardcode counts. They point at
  `rick_capabilities` for live state.
- **CHANGELOG entries** stay as point-in-time records — historical counts within a
  released version are correct for that release and are not auto-synced.

Tagged regions use HTML comments (render as nothing on GitHub):
`<!-- counts:tools -->46<!-- /counts:tools -->`. Coverage badge and per-resource-family
sub-counts (Profile / Documents / Resume / Vault) remain manually maintained for now.

### Structural tests for `.claude/skills/`

Added `tests/test_skills.py` — 68 structural assertions over the skills suite. Catches
drift between skill files, the `SKILLS.md` catalog, and the MCP tool registry. Does NOT
attempt to validate Claude Code's natural-language matching or runtime LLM behavior —
those are non-deterministic and out of scope.

Covers: every skill dir has a `SKILL.md`; kebab-case dir names; YAML frontmatter parses
and has `name` + `description`; `name` matches the dir; description includes the
`/<skill-name>` trigger phrase; required body sections present (Prerequisites / Workflow /
Acceptance); `mcp__rick_mcp__*` references resolve to real registered tools; sibling
`/<skill-name>` references exist on disk; catalog lists every skill and every catalog
entry is a real skill; `SKILL_TEMPLATE.md` lives at the catalog root (not inside a
subdir where it would become a phantom skill).

Caught one drift bug on first run: `voice-check/SKILL.md` referenced `/research`, a
global Claude Code skill that doesn't ship with rick_mcp. Generalized the reference to
"use a research tool or vault history" for forkability.

Test count: 721 → 789. Pipeline still passes clean under `make check`.

### Removed hardcoded operator identity from vault layer + shipped `soul-example/vault/` skeleton

Discovered during work on the vault example: the production code hardcoded the operator's
real name in three places, violating the project's "no hardcoded identity in Python source"
rule (CLAUDE.md § Rules). Cleaned it up and shipped a forkable vault skeleton so the
`vault://` resource family resolves out of the box for anyone who clones rick_mcp.

**Code (the violations and their fixes):**

- **Identity-hub URI renamed to `vault://identity/hub`** — the previous URI hardcoded the
  operator's first name as the path segment. New URI is generic; the handler resolves
  `Identity/<NAME>.md` dynamically from the operator's display name (from `identity.yaml`),
  falling back to the generic `Identity/Operator.md` that ships with soul-example. Final
  fallback: a missing-file stub.
- **Operator wikilink hardcoded in `engagement.py` × 3** — `rick_engagement_proposal`,
  `rick_roe`, and `rick_tracker` wrote a literal `[[Identity/<first-name>]]` wikilink into
  every vault engagement note. Now uses `f"[[Identity/{NAME}]]"`.
- **Bootstrap stub baked the operator's name into the suggested `--name` argument** —
  generalized to `--name '<your name>'`.
- **`rick_capabilities` URI list** — updated to advertise the new `vault://identity/hub` URI.

**Soul-example vault skeleton at `soul-example/vault/`:**

- `_CLAUDE.md`, `index.md`, `log.md` — operating manual, catalog, activity log
- `Identity/Operator.md` — generic identity hub fallback (always resolves for forkers)
- `Identity/Soul.md`, `Identity/Values.md`, `Identity/Methodology.md`, `Identity/Mantras.md`,
  `Identity/Rick.md` — bridge stubs that point at canonical sources in `~/.rick_mcp/`
- `Templates/Engagement.md` — engagement note template
- `Engagements/Acme Corp - Web App Pentest (2026-01-15).md` — proposal-shape example
- Updated `README.md` "Make It Yours" to include `cp -r soul-example/vault ~/.rick_mcp/`.

**Tests:**

- Renamed two existing vault tests for the renamed handler.
- Added `test_identity_hub_reads_name_derived_file` and
  `test_identity_hub_falls_back_to_operator_md` — coverage for the dynamic resolution
    + the soul-example fallback path.

**Follow-up scrub:**

- `tests/test_recon_handle.py` — fake GitHub API response fixture: identifying fields
  (name, bio, location, company) replaced with generic placeholders. No test assertions
  depended on the values.
- `rick_mcp/resources/vault.py` docstring example — illustrative `NAME` reference
  swapped to the soul-example fictional persona's display name for consistency.
- `soul-example/vault/` — handle references aligned with the existing soul-example
  fictional persona used elsewhere in the example tree.

**What stays:** GitHub username in URLs (CI badges, clone commands, security-advisory
links, issue-template assignees) — factual references to where the repo lives, not
personal data. The `rick_and_jiveturkey` resource family is project branding (the
father-son lineage), not operator identity. The `REF_HANDLE` constant in
`tests/test_recon_handle.py` is an intentional test target for the OSINT pivot logic.

**Breaking change for MCP clients:** The old identity-hub URI no longer exists; use
`vault://identity/hub`. Internal-only break — the URI was new in v3.10.0 and has no
external consumers known.

### Engagement vault-projection vocab seam + sitrep target enrichment

End-to-end smoke testing of the engagement lifecycle skills surfaced two tool-level seams
worth closing.

- **Vault-projection vocab seam (`engagement.py`).** `rick_engagement_proposal` writes
  the vault note under `<Client> - <Title-Case-Type>.md` using its own type vocabulary
  (e.g. `web_app_pentest` → "Web App Pentest"). `rick_roe`, `rick_client_onboarding`, and
  `rick_debrief` use a different, more-general vocabulary (e.g. `app_security`). When the
  vocabularies differ, the lookup in `_find_matching_engagement()` missed the proposal
  note and silently no-op'd the append — the tool returned `"no matching engagement
  note found — text-only output"`. Fixed by extending the lookup with a client-only
  fallback (most recent by mtime) when the strict `<Client> - <Type Title>` prefix
  fails. The kickoff workflow is sequential and minutes apart, so most-recent-for-this-
  client is the right note. Two new tests cover the vocab-mismatch path for ROE and
  debrief.
- **`rick_sitrep` target enrichment.** Kill-chain state (`~/.rick_mcp/dick/<id>.json`)
  and tracker state (`~/.rick_mcp/engagements/<id>.json`) are two separate JSON stores.
  When an engagement was created via `rick_tracker create` (which is what
  `/engagement-kickoff` and `/htb-day` do) rather than `rick_full_auto`, the kill-chain
  state lacked the target field and sitrep printed `"Target: Not yet specified"` even
  though the tracker had the data. `rick_sitrep` now reads tracker JSON via the new
  `_load_tracker_state()` helper in `jarvis_state.py` and surfaces both `target` and
  `client` when the kill-chain side doesn't have them. `rick_tracker create` also now
  preserves a `target` field if provided in the create data (previously dropped). Two
  new tests cover tracker-present and tracker-absent paths.

**Intentionally not fixed:** the engagement tools' methodology output (7 operator phases:
Recon → Vuln Assess → Exploit → PrivEsc → Lateral → Docs → Remediation) and
`rick_kill_chain`'s phase model (Lockheed Martin 7-step: Recon → Weaponization →
Delivery → Exploit → Installation → C2 → Actions) are two different frameworks living
in the same toolchain. Methodology describes operator workflow; kill chain describes
attack lifecycle. Different concepts, different uses. Conflating would lose
information. Document here so future-readers know this is deliberate.

Test count: 790 → 794. Pipeline still passes clean under `make check`.

## [3.11.1] - 2026-05-14

### Fix: percent-decoding + path containment for `vault://engagements/{codename}`

End-to-end MCP verification of v3.11.0 turned up two issues, both now fixed:

- **Percent-decoding** — FastMCP passes URI path parameters in their percent-encoded form
  (e.g. `HTB%20-%20MonitorsFour%20(2026-05-09)`). The v3.11.0 handler was matching the
  encoded string against on-disk filenames that contain literal spaces, so every live
  pull hit the missing-codename branch. Handler now decodes via `urllib.parse.unquote`
  before sanitizing.
- **Path containment** — defense-in-depth check added. The resolved target path is
  verified to be inside `vault/Engagements/` before any filesystem read. Guards against:
  rogue symlinks inside the engagements dir pointing outside the vault, and any future
  change to `codename_to_filename` that loosens the slash strip. Returns a generic
  "invalid codename" stub on escape; never echoes attempted resolved paths.
- **Tests** — 2 new cases: `test_engagement_detail_decodes_percent_encoded_codename`,
  `test_engagement_detail_path_traversal_rejected`,
  `test_engagement_detail_symlink_escape_rejected`. 721 tests total.

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
    - `vault://identity/hub` (originally hardcoded to the operator's name; renamed in v3.12.0) / `methodology` /
      `values` / `soul` / `rick` — identity stubs
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
  voice — first person, builder metaphors, military-grade precision, dry humor. AI-first structural rules
  (preamble, frontmatter, wikilinks, recency markers) apply regardless of voice.
- **Zero new dependencies.** Uses stdlib `pathlib` + existing `pyyaml`.

---

## [3.9.0] - 2026-05-07

### Philosophy-Aware Tool Output — Decision Tree Framework

- **New data file** `rick_mcp/data/philosophy.yaml` — operator-facing philosophy as data, not code. Three top-level
  sections:
    - `core_principles` — 7 soul values (Do No Harm, Integrity First, Continuous Improvement, Teach What You Know,
      Measure Twice Hack Once, Accountability, The Craft) with operational meanings.
    - `decision_filters` — 9 active constraints (Thorough > Fast, Manual > Scanner, Honesty above all, Builder's eye
      first, Cycle breaker, No checkbox compliance, Chain over isolation, Builder metaphor, Mantras when stuck) with
      trigger keywords for keyword-based matching.
    - `validation_rules` — 5 RoE rules (authorized targets, 1hr critical escalation, severity+PoC+impact+remediation,
      reproducibility, no-DoS-without-approval).
- **Override path** — `~/.rick_mcp/philosophy.yaml` overrides the bundled defaults, mirroring the `identity.yaml`
  pattern. Philosophy stays out of Python source.
- **New module** `rick_mcp/philosophy.py` — YAML loader + structural dispatch tables. Loads override → bundled →
  minimal-baseline. Code-side (not data) tables stay in Python because they're framework code-shape, not operator
  philosophy:
    - `METHODOLOGY_GATE_KEYWORDS` — scenario keywords → MISSION_PHASES name.
    - `ARSENAL_CHAIN` — situation → next-tool chain (mirrors the JARVIS arsenal table at `prompts.py:686-700`).
    - `STRIDE_PRINCIPLE_ANCHORS` + `STRIDE_FILTER_MAP` — STRIDE pillar → governing principles + filters (slug references
      into the YAML).
    - `chain_validation` — STRIDE → chain-framing prose.
- **`rick_tool_recommend` upgraded** — output now carries `decision_filters_applied`, `methodology_gate`,
  `validation_checklist`, and `chain_to`, all derived from the philosophy module instead of being implicit in prose.
- **`rick_threat_model` upgraded** — every STRIDE category now ships with `decision_filters`, `chain_validation`, and
  `core_principle_anchors`. The architecture is no longer a flat lookup; each pillar declares the soul values, the
  filters, and the chain-framing note that govern its branches.
- **Tests** — new `tests/test_philosophy.py` (~50 tests) covering YAML loading + override precedence, the module's data
  shape, helper functions (`apply_filters`, `infer_methodology_gate`, `chain_for`, `principle_anchors`,
  `chain_validation`, `filters_for_stride`), and end-to-end wiring into both tools across markdown + JSON formats.
- **Out of scope this release**: wiring filters into `rick_attack_chain`, `rick_kill_chain`, `rick_next_move`,
  `rick_vuln_assess`. Follow-up bump.

---

## [3.8.0] - 2026-05-02

### Operator Philosophy Layer — Prompts That Reason Like the Operator

- **`build_jarvis()` expanded** — JARVIS now reasons *like* the operator, not just *about* them. Adds two new sections
  to the prompt:
    - **Operator Philosophy** — embeds 6 profile files (`values`, `craftsmanship`, `heritage`, `human`, `mantras`,
      `rick_and_jiveturkey`) as the lenses every recommendation must pass through. Previously only `summary`, `stack`,
      `methodology` were loaded.
    - **Decision Filters** — translates philosophy into prescriptive JARVIS rules: *Thorough > Fast*, *Manual depth >
      Scanner output*, *Honesty above all*, *Builder's eye first*, *Three boys watching*, *Cycle breaker*, *No checkbox
      compliance*, *Chain over single-vuln framing*, *Builder metaphors as native register*, *Mantras surface when
      stuck*.
- **`build_be_rick()` and `build_mentor_mode()`** also gain the **Operator Philosophy** section, so the foundation and
  the mentorship voice carry the same distilled principles JARVIS uses. Decision Filters stay JARVIS-only — they're
  tactical rules, not voice.
- **New shared helper** `_operator_philosophy_section()` keeps the 6 reads in one place, used by all three builders.
- **Other prompts unchanged** — `dick_mode`, `pentest_mode`, `evaluate_fit`, `engagement_ops` deliberately skip the
  section (tactical or evaluative contexts where the structured philosophy doesn't fit).
- **No new dependencies.** Reuses existing `_read_data()`. Backward-compatible — generic fallback path still works
  without `~/.rick_mcp/profiles/` overrides.
- **Tests**: new `tests/test_prompts.py` (23 tests) covering JARVIS philosophy + filters, be_rick philosophy +
  no-filters guard, mentor_mode philosophy + no-filters guard, and explicit "still untouched" guards for
  dick_mode/pentest_mode/evaluate_fit/engagement_ops.

---

## [3.7.0] - 2026-04-26

### Handle Reconnaissance Tool

- **New tool**: `rick_recon_handle` — OSINT against a hacker handle. Returns a structured JSON profile from public
  sources. Default response format is JSON (machine-readable, chain-friendly).
- **GitHub** (load-bearing wall): real REST API fetch for `/users/{h}`, `/users/{h}/repos`, and
  `/users/{h}/events/public` — profile fields, top 5 starred non-fork repos, top 5 languages, recent activity count.
  Optional `github_token` raises rate limit 60/hr → 5000/hr.
- **CTFTime**: optional `ctftime_id` triggers direct enrichment via `/api/v1/users/{id}/` (team, ranking). Without an
  ID, returns a search URL — CTFTime's API requires numeric IDs, not handles.
- **HackTheBox**: returns the public profile URL with a note that programmatic enrichment requires an API token.
- **Search pivots** (URLs only, no scraping): HackerOne, Bugcrowd, Mastodon (infosec.exchange), Google dorks for blogs
  and conference talks, LinkedIn search.
- **Cache**: 24hr file cache at `~/.rick_mcp/handle_cache/` (sha256-keyed by URL), mirroring `rick_cve`'s pattern.
- **Soul-bounded**: `authorization` field on every output, public sources only, no email harvesting, no doxxing, no paid
  OSINT brokers, graceful degrade when sources fail.
- 46 tools total (up from 45).

---

## [3.6.0] - 2026-04-16

### Writeups as Reference Material

- **New action**: `rick_writeups(action='index')` — corpus intelligence. Scans all write-ups, extracts top 20 tools
  mentioned, CVEs (regex `CVE-YYYY-NNNNN`), MITRE technique IDs (regex `T\d{4}`), and Linux/Windows OS breakdown. Cached
  to `.index.json` with 24hr TTL.
- **Cross-referencing**: 6 existing tools now cite your writeups alongside theoretical guidance:
    - `rick_cheatsheet` — "Seen in your writeups: [paths]" cites boxes where you used the tool
    - `rick_recon` — cites writeups matching the target type (AD, cloud, web, etc.)
    - `rick_vuln_assess` — cites writeups demonstrating the vulnerability category
    - `rick_attack_chain` — cites writeups showing the scenario's techniques
    - `rick_pivot_plan` — cites writeups matching the compromised position
    - `rick_tool_recommend` — cites writeups featuring the top recommended tool
- **New exported helper**: `cite_writeups(term, limit=5)` — used by any tool that wants citation support. Silent when no
  writeups exist (generic output unchanged).
- Citation uses ripgrep for speed, falls back to pure-Python grep. Dedupes by file so the same writeup isn't cited
  twice.

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

- **New tool**: `rick_mantra` — pulls a random mantra from the operator's stored mantras. One per call. Reads from
  `~/.rick_mcp/profiles/mantras.md` at runtime.
- 44 tools total (up from 43)

---

## [3.3.0] - 2026-04-02

### JARVIS Intelligence Layer Expansion

- **8 new tools**: `rick_notes`, `rick_timeline`, `rick_compare`, `rick_scope_check`, `rick_export`, `rick_checklist`,
  `rick_tag`, `rick_rollback`
- **Image attachments**: `rick_notes` and `rick_kill_chain` add_finding support image path references (png, jpg, gif,
  svg, pdf, webp)
- **Scope safety rail**: `rick_scope_check` stores in-scope targets and ROE, validates before you touch anything
- **Engagement comparison**: `rick_compare` diffs two engagements side by side for retests
- **Export**: markdown, JSON, CSV — report-ready output from any engagement
- **Phase checklists**: auto-generated by target type with 8 environment-specific templates
- **Finding tags**: severity, category, MITRE ATT&CK technique IDs on any finding
- **State rollback**: automatic snapshots before mutations, undo with `rick_rollback`
- **Architecture**: split `jarvis.py` into `jarvis_state.py` (shared persistence), `jarvis.py` (core 4 tools),
  `jarvis_extended.py` (8 new tools)
- **Input models**: all JARVIS models moved to `models/inputs.py` — consistent with project convention
- 43 tools total (up from 35)
- 512 tests total (up from 449)

---

## [3.2.0] - 2026-03-23

### JARVIS — The Intelligence Layer

- **New mode**: `jarvis` — master prompt that turns Claude into a proactive orchestrator with automatic tool chaining,
  kill chain tracking, and situational awareness
- **New tool**: `rick_sitrep` — Situation Report. One command, full tactical picture: kill chain progress, findings,
  mission log, tool history, tactical assessment
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
- `profile://timeline` — Career timeline from early-career start through offensive security

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
