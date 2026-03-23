# Rick MCP Server v3.0

[![CI](https://github.com/j1v37u2k3y/rick/actions/workflows/ci.yml/badge.svg)](https://github.com/j1v37u2k3y/rick/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-406%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)]()

A forkable security MCP platform. Load your identity, own your craft.

31 tools. 25 resources. Fork it, fill it, make it yours.

## Why an MCP Server

A webpage sits there and waits to be read. Rick **responds**.

Rick is a Model Context Protocol server that an AI can query, reason about, and use as a tool. An LLM can ask Rick
who you are and get structured identity data back. It can pull your writing, your values, your methodology — all as
structured resources an AI can reason over. And there are 31 functional tools that *do things* — generate ROE docs,
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

See `soul-example/` for the full directory structure and example files. Copy them into `~/.rick_mcp/` and fill in your own content:

```bash
# The setup command creates ~/.rick_mcp/soul/ for you.
# Copy the examples and make them yours:

cp -r soul-example/* ~/.rick_mcp/

# Then edit:
~/.rick_mcp/soul/SOUL.md        # Core principles and values
~/.rick_mcp/soul/my book.txt    # Your writing — memoirs, essays, whatever you carry
~/.rick_mcp/soul/PROFILE.md     # Current state, what's on the horizon, key learnings
~/.rick_mcp/identity.yaml       # Name, callsign, tagline, contact info
```

Rick's prompts (`be_rick`, `mentor_mode`, etc.) pull live from these files at call time. Update the soul, update Rick's voice. The `doc://soul`, `doc://the-book`, and `doc://profile` resources serve this content to any MCP client.

If these files don't exist, Rick falls back to project-root copies (if present) or returns a default message.

### Make It Yours

The fork workflow:

1. **Clone** — `git clone https://github.com/j1v37u2k3y/rick.git && cd rick`
2. **Setup** — `make setup`
3. **Copy examples** — `cp -r soul-example/* ~/.rick_mcp/`
4. **Edit identity** — Open `~/.rick_mcp/identity.yaml` and fill in your name, callsign, tagline, and contact
5. **Add your soul** — Edit the files in `~/.rick_mcp/soul/` with your values, your story, your profile
6. **Add your profiles** — Edit `~/.rick_mcp/profiles/` with your stack, methodology, timeline, etc.
7. **Done** — Rick now speaks for you

Your identity files live outside the repo in `~/.rick_mcp/`. The tools are generic. The soul is yours.

### Use with Claude Code

The repo includes `.mcp.json` — just clone, install deps, and open the project with Claude Code. Rick loads
automatically.

```bash
cd rick
claude
```

Then run `/mcp` to verify the connection. Try `rick_capabilities` to see everything Rick can do.

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

## Tools — 31 Functional Tools

### Offensive — Recon & Assessment

| Tool                  | What It Does                                                                         |
|-----------------------|--------------------------------------------------------------------------------------|
| `rick_recon`          | Recon playbooks for 8 target types (web, network, cloud, AD, API, container, mobile) |
| `rick_vuln_assess`    | Vuln assessment methodology for 10 categories (SQLi, XSS, SSRF, IDOR, etc.)          |
| `rick_tool_recommend` | Scenario-aware security tool recommendations                                         |
| `rick_threat_model`   | STRIDE threat modeling for 8 system types                                            |

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

### Meta

| Tool                | What It Does                                                                   |
|---------------------|--------------------------------------------------------------------------------|
| `rick_capabilities` | Full capability map — every tool organized by mission phase                    |
| `rick_status`       | Server status — version, callsign, tool/resource counts, operational readiness |
| `rick_health`       | Health check with optional self-healing (`fix=True`)                           |
| `rick_demo`         | Guided tour — fires one tool from each category                                |
| `rick_mode`         | Activate persona modes (be_rick, pentest_mode, mentor_mode, etc.)              |

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

## Resources — 25 Identity Resources

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

## Development

### Run Tests

```bash
make test        # 406 tests across 4 test files
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
| `make test`        | Run 406 tests                                               |
| `make coverage`    | Tests with coverage report (80% minimum enforced)           |
| `make typecheck`   | mypy static type analysis                                   |
| `make lint`        | ruff lint check                                             |
| `make file-length` | Verify no Python file exceeds 1500 lines                    |
| `make smoke`       | Fire every tool once — live operational check               |
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
- Full test suite

### CI/CD

GitHub Actions runs on every push/PR against Python 3.10, 3.12, and 3.14. Includes Docker build verification.

## Achievements

Read [ACHIEVEMENTS.md](ACHIEVEMENTS.md) for the full build log — 31 tools, 406 tests, full CI/CD pipeline.

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
