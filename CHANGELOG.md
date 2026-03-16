# Changelog

All notable changes to rick_mcp will be documented in this file.

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