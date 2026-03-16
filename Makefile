.PHONY: check fix test lint format-check typecheck coverage smoke clean

# Run everything — the full inspection
check: lint format-check typecheck test
	@echo ""
	@echo "═══════════════════════════════════════════════"
	@echo " ALL CHECKS PASSED — Semper Fidelis"
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

# Smoke test — fire every tool once, verify output
smoke:
	@echo "═══════════════════════════════════════════════"
	@echo " SMOKE TEST — Firing all 20 tools"
	@echo "═══════════════════════════════════════════════"
	@python smoke_test.py
	@echo ""
	@echo "═══════════════════════════════════════════════"
	@echo " ALL TOOLS OPERATIONAL — Semper Fidelis"
	@echo "═══════════════════════════════════════════════"

# Clean build/test artifacts
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist *.egg-info
	find . -type d -name __pycache__ -not -path './venv/*' -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean."
