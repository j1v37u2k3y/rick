# Rick MCP Server v1.0

[![CI](https://github.com/j1v37u2k3y/rick/actions/workflows/ci.yml/badge.svg)](https://github.com/j1v37u2k3y/rick/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-259%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)]()

Rick is the father. jiveturkey is the son. The MCP is Rick.

A Model Context Protocol server that IS the resume. 20 tools. 23 resources. The code IS the craft.

From frontier reconnaissance to cyber reconnaissance — same mission, different battlefield.

## Why an MCP Server and Not a Webpage

A webpage sits there and waits to be read. Rick **responds**.

Rick is a living system that an AI can query, reason about, and use as a tool. An LLM can ask Rick who jiveturkey is and
get structured identity data back. It can pull the book — raw, unfiltered, with all the carriage returns intact. It can
query values, mantras, methodology — all as structured resources an AI can reason over. And there are 20 functional
tools that *do things* — generate ROE docs, model threats, look up CVEs, track engagements, recommend tools, write cover
letters matched to job postings.

A webpage can't do any of that. A PDF resume definitely can't.

**What this actually is:**

- A **machine-readable identity** that any MCP-compatible AI can consume and act on
- **Functional proof of skill** — the code IS the portfolio, not a description of one
- **An interactive operator** — say "check if jiveturkey's a fit for this job posting" and Rick runs the analysis
- **A teaching tool** — newcomers can ask Rick for mentorship paths, cheatsheets, attack chains

The closest analogy isn't a webpage. It's closer to an API that represents a person — except it also has opinions,
heritage, and a theme song.

[jiveturkey.rocks](https://jiveturkey.rocks/) is where people go to learn about jiveturkey. Rick is where AI goes to
*work with* jiveturkey.

## Quick Start

### Prerequisites

- Python 3.10+
- A virtual environment

### Install

```bash
git clone https://github.com/j1v37u2k3y/rick.git
cd rick
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Use with Claude Code

The repo includes `.mcp.json` — just clone, install deps, and open the project with Claude Code. Rick loads
automatically.

```bash
cd rick
claude
```

Then run `/mcp` to verify the connection.

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

## Tools — 20 Functional Tools

| Tool                       | What It Does                                                                             |
|----------------------------|------------------------------------------------------------------------------------------|
| `rick_recon`               | Recon playbooks for 8 target types (web, network, cloud, AD, API, container, mobile)     |
| `rick_vuln_assess`         | Vuln assessment methodology for 10 categories (SQLi, XSS, SSRF, IDOR, privesc, etc.)     |
| `rick_roe`                 | Rules of Engagement generator — scope, authorization, escalation, deliverables           |
| `rick_report_template`     | Pentest report section templates — executive summary, findings, methodology, remediation |
| `rick_tool_recommend`      | Scenario-aware security tool recommendations                                             |
| `rick_engagement_proposal` | SOW/proposal generator for 7 engagement types                                            |
| `rick_client_onboarding`   | Client onboarding packet — checklists, ground rules, comms protocol                      |
| `rick_compatibility_check` | Analyze a job posting or engagement brief against jiveturkey's profile                   |
| `rick_cover_letter`        | Targeted cover letter generator with 3 tones                                             |
| `rick_attack_chain`        | MITRE ATT&CK kill chain mapper — 6 attack scenarios                                      |
| `rick_pivot_plan`          | Pivoting and lateral movement playbook by compromised position                           |
| `rick_hardening`           | Defensive hardening blueprints for 9 technologies                                        |
| `rick_cheatsheet`          | Field manual cheatsheets for 10 core offensive tools                                     |
| `rick_debrief`             | Post-engagement debrief template                                                         |
| `rick_mentorship`          | Learning paths and mentorship for newcomers to offensive security                        |
| `rick_threat_model`        | STRIDE threat modeling for 8 system types                                                |
| `rick_status`              | Server status — version, callsign, tool/resource counts, operational readiness           |
| `rick_health`              | Health check — verifies all tools, resources, formatting, version are operational        |
| `rick_cve`                 | NVD CVE lookup — search by CVE ID or keyword, returns CVSS scores and details            |
| `rick_tracker`             | Engagement tracker — create engagements, track findings, export as JSON                  |

## Example Usage

Once connected, try asking:

**Recon a target:**
> "Run rick_recon for a web_app target"

**Assess a vulnerability category:**
> "Use rick_vuln_assess for injection vulnerabilities"

**Plan an attack chain:**
> "Show me the external_to_da attack chain"

**Get tool recommendations:**
> "What tools do I need for an internal network pentest with Active Directory?"

**Generate engagement docs:**
> "Create a rick_roe for a red_team engagement for Acme Corp, 20 days"
> "Generate a rick_engagement_proposal for a full_scope assessment"

**Hardening guidance:**
> "Give me the rick_hardening blueprint for active_directory, critical priority only"

**Mentorship:**
> "Run rick_mentorship for getting_started in offensive security"

**Check job fit:**
> "Run rick_compatibility_check against this job posting: [paste job description]"

**Generate a cover letter:**
> "Use rick_cover_letter for BigCorp, Senior Pentester role, key requirements: OSCP web app cloud"

## Resources — 23 Identity Resources

Access these via MCP resource URIs:

- `profile://rick_and_jiveturkey` — The connection. Rick is the father, jiveturkey is the operator.
- `profile://summary` — Quick reference card
- `profile://values` — Honor. Courage. Commitment. Honesty.
- `profile://heritage` — Lineage, roots, frontier spirit
- `profile://craftsmanship` — Builder meets breaker philosophy
- `profile://stack` — Complete technical arsenal
- `profile://methodology` — 7-phase engagement methodology
- `profile://mantras` — Operational mantras and philosophy
- `profile://human` — Father, cycle breaker, poet, ever evolving
- `profile://entertainment` — Humor as operational tool
- `doc://working-with-me` — Complete engagement guide
- `doc://the-book` — Memoirs of jiveturkey
- `doc://soul` — Core principles and values
- `doc://operator` — Full mission parameters and Working With Me guide
- `doc://profile` — Current state, horizon, key learnings
- `doc://achievements` — The full build log
- `doc://contributing` — How to contribute
- `doc://changelog` — Version history
- `doc://security` — Security policy and responsible disclosure
- `resume://overview` — The MCP as living resume
- `resume://evidence` — Skill-to-tool mapping
- `resume://portfolio` — External portfolio links
- `resume://contact` — How to engage, next steps

## Development

### Run Tests

```bash
make test        # 259 tests
make coverage    # Tests + coverage report (99%+)
```

### Run All Checks

```bash
make check       # Lint + format + typecheck + tests
```

### Auto-fix Issues

```bash
make fix         # Auto-fix lint and formatting
```

### Available Make Commands

| Command          | Description                                       |
|------------------|---------------------------------------------------|
| `make check`     | Full pipeline — lint, format, typecheck, tests    |
| `make fix`       | Auto-fix lint and format issues                   |
| `make test`      | Run 259 tests                                     |
| `make coverage`  | Tests with coverage report (80% minimum enforced) |
| `make typecheck` | mypy static type analysis                         |
| `make lint`      | ruff lint check                                   |
| `make smoke`     | Fire every tool once — live operational check     |
| `make clean`     | Remove build/test artifacts                       |

### Pre-commit Hooks

Pre-commit hooks are installed automatically. Every commit runs:

- Trailing whitespace and EOF fixes
- YAML/JSON validation
- Large file detection
- Private key detection
- Merge conflict detection
- Ruff lint + format
- Full test suite

### CI/CD

GitHub Actions runs on every push/PR against Python 3.10, 3.12, and 3.14.

## Achievements

Read [ACHIEVEMENTS.md](ACHIEVEMENTS.md) for the full build log — 20 tools, 259 tests, 97% coverage, full CI/CD pipeline.

## The Operator

Read [WORKING_WITH_ME.md](WORKING_WITH_ME.md) for how to engage, what to expect, and what I need.

Access `doc://profile` for current state and key learnings (private — available when deployed locally).

Access `doc://soul` and `doc://the-book` through Rick's MCP resources for the principles and the memoirs.

## Built With

- [FastMCP](https://github.com/jlowin/fastmcp) — MCP server framework
- [Pydantic v2](https://docs.pydantic.dev/) — Input validation
- [pytest](https://docs.pytest.org/) — Testing
- [ruff](https://docs.astral.sh/ruff/) — Linting and formatting
- [mypy](https://mypy-lang.org/) — Static type checking
- [pre-commit](https://pre-commit.com/) — Git hooks

## Semper Fidelis

I'm still building. Are you?
