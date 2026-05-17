.PHONY: check fix test lint format-check typecheck coverage smoke clean file-length setup refresh-counts check-counts

# Local venv — all targets use this so the dev experience is self-contained.
# After `make setup`, every other make target works without manual activation.
VENV        := venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP    := $(VENV)/bin/pip
PYTEST      := $(VENV)/bin/pytest
RUFF        := $(VENV)/bin/ruff
MYPY        := $(VENV)/bin/mypy
PRE_COMMIT  := $(VENV)/bin/pre-commit

MAX_FILE_LINES := 1500

# Run everything — the full inspection
check: lint format-check typecheck file-length test
	@echo ""
	@echo "═══════════════════════════════════════════════"
	@echo " ALL CHECKS PASSED"
	@echo "═══════════════════════════════════════════════"

# Auto-fix what can be fixed
fix:
	$(RUFF) check rick_mcp.py rick_mcp/ tests/ smoke_test.py --fix
	$(RUFF) format rick_mcp.py rick_mcp/ tests/ smoke_test.py
	@echo "Fixed. Run 'make check' to verify."

# Tests only
test:
	$(PYTEST) tests/ -v

# Tests with coverage
coverage:
	$(PYTEST) tests/ -v --cov=rick_mcp --cov-report=term-missing --cov-fail-under=80
	@echo ""
	@echo "Coverage report above. 80% minimum enforced."

# Lint only
lint:
	$(RUFF) check rick_mcp.py rick_mcp/ tests/ smoke_test.py

# Format check (no modifications)
format-check:
	$(RUFF) format --check rick_mcp.py rick_mcp/ tests/ smoke_test.py

# Type check
typecheck:
	$(MYPY) rick_mcp.py --ignore-missing-imports --no-strict-optional

# File length check — no Python file should exceed MAX_FILE_LINES
file-length:
	@FAIL=0; \
	for f in $$(find rick_mcp/ tests/ -name '*.py' -not -path '*/venv/*'); do \
		LINES=$$(wc -l < "$$f"); \
		if [ "$$LINES" -gt "$(MAX_FILE_LINES)" ]; then \
			echo "ERROR: $$f has $$LINES lines (max $(MAX_FILE_LINES))"; \
			FAIL=1; \
		fi; \
	done; \
	if [ "$$FAIL" -eq 1 ]; then exit 1; fi
	@echo "All Python files under $(MAX_FILE_LINES) lines."

# Smoke test — fire every tool once, verify output
smoke:
	@echo "═══════════════════════════════════════════════"
	@echo " SMOKE TEST — Firing all tools"
	@echo "═══════════════════════════════════════════════"
	@$(VENV_PYTHON) smoke_test.py
	@echo ""
	@echo "═══════════════════════════════════════════════"
	@echo " ALL TOOLS OPERATIONAL"
	@echo "═══════════════════════════════════════════════"

# Full dev environment setup — creates venv, installs deps, hooks, and private content dir.
# Idempotent: safe to re-run.
setup:
	@echo "═══════════════════════════════════════════════"
	@echo " RICK MCP — Dev Environment Setup"
	@echo "═══════════════════════════════════════════════"
	@if [ ! -d $(VENV) ]; then \
		echo " Creating venv at ./$(VENV) ..."; \
		python3 -m venv $(VENV); \
	else \
		echo " venv already exists at ./$(VENV)"; \
	fi
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements-dev.txt
	$(PRE_COMMIT) install
	@mkdir -p ~/.rick_mcp/soul
	@if [ ! -f .claude/settings.local.json ] && [ -f .claude/settings.example.json ]; then \
		cp .claude/settings.example.json .claude/settings.local.json; \
		echo " Created .claude/settings.local.json (auto-trusts rick_mcp on Claude Code launch)"; \
	elif [ -f .claude/settings.local.json ]; then \
		echo " .claude/settings.local.json already exists — leaving it alone"; \
	fi
	@echo ""
	@echo " venv:                ./$(VENV)/"
	@echo " Dependencies:        installed"
	@echo " Pre-commit hooks:    installed"
	@echo " Private content dir: ~/.rick_mcp/soul/"
	@echo ""
	@echo " Make targets use the venv automatically — no activation needed:"
	@echo "   make test     — run the test suite"
	@echo "   make check    — full pipeline (lint + format + typecheck + tests)"
	@echo ""
	@echo " To activate the venv in your shell (for ad-hoc python/pip work):"
	@echo "   source $(VENV)/bin/activate"
	@echo ""
	@echo " To configure your identity:"
	@echo "   cp soul-example/identity.yaml.example ~/.rick_mcp/identity.yaml"
	@echo "   Edit ~/.rick_mcp/identity.yaml with your details"
	@echo ""
	@echo " For the full experience, also add:"
	@echo "   ~/.rick_mcp/soul/SOUL.md       — Your core principles"
	@echo "   ~/.rick_mcp/soul/my book.txt   — Your memoirs"
	@echo "   ~/.rick_mcp/soul/PROFILE.md    — Current state"
	@echo ""
	@echo " See soul-example/ for all templates."
	@echo " Without identity files, Rick works with generic defaults."
	@echo " With them, Rick becomes yours."
	@echo ""
	@$(MAKE) -s smoke
	@echo ""
	@echo "═══════════════════════════════════════════════"
	@echo " Setup + smoke verified. Rick loads cleanly."
	@echo " Run 'make check' for the full pipeline (lint + tests)."
	@echo "═══════════════════════════════════════════════"

# Sync count placeholders (tools / resources / skills / tests / version) into README + SKILLS.md
refresh-counts:
	$(VENV_PYTHON) scripts/refresh_counts.py

# CI-friendly: fail if any tagged count region is stale
check-counts:
	$(VENV_PYTHON) scripts/refresh_counts.py --check

# Clean build/test artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist *.egg-info
	find . -type d -name __pycache__ -not -path './venv/*' -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean."
