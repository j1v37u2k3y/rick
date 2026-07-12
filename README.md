# Rick MCP Server <!-- counts:version -->v3.14<!-- /counts:version -->

[![CI](https://github.com/j1v37u2k3y/rick/actions/workflows/ci.yml/badge.svg)](https://github.com/j1v37u2k3y/rick/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-930%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-%E2%89%A590%25-brightgreen.svg)]()

A forkable security MCP platform. Load your identity, own your craft.

<!-- counts:tools -->48<!-- /counts:tools --> tools. <!-- counts:resources -->36<!-- /counts:resources --> resources. <!-- counts:skills -->11<!-- /counts:skills --> Claude Code skills. Fork it, fill it, make it yours.

<!-- Counts and version above are auto-synced by `scripts/refresh_counts.py`. Run `make refresh-counts` after adding tools / resources / skills, or `make check-counts` in CI. -->

## Install

```bash
git clone https://github.com/j1v37u2k3y/rick.git
cd rick
make setup
```

`make setup` installs deps, sets up pre-commit hooks, and creates `~/.rick_mcp/`. Verify with `claude` then
`/mcp`. Soul, vault, Docker, and Claude Desktop config in [Quick Start](#quick-start) below.

**Full walkthrough (clone → working Rick + identity + Kali + troubleshooting):** [SETUP.md](SETUP.md).

Running Kali in VMware? [`scripts/setup_kali_mount.sh`](scripts/setup_kali_mount.sh) mirrors host
`~/.rick_mcp/` into the guest at the same logical path. Idempotent.

**Prereq:** on the host, VM Settings → Sharing → enable Shared Folders, add `~/.rick_mcp`, name the share
`rick_mcp`. The script assumes that share exists — verify in the guest with `vmware-hgfsclient` before
running.

## Why an MCP Server

A webpage sits there and waits to be read. Rick **responds**.

Rick is a Model Context Protocol server that an AI can query, reason about, and use as a tool. An LLM can ask Rick
who you are and get structured identity data back. It can pull your writing, your values, your methodology — all as
structured resources an AI can reason over. And there are <!-- counts:tools -->48<!-- /counts:tools --> functional tools
that *do things* — generate ROE docs,
model threats, look up CVEs, track engagements, recommend tools, write cover letters matched to job postings, generate
IR playbooks, compare C2 frameworks, and scope entire engagements.

A webpage can't do any of that. A PDF resume definitely can't.

**What this actually is:**

- A **machine-readable identity** that any MCP-compatible AI can consume and act on
- **Functional proof of skill** — the code IS the portfolio, not a description of one
- **An interactive operator** — say "check if I'm a fit for this job posting" and Rick runs the analysis
- **A teaching tool** — newcomers can ask Rick for mentorship paths, cheatsheets, attack chains
- **A purple team platform** — offensive AND defensive tools, attack chains AND detection rules

## Quick Start

### Prerequisites

- Python 3.10+
- A virtual environment

### Install

```bash
git clone https://github.com/j1v37u2k3y/rick.git
cd rick
make setup
```

`make setup` installs all dependencies, activates pre-commit hooks, and creates the private content directory.

### Give Rick His Soul (Optional)

Rick works without these files, but with them he has a soul. These are private — they never enter git.

See `soul-example/` for a fully worked example using a fictional operator (sh4d0wf0x).

```bash
# Copy the example files
cp soul-example/identity.yaml ~/.rick_mcp/
cp -r soul-example/soul soul-example/profiles soul-example/resume soul-example/docs ~/.rick_mcp/

# Optional: copy the vault skeleton too (enables vault:// resources + engagement → vault projection)
cp -r soul-example/vault ~/.rick_mcp/

# Edit your identity — this is the core config
$EDITOR ~/.rick_mcp/identity.yaml
```

**What lives where:**

| Path                           | Purpose                                                                            |
|--------------------------------|------------------------------------------------------------------------------------|
| `~/.rick_mcp/identity.yaml`    | Name, callsign, certs, tools, tagline — powers all output                          |
| `~/.rick_mcp/soul/SOUL.md`     | Core principles and values — feeds `be_rick` and `dick_mode`                       |
| `~/.rick_mcp/soul/my book.txt` | Your writing, memoirs, voice — feeds `mentor_mode`                                 |
| `~/.rick_mcp/soul/PROFILE.md`  | Current state, what's on the horizon                                               |
| `~/.rick_mcp/profiles/`        | 11 identity resources (stack, methodology, timeline, etc.)                         |
| `~/.rick_mcp/resume/`          | 4 resume resources (overview, evidence, portfolio, contact)                        |
| `~/.rick_mcp/docs/`            | War stories and additional content                                                 |
| `~/.rick_mcp/vault/`           | Optional Obsidian Second Brain — engagement projection, identity hub, bridge stubs |

Rick's prompts pull live from these files at call time. Update the soul, update Rick's voice. Without these files, Rick
falls back to generic defaults.

### Make It Yours

1. **Clone** — `git clone https://github.com/j1v37u2k3y/rick.git && cd rick`
2. **Setup** — `make setup`
3. **Copy examples** —
   `cp soul-example/identity.yaml ~/.rick_mcp/ && cp -r soul-example/soul soul-example/profiles soul-example/resume soul-example/docs soul-example/vault ~/.rick_mcp/`
4. **Edit identity** — `$EDITOR ~/.rick_mcp/identity.yaml`
5. **Add your soul** — Edit `~/.rick_mcp/soul/` with your values, your story, your profile
6. **Done** — Rick now speaks for you

Your identity files live outside the repo in `~/.rick_mcp/`. The tools are generic. The soul is yours.

### Use with Claude Code

The repo includes `.mcp.json` — just clone, install deps, and open the project with Claude Code. Rick loads
automatically.

```bash
cd rick
claude
```

Then run `/mcp` to verify the connection. Try `rick_capabilities` to see everything Rick can do.

### Claude Code Skills (auto-discover)

The repo ships <!-- counts:skills -->11<!-- /counts:skills --> project-local Claude Code skills at `.claude/skills/`.
They auto-discover when Claude Code launches
from the repo root — no extra install. Skills are pure orchestration: they chain `rick_mcp` MCP tools into higher-level
workflows (engagement kickoff, kill-chain walks, writeup publishing, resume tailoring) and return content to chat.

- **Engagement lifecycle** — `/engagement-kickoff`, `/htb-day`, `/kill-chain-walk`, `/engagement-checkin`, `/debrief-then-publish`
- **Content production** — `/writeup-publish`, `/voice-check`
- **Operations support** — `/arsenal-report`, `/cheatsheet-build`, `/rick-review`
- **Career** — `/resume-tailor`

Voice / persona register shifts live server-side (`rick_mcp/prompts.py`), invoked via `rick_mode(persona=...)` — one
source of truth for voice, no skill-vs-server drift.

Full catalog with trigger phrases and composition patterns: [`.claude/skills/SKILLS.md`](.claude/skills/SKILLS.md).
Authoring conventions live in [`CLAUDE.md`](CLAUDE.md) § Claude Code Skills; new skills start from [
`.claude/skills/SKILL_TEMPLATE.md`](.claude/skills/SKILL_TEMPLATE.md).

### Run the Server Standalone

```bash
python rick_mcp.py
```

Or with the MCP CLI:

```bash
mcp run rick_mcp.py
```

### Docker

```bash
docker build -t rick_mcp .
docker run rick_mcp
```

### Add to Claude Desktop

Add this to your Claude Desktop MCP config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "rick_mcp": {
      "command": "python",
      "args": [
        "/path/to/rick/rick_mcp.py"
      ]
    }
  }
}
```

## Tools — <!-- counts:tools -->48<!-- /counts:tools --> Functional Tools

### Offensive — Recon & Assessment

| Tool                  | What It Does                                                                                |
|-----------------------|---------------------------------------------------------------------------------------------|
| `rick_recon`          | Recon playbooks for 8 target types (web, network, cloud, AD, API, container, mobile)        |
| `rick_recon_handle`   | OSINT against a hacker handle — GitHub profile/repos/activity + pivot URLs to HTB, H1, etc. |
| `rick_vuln_assess`    | Vuln assessment methodology for 10 categories (SQLi, XSS, SSRF, IDOR, etc.)                 |
| `rick_tool_recommend` | Scenario-aware security tool recommendations                                                |
| `rick_threat_model`   | STRIDE threat modeling for 8 system types                                                   |

### Offensive — Attack Methodology

| Tool                     | What It Does                                                              |
|--------------------------|---------------------------------------------------------------------------|
| `rick_attack_chain`      | MITRE ATT&CK kill chain mapper — 6 attack scenarios                       |
| `rick_pivot_plan`        | Pivoting and lateral movement playbook by compromised position            |
| `rick_cheatsheet`        | Field manual cheatsheets for 10 core offensive tools                      |
| `rick_c2_compare`        | C2 framework comparison — Cobalt Strike vs Sliver vs Mythic vs Havoc      |
| `rick_payload_guide`     | Payload methodology — evasion, encoding, delivery vectors by MITRE ATT&CK |
| `rick_cloud_attack_path` | Cloud-specific attack paths for Azure, AWS, GCP                           |
| `rick_wireless`          | Wireless attack playbooks — WiFi, Bluetooth, RFID                         |

### Defensive & Detection

| Tool                     | What It Does                                                                       |
|--------------------------|------------------------------------------------------------------------------------|
| `rick_hardening`         | Defensive hardening blueprints for 9 technologies                                  |
| `rick_incident_response` | IR playbooks for 5 incident types (ransomware, breach, insider, BEC, supply chain) |
| `rick_detection_rules`   | Sigma/YARA rule templates for 6 attack patterns                                    |
| `rick_log_analysis`      | Log review methodology for 6 log sources                                           |

### Code Review

| Tool               | What It Does                                                                                      |
|--------------------|---------------------------------------------------------------------------------------------------|
| `rick_code_review` | Builder's-eye scoring & verdict rubric (craftsmanship + security + architecture) — powers `/rick-review` |

### Cognitive Appraisal

| Tool                       | What It Does                                                                                      |
|----------------------------|---------------------------------------------------------------------------------------------------|
| `rick_cognitive_appraisal` | Defense-first appraisal **scaffold** (OCC/Lazarus/Scherer) — structures the reasoning (levers + detection/hardening); the model fills it in. Red-team pretext path behind an operator-set scope gate (deliberate friction, not access control) |

### Engagement Lifecycle

| Tool                       | What It Does                                                                   |
|----------------------------|--------------------------------------------------------------------------------|
| `rick_scoping`             | Engagement scoping calculator — hours, team size, rate card, timeline          |
| `rick_roe`                 | Rules of Engagement generator — scope, authorization, escalation, deliverables |
| `rick_engagement_proposal` | SOW/proposal generator for 7 engagement types                                  |
| `rick_client_onboarding`   | Client onboarding packet — checklists, ground rules, comms protocol            |
| `rick_report_template`     | Pentest report section templates (PlexTrac-compatible)                         |
| `rick_debrief`             | Post-engagement debrief template                                               |
| `rick_tracker`             | Engagement tracker — create, findings, export (JSON/CSV/Markdown)              |

### Career & Mentorship

| Tool                       | What It Does                                                   |
|----------------------------|----------------------------------------------------------------|
| `rick_compatibility_check` | Analyze a job posting or engagement brief against your profile |
| `rick_cover_letter`        | Targeted cover letter generator with 3 tones                   |
| `rick_mentorship`          | Learning paths for 9 topics — getting started through advanced |

### Research

| Tool       | What It Does                                              |
|------------|-----------------------------------------------------------|
| `rick_cve` | NVD CVE lookup — search by ID or keyword, cached 24 hours |

### JARVIS — Intelligence Layer

| Tool               | What It Does                                                                                      |
|--------------------|---------------------------------------------------------------------------------------------------|
| `rick_full_auto`   | Give a target, get the complete playbook — recon, vulns, attack chain, tools, pivot. All chained. |
| `rick_kill_chain`  | Stateful 7-phase kill chain tracker — persists across conversations. Image attachments.           |
| `rick_next_move`   | Situational awareness — analyzes position, findings, and kill chain state. What's next.           |
| `rick_sitrep`      | Situation Report — one command, full tactical picture. Kill chain, findings, mission log.         |
| `rick_notes`       | Engagement notes — add, list, search, delete. Supports image attachments as evidence.             |
| `rick_timeline`    | Unified chronological timeline — findings, logs, tool history. Filterable.                        |
| `rick_compare`     | Diff two engagements side by side — retests, what changed.                                        |
| `rick_scope_check` | Safety rail — check targets/actions against stored scope and ROE.                                 |
| `rick_export`      | Export engagement to markdown, JSON, or CSV. Report-ready.                                        |
| `rick_checklist`   | Phase-specific checklists by target type. Generate, check, track.                                 |
| `rick_tag`         | Tag findings — severity, category, MITRE ATT&CK technique IDs.                                    |
| `rick_rollback`    | Undo last kill chain state change. Automatic state snapshots.                                     |

### Meta

| Tool                | What It Does                                                                   |
|---------------------|--------------------------------------------------------------------------------|
| `rick_capabilities` | Full capability map — every tool organized by mission phase                    |
| `rick_status`       | Server status — version, callsign, tool/resource counts, operational readiness |
| `rick_health`       | Health check with optional self-healing (`fix=True`)                           |
| `rick_demo`         | Guided tour — fires one tool from each category                                |
| `rick_mantra`       | Random mantra from the operator's stored principles — one per call             |
| `rick_mode`         | Activate persona modes (be_rick, dick_mode, pentest_mode, mentor_mode, etc.)   |
| `rick_writeups`     | Browse, read, and search operator write-ups from `~/.rick_mcp/writeups/`       |

## Example Usage

Once connected, try asking:

**See what Rick can do:**
> "Run rick_capabilities"

**Recon a target:**
> "Run rick_recon for a web_app target"

**Assess a vulnerability category:**
> "Use rick_vuln_assess for injection vulnerabilities"

**Plan an attack chain:**
> "Show me the external_to_da attack chain"

**Compare C2 frameworks:**
> "Run rick_c2_compare for a stealth scenario"

**Get tool recommendations:**
> "What tools do I need for an internal network pentest with Active Directory?"

**Scope an engagement:**
> "Run rick_scoping for a red_team engagement, 5 targets, high complexity"

**Generate engagement docs:**
> "Create a rick_roe for a red_team engagement for Acme Corp, 20 days"

**Hardening guidance:**
> "Give me the rick_hardening blueprint for active_directory, critical priority only"

**Incident response:**
> "Run rick_incident_response for a ransomware incident"

**Detection rules:**
> "Generate rick_detection_rules for credential_dumping"

**Mentorship:**
> "Run rick_mentorship for getting_started in offensive security"

**Check job fit:**
> "Run rick_compatibility_check against this job posting: [paste job description]"

## Resources — <!-- counts:resources -->36<!-- /counts:resources --> Identity Resources

Access these via MCP resource URIs. Content is loaded from your private `~/.rick_mcp/` directory.

### Profile (11)

- `profile://rick_and_jiveturkey` — The operator's origin story and connection to Rick
- `profile://summary` — Quick reference card
- `profile://values` — Core values and principles
- `profile://heritage` — Lineage, roots, where you come from
- `profile://craftsmanship` — Builder meets breaker philosophy
- `profile://stack` — Complete technical arsenal
- `profile://methodology` — Engagement methodology
- `profile://mantras` — Operational mantras and philosophy
- `profile://human` — The person behind the operator
- `profile://entertainment` — Humor as operational tool
- `profile://timeline` — Career timeline

### Documents (9)

- `doc://working-with-me` — Complete engagement guide
- `doc://the-book` — Your writing — memoirs, essays, whatever you carry
- `doc://soul` — Core principles and values
- `doc://profile` — Current state, horizon, key learnings
- `doc://achievements` — The full build log
- `doc://contributing` — How to contribute
- `doc://changelog` — Version history
- `doc://security` — Security policy and responsible disclosure
- `doc://war-stories` — Anonymized engagement narratives from the field

### Resume (4)

- `resume://overview` — The MCP as living resume
- `resume://evidence` — Skill-to-tool mapping
- `resume://portfolio` — External portfolio links
- `resume://contact` — How to engage, next steps

### Vault (12) — Optional, requires Obsidian Second Brain

- `vault://manual` — Vault `_CLAUDE.md` (operating manual)
- `vault://index` — Vault catalog (all notes by folder)
- `vault://log` — Chronological vault activity log
- `vault://identity/hub` — Identity hub (aggregates soul, profiles, certs, tools); resolves `Identity/<your-NAME>.md`
  with fallback to `Identity/Operator.md`
- `vault://identity/methodology` — Bridge to Rick's 7-phase methodology
- `vault://identity/values` — Bridge to the four core values
- `vault://identity/soul` — Bridge to `~/.rick_mcp/soul/SOUL.md`
- `vault://identity/rick` — Father-son frame
- `vault://engagements` — JSON list of all engagement notes
- `vault://engagements/{codename}` — Single engagement note by codename (parameterized, v3.11+)
- `vault://templates/engagement` — Templater-based engagement template
- `vault://status` — Vault health (JSON)

## Vault Integration (v3.10+)

When `~/.rick_mcp/vault/` is bootstrapped as an Obsidian Second Brain, Rick MCP becomes a vault
contributor. Engagement tools auto-write Rick-voice AI-first notes to `vault/Engagements/`:

- `rick_engagement_proposal` creates `<Client - Type (Date)>.md` anchor with full Rick-voice body,
  wikilinks to `[[Identity/Methodology]]`, `[[Identity/Specializations/...]]`, `[[Identity/Tools/...]]`
- `rick_debrief`, `rick_roe`, `rick_client_onboarding` append their respective sections to the
  matching engagement note
- `rick_tracker` projects engagement state to `vault/Engagements/<eng_id>.md` — JSON canonical,
  vault is the human-readable mirror with dynamic findings table

Bootstrap the vault via [obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain):

```bash
git clone https://github.com/eugeniughelbur/obsidian-second-brain ~/.claude/skills/obsidian-second-brain
mkdir -p ~/.rick_mcp/vault
python3 ~/.claude/skills/obsidian-second-brain/scripts/bootstrap_vault.py \
  --path ~/.rick_mcp/vault --name "Your Name"
```

**Fork-friendly:** without the vault, every tool still works — vault writes are gated by
`vault.is_configured()` and degrade silently.

**Architectural rule:** vault references bedrock; bedrock is never duplicated. The soul, profiles,
and identity.yaml stay canonical at `~/.rick_mcp/`; vault wikilinks point at them.

## Development

### Run Tests

```bash
make test        # <!-- counts:tests -->930<!-- /counts:tests --> tests
make coverage    # Tests + coverage report (80%+ enforced)
```

### Run All Checks

```bash
make check       # Lint + format + typecheck + file-length + tests
```

### Auto-fix Issues

```bash
make fix         # Auto-fix lint and formatting
```

### Available Make Commands

| Command            | Description                                                 |
|--------------------|-------------------------------------------------------------|
| `make setup`       | Install deps, pre-commit hooks, create private content dir  |
| `make check`       | Full pipeline — lint, format, typecheck, file-length, tests |
| `make fix`         | Auto-fix lint and format issues                             |
| `make test`        | Run <!-- counts:tests -->930<!-- /counts:tests --> tests    |
| `make coverage`    | Tests with coverage report (80% minimum enforced)           |
| `make typecheck`   | mypy static type analysis                                   |
| `make lint`        | ruff lint check                                             |
| `make file-length` | Verify no Python file exceeds 1500 lines                    |
| `make smoke`       | Fire all non-network tools once — live operational check    |
| `make clean`       | Remove build/test artifacts                                 |

### Pre-commit Hooks

Pre-commit hooks are installed automatically. Every commit runs:

- Trailing whitespace and EOF fixes
- YAML/JSON validation
- Large file detection
- Private key detection
- Merge conflict detection
- **File length check** (1500 line max per Python file)
- Ruff lint + format
- **mypy** static type checking
- Full test suite

### CI/CD

GitHub Actions runs on every push/PR against Python 3.10, 3.12, and 3.14. Includes Docker build verification.

## Achievements

Read [ACHIEVEMENTS.md](ACHIEVEMENTS.md) for the build story. See [CHANGELOG.md](CHANGELOG.md) for version details.

## Built With

- [FastMCP](https://github.com/jlowin/fastmcp) — MCP server framework
- [Pydantic v2](https://docs.pydantic.dev/) — Input validation
- [PyYAML](https://pyyaml.org/) — Identity configuration loading
- [pytest](https://docs.pytest.org/) — Testing
- [Hypothesis](https://hypothesis.readthedocs.io/) — Property-based fuzz testing
- [ruff](https://docs.astral.sh/ruff/) — Linting and formatting
- [mypy](https://mypy-lang.org/) — Static type checking
- [pre-commit](https://pre-commit.com/) — Git hooks

---

The tools are the craft. The identity is yours.
