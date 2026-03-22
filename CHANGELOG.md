# Changelog

All notable changes to rick_mcp will be documented in this file.

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