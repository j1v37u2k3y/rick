.PHONY: check fix test lint format-check typecheck coverage smoke clean file-length setup

MAX_FILE_LINES := 1500

# Run everything — the full inspection
check: lint format-check typecheck file-length test
	@echo ""
	@echo "═══════════════════════════════════════════════"
	@echo " ALL CHECKS PASSED"
	@echo "═══════════════════════════════════════════════"

# Auto-fix what can be fixed
fix:
	ruff check rick_mcp.py rick_mcp/ tests/ smoke_test.py --fix
	ruff format rick_mcp.py rick_mcp/ tests/ smoke_test.py
	@echo "Fixed. Run 'make check' to verify."

# Tests only
test:
	pytest tests/ -v

# Tests with coverage
coverage:
	pytest tests/ -v --cov=rick_mcp --cov-report=term-missing --cov-fail-under=80
	@echo ""
	@echo "Coverage report above. 80% minimum enforced."

# Lint only
lint:
	ruff check rick_mcp.py rick_mcp/ tests/ smoke_test.py

# Format check (no modifications)
format-check:
	ruff format --check rick_mcp.py rick_mcp/ tests/ smoke_test.py

# Type check
typecheck:
	mypy rick_mcp.py --ignore-missing-imports --no-strict-optional

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
	@python smoke_test.py
	@echo ""
	@echo "═══════════════════════════════════════════════"
	@echo " ALL TOOLS OPERATIONAL"
	@echo "═══════════════════════════════════════════════"

# Full dev environment setup
setup:
	@echo "═══════════════════════════════════════════════"
	@echo " RICK MCP — Dev Environment Setup"
	@echo "═══════════════════════════════════════════════"
	pip install -r requirements-dev.txt
	pre-commit install
	@mkdir -p ~/.rick_mcp/soul
	@echo ""
	@echo " Dependencies installed."
	@echo " Pre-commit hooks installed."
	@echo " Private content directory: ~/.rick_mcp/soul/"
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
	@echo "═══════════════════════════════════════════════"
	@echo " Setup complete. Run 'make check' to verify."
	@echo "═══════════════════════════════════════════════"

# Clean build/test artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist *.egg-info
	find . -type d -name __pycache__ -not -path './venv/*' -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean."
