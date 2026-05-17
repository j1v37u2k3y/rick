.PHONY: check fix test lint format-check typecheck coverage smoke clean file-length setup refresh-counts check-counts install-user-mcp install-user-skills uninstall-user-skills

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
	@echo "   make test                  — run the test suite"
	@echo "   make check                 — full pipeline (lint + format + typecheck + tests)"
	@echo "   make install-user-mcp      — register rick_mcp at user scope (use Rick from any dir)"
	@echo "   make install-user-skills   — symlink the 11 skills into ~/.claude/skills/ (use anywhere)"
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

# Symlink every skill in .claude/skills/<name>/ into ~/.claude/skills/<name> so the
# skills are auto-discovered from any directory (not just when Claude Code launches
# from this repo). Opt-in — run manually. Idempotent: already-linked + conflicts handled.
install-user-skills:
	@echo "═══════════════════════════════════════════════"
	@echo " Installing skills at USER scope (~/.claude/skills/)"
	@echo "═══════════════════════════════════════════════"
	@mkdir -p $$HOME/.claude/skills
	@count_new=0; count_have=0; count_skip=0; \
	for skill_dir in $$(find $(CURDIR)/.claude/skills -maxdepth 1 -mindepth 1 -type d | sort); do \
		skill_name=$$(basename "$$skill_dir"); \
		target="$$HOME/.claude/skills/$$skill_name"; \
		if [ ! -e "$$target" ] && [ ! -L "$$target" ]; then \
			ln -s "$$skill_dir" "$$target"; \
			echo " + $$skill_name  (symlinked)"; \
			count_new=$$((count_new + 1)); \
		elif [ -L "$$target" ] && [ "$$(readlink "$$target")" = "$$skill_dir" ]; then \
			echo " = $$skill_name  (already linked to this repo)"; \
			count_have=$$((count_have + 1)); \
		else \
			echo " ! $$skill_name  (exists, not from this repo — skipping; remove manually if you want to replace)"; \
			count_skip=$$((count_skip + 1)); \
		fi; \
	done; \
	echo ""; \
	echo " Summary: $$count_new newly linked, $$count_have already linked, $$count_skip skipped (conflict)"
	@echo ""
	@echo " Verify: 'ls -la ~/.claude/skills/' should show symlinks pointing to $(CURDIR)/.claude/skills/"
	@echo " Remove: 'make uninstall-user-skills'"

# Remove the symlinks created by install-user-skills (only those pointing to THIS clone).
uninstall-user-skills:
	@echo "Removing skill symlinks in ~/.claude/skills/ that point to $(CURDIR)..."
	@count=0; \
	for link in $$(find $$HOME/.claude/skills -maxdepth 1 -type l 2>/dev/null); do \
		target=$$(readlink "$$link"); \
		case "$$target" in \
			$(CURDIR)/*) \
				rm "$$link"; \
				echo " - $$(basename $$link)"; \
				count=$$((count + 1)); \
				;; \
		esac; \
	done; \
	echo ""; \
	echo " Removed $$count symlink(s)."

# Register rick_mcp at user scope in Claude Code so it's available from any directory
# (not just when launching Claude Code from this repo). Opt-in — run this manually.
# Uses absolute paths derived from $(CURDIR) so no path-typing required.
install-user-mcp:
	@echo "═══════════════════════════════════════════════"
	@echo " Installing rick_mcp at USER scope (Claude Code)"
	@echo "═══════════════════════════════════════════════"
	@if ! command -v claude >/dev/null 2>&1; then \
		echo " ERROR: claude CLI not found in PATH."; \
		echo " Install Claude Code first, then re-run."; \
		exit 1; \
	fi
	@if [ ! -x $(VENV_PYTHON) ]; then \
		echo " ERROR: $(VENV_PYTHON) not found. Run 'make setup' first."; \
		exit 1; \
	fi
	claude mcp add --scope user rick_mcp $(CURDIR)/$(VENV_PYTHON) $(CURDIR)/rick_mcp.py
	@echo ""
	@echo " ✓ rick_mcp registered at user scope."
	@echo "   Python:  $(CURDIR)/$(VENV_PYTHON)"
	@echo "   Entry:   $(CURDIR)/rick_mcp.py"
	@echo ""
	@echo " Verify: run 'claude' from any directory, then '/mcp'."
	@echo " Remove: 'claude mcp remove rick_mcp'."

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
