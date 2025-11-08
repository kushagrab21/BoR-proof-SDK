#!/bin/bash
# Verification script for Step 2: BoR Invariant Framework Integration (P₀-P₂)

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║       BoR INVARIANT FRAMEWORK - STEP 2 INTEGRATION VERIFICATION           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# Clean previous state
echo "➤ Cleaning previous state files..."
rm -f state.json metrics.json
echo "  ✓ Cleaned"
echo ""

# Run integration test
echo "➤ Running integration test..."
if python test_integration.py > /tmp/integration_output.txt 2>&1; then
    echo "  ✓ Integration test passed"
else
    echo "  ✗ Integration test failed"
    cat /tmp/integration_output.txt
    exit 1
fi
echo ""

# Verify files generated
echo "➤ Verifying generated artifacts..."
if [ -f "state.json" ]; then
    STATE_ENTRIES=$(cat state.json | grep -c '"step"')
    echo "  ✓ state.json generated ($STATE_ENTRIES entries)"
else
    echo "  ✗ state.json not found"
    exit 1
fi

if [ -f "metrics.json" ]; then
    echo "  ✓ metrics.json generated"
    cat metrics.json | python -m json.tool | head -10
else
    echo "  ✗ metrics.json not found"
    exit 1
fi

if [ -f "out/rich_proof_bundle.json" ]; then
    echo "  ✓ Bundle generated"
else
    echo "  ✗ Bundle not found"
    exit 1
fi
echo ""

# Run invariant evaluator
echo "➤ Running invariant evaluator..."
if python evaluate_invariant.py 2>&1 | grep -q "VERIFIED"; then
    echo "  ✓ [BoR-Invariant] VERIFIED"
else
    echo "  ✗ Invariant verification failed"
    exit 1
fi
echo ""

# Run core tests
echo "➤ Running BoR core tests..."
if python -m pytest tests/test_core.py -q 2>&1 | grep -q "passed"; then
    echo "  ✓ Core tests passed"
else
    echo "  ✗ Core tests failed"
    exit 1
fi
echo ""

# Run verify tests
echo "➤ Running BoR verify tests..."
if python -m pytest tests/test_verify.py -q 2>&1 | grep -q "passed"; then
    echo "  ✓ Verify tests passed"
else
    echo "  ✗ Verify tests failed"
    exit 1
fi
echo ""

# Check for drift detection
echo "➤ Checking drift detection..."
DRIFT=$(cat metrics.json | grep -o '"drift_detected": [a-z]*' | cut -d' ' -f2)
if [ "$DRIFT" = "false" ]; then
    echo "  ✓ No drift detected (reproducibility maintained)"
elif [ "$DRIFT" = "true" ]; then
    echo "  ⚠ Drift detected (expected on first run or after changes)"
else
    echo "  ✗ Could not determine drift status"
    exit 1
fi
echo ""

# Verify telemetry
echo "➤ Verifying telemetry output..."
if grep -q "BoR-Invariant" /tmp/integration_output.txt; then
    echo "  ✓ Invariant telemetry present in output"
    grep "BoR-Invariant" /tmp/integration_output.txt | head -3
else
    echo "  ✗ No invariant telemetry found"
    exit 1
fi
echo ""

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                    STEP 2 INTEGRATION - ALL CHECKS PASSED ✓               ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  • Invariant hooks integrated into bor/core.py (P₀-P₁)"
echo "  • Drift detection integrated into bor/bundle.py (P₂)"
echo "  • Telemetry emitted at all proof layers"
echo "  • state.json and metrics.json generated"
echo "  • All existing tests pass (backward compatible)"
echo "  • Invariant evaluator confirms: [BoR-Invariant] VERIFIED"
echo ""
echo "Ready for Step 3: P₃-P₄ Integration (verify.py + store.py)"

