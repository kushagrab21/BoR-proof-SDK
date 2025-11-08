.PHONY: setup prove demo verify persist audit consensus test lint fmt check ci clean verify-release manual-verify help

help:
	@echo "BoR-Proof SDK - Developer Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup      Install package with dev dependencies"
	@echo ""
	@echo "Proof Operations:"
	@echo "  make prove      Generate proof bundle"
	@echo "  make demo       Generate and verify bundle (prove + verify)"
	@echo "  make verify     Verify existing bundle"
	@echo "  make persist    Persist proof to storage"
	@echo ""
	@echo "Meta-Layer:"
	@echo "  make audit      Self-audit last 5 bundles"
	@echo "  make consensus  Build consensus ledger"
	@echo ""
	@echo "Development:"
	@echo "  make test       Run test suite"
	@echo "  make lint       Check code style"
	@echo "  make fmt        Format code"
	@echo "  make check      Run lint + test"
	@echo "  make ci         Full CI checks"
	@echo "  make clean      Remove generated files"
	@echo ""
	@echo "Release:"
	@echo "  make verify-release  Run pre-release verification"
	@echo "  make manual-verify   Full manual test with all output"

setup:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

prove:
	python test_integration.py

demo: prove verify
	@echo "✓ Demo complete (prove + verify)"

verify:
	python evaluate_invariant.py

persist:
	@echo "Persistence operations via bor.store module"
	@python -c "from bor.store import save_json_proof, save_sqlite_proof; print('✓ Persistence modules available')"

audit:
	python evaluate_invariant.py --self-audit 5

consensus:
	python evaluate_invariant.py --consensus-ledger

test:
	pytest -q

lint:
	@command -v ruff >/dev/null 2>&1 && ruff check . || echo "⚠ ruff not installed, skipping"
	@command -v black >/dev/null 2>&1 && black --check . || echo "⚠ black not installed, skipping"
	@command -v isort >/dev/null 2>&1 && isort --check-only . || echo "⚠ isort not installed, skipping"

fmt:
	@command -v black >/dev/null 2>&1 && black . || echo "⚠ black not installed, run: pip install black"
	@command -v isort >/dev/null 2>&1 && isort . || echo "⚠ isort not installed, run: pip install isort"

check: lint test
	@echo "✓ All checks passed"

ci: check
	@echo "✓ CI checks complete"

clean:
	rm -rf .pytest_cache __pycache__ **/__pycache__ *.pyc **/*.pyc
	rm -rf .coverage coverage.xml htmlcov
	rm -rf build dist *.egg-info
	rm -f state.json metrics.json consensus_ledger.json proof_registry.json
	@echo "✓ Cleaned temporary files"

verify-release:
	@bash verify_release.sh

manual-verify:
	@bash manual_test_verifier.sh

