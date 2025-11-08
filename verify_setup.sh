#!/bin/bash
# Verification script for BoR Invariant Framework setup

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║          BoR INVARIANT FRAMEWORK - SETUP VERIFICATION                     ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Change to the repository directory
cd "$(dirname "$0")"

echo "➤ Checking directory structure..."
if [ -d "src/bor_core" ]; then
    echo "  ✓ src/bor_core/ exists"
else
    echo "  ✗ src/bor_core/ not found"
    exit 1
fi

echo ""
echo "➤ Checking required files..."
for file in "__init__.py" "init_hooks.py" "registry.py" "env_utils.py" "hooks.py" "README.md"; do
    if [ -f "src/bor_core/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

echo ""
echo "➤ Running test suite..."
if python tests/test_invariant_hooks.py 2>&1; then
    echo "  ✓ Tests passed"
else
    echo "  ✗ Tests failed"
    exit 1
fi

echo ""
echo "➤ Verifying imports..."
if PYTHONPATH=src python -c "from bor_core.hooks import pre_run_hook, post_run_hook, transform_hook, register_proof_hook, drift_check_hook" 2>&1; then
    echo "  ✓ All hooks importable"
else
    echo "  ✗ Import failed"
    exit 1
fi

echo ""
echo "➤ Running invariant evaluation..."
if python evaluate_invariant.py 2>&1; then
    echo "  ✓ Invariant evaluator working"
else
    echo "  ✗ Invariant evaluator failed"
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                          ALL CHECKS PASSED ✓                              ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "The BoR Invariant Framework is ready for Step 2 integration!"

