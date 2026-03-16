# Contributing to Rick MCP

Thanks for your interest. Here's how to contribute.

## Getting Started

```bash
git clone https://github.com/j1v37u2k3y/rick.git
cd rick
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
pre-commit install
```

## Development Workflow

1. Create a branch from `main`
2. Make your changes
3. Run `make check` — all checks must pass
4. Commit (pre-commit hooks will verify)
5. Open a PR against `main`

## Code Standards

- **Lint**: `ruff check rick_mcp.py tests/`
- **Format**: `ruff format rick_mcp.py tests/`
- **Types**: `mypy rick_mcp.py --ignore-missing-imports --no-strict-optional`
- **Tests**: `pytest tests/ -v` — 195+ tests must pass
- **Coverage**: 80% minimum enforced

Run `make check` to verify everything at once.

## Adding a Tool

1. Create a Pydantic input model with `ConfigDict(str_strip_whitespace=True, extra="forbid")`
2. Add the `@mcp.tool()` decorated async function
3. Add tests covering all valid inputs, error cases, and both output formats
4. Update `rick_status` tool count
5. Update `README.md` tool table
6. Update `CHANGELOG.md`

## Adding a Resource

1. Add the `@mcp.resource()` decorated async function
2. Return JSON (via `json.dumps`) or plain text
3. Add a test verifying the resource returns expected content
4. Update `rick_status` resource count
5. Update `README.md` resource list

## Commit Messages

Keep them concise. Lead with what changed, not why.

```
Add rick_new_tool — description of what it does
Fix rick_recon error handling for edge case
Update README with new tool documentation
```

## Pull Requests

- Keep PRs focused — one feature or fix per PR
- All checks must pass
- Include tests for new functionality
- Update docs if user-facing behavior changes

## Principles

- No harm. Ever. Point blank. Full stop.
- Facts not opinions
- Thorough > fast
- Honest findings, no padded reports
- The craft demands quality

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — don't open a public issue.

*Semper Fidelis*
