#!/bin/bash
# BoR-SDK Visual Proof Pipeline - Single-Click Verification
# Tests the complete end-to-end system

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     BoR-SDK Visual Proof Pipeline - System Verification Test          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for test results
test_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"
    
    if [ "$status" = "pass" ]; then
        echo -e "  ${GREEN}✅ PASS${NC}: $test_name - $message"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "  ${RED}❌ FAIL${NC}: $test_name - $message"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo "🔧 Pre-flight checks..."
echo ""

# Check Python
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    test_result "Python available" "pass" "version $PYTHON_VERSION"
else
    test_result "Python available" "fail" "Python not found"
fi

# Check required packages
if python -c "import sentence_transformers, transformers, matplotlib, networkx" 2>/dev/null; then
    test_result "Python dependencies" "pass" "All required packages installed"
else
    test_result "Python dependencies" "fail" "Missing packages - run: pip install -r requirements.txt -r requirements-viz.txt"
fi

# Check graphviz
if command -v dot &> /dev/null; then
    test_result "Graphviz" "pass" "dot command available"
else
    test_result "Graphviz" "fail" "graphviz not installed"
fi

echo ""
echo "🚀 Running complete pipeline (strict mode)..."
echo ""

# Run the pipeline
START_TIME=$(date +%s)
if make visualize-strict > /tmp/pipeline_output.log 2>&1; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    test_result "Pipeline execution" "pass" "Completed in ${DURATION}s"
else
    test_result "Pipeline execution" "fail" "Pipeline failed (see /tmp/pipeline_output.log)"
    cat /tmp/pipeline_output.log
    exit 1
fi

echo ""
echo "🔍 Verifying outputs..."
echo ""

# Check visual_data.json
if [ -f visual_data.json ]; then
    STEPS=$(python -c "import json; print(len(json.load(open('visual_data.json'))['steps']))" 2>/dev/null || echo "0")
    test_result "visual_data.json" "pass" "$STEPS reasoning steps extracted"
else
    test_result "visual_data.json" "fail" "File not found"
fi

# Check figures
EXPECTED_FIGURES=("reasoning_chain.svg" "hash_flow.png" "hallucination_guard.png" "master_certificate_tree.svg")
for fig in "${EXPECTED_FIGURES[@]}"; do
    if [ -f "figures/$fig" ]; then
        SIZE=$(ls -lh "figures/$fig" | awk '{print $5}')
        test_result "figures/$fig" "pass" "Generated ($SIZE)"
    else
        test_result "figures/$fig" "fail" "File not found"
    fi
done

# Check sidecar specs
EXPECTED_SPECS=("reasoning_chain.spec.json" "hash_flow.spec.json" "hallucination_guard.spec.json" "master_certificate_tree.spec.json")
for spec in "${EXPECTED_SPECS[@]}"; do
    if [ -f "figures/$spec" ]; then
        test_result "figures/$spec" "pass" "Sidecar present"
    else
        test_result "figures/$spec" "fail" "Sidecar missing"
    fi
done

# Check verification report
if [ -f visual_verification_report.json ]; then
    OVERALL_STATUS=$(python -c "import json; print(json.load(open('visual_verification_report.json'))['overall_status'])" 2>/dev/null || echo "UNKNOWN")
    CHECKS_PASSED=$(python -c "import json; print(json.load(open('visual_verification_report.json'))['checks_passed'])" 2>/dev/null || echo "0")
    CHECKS_WARNED=$(python -c "import json; print(json.load(open('visual_verification_report.json'))['checks_warned'])" 2>/dev/null || echo "0")
    CHECKS_FAILED=$(python -c "import json; print(json.load(open('visual_verification_report.json'))['checks_failed'])" 2>/dev/null || echo "0")
    
    if [ "$OVERALL_STATUS" = "VERIFIED" ]; then
        test_result "Verification status" "pass" "VERIFIED ($CHECKS_PASSED passed, $CHECKS_WARNED warned, $CHECKS_FAILED failed)"
    else
        test_result "Verification status" "fail" "$OVERALL_STATUS ($CHECKS_PASSED passed, $CHECKS_WARNED warned, $CHECKS_FAILED failed)"
    fi
else
    test_result "visual_verification_report.json" "fail" "File not found"
fi

# Check documentation
if [ -f docs/visual_proof.md ]; then
    LINES=$(wc -l < docs/visual_proof.md)
    test_result "docs/visual_proof.md" "pass" "Generated ($LINES lines)"
else
    test_result "docs/visual_proof.md" "fail" "File not found"
fi

# Check bundle was created
if [ -d visual_proofs ]; then
    BUNDLE_COUNT=$(ls -1d visual_proofs/*/ 2>/dev/null | wc -l)
    if [ "$BUNDLE_COUNT" -gt 0 ]; then
        LATEST_BUNDLE=$(ls -td visual_proofs/*/ | head -1)
        test_result "Artifact bundle" "pass" "$BUNDLE_COUNT bundle(s) - latest: $LATEST_BUNDLE"
    else
        test_result "Artifact bundle" "fail" "No bundles found"
    fi
else
    test_result "Artifact bundle" "fail" "visual_proofs/ directory not found"
fi

# Guard metrics check
if [ -f visual_data.json ]; then
    RED_COUNT=$(python -c "import json; d=json.load(open('visual_data.json')); print(sum(1 for s in d['steps'] if s['guard_state']['status']=='red'))" 2>/dev/null || echo "0")
    YELLOW_COUNT=$(python -c "import json; d=json.load(open('visual_data.json')); print(sum(1 for s in d['steps'] if s['guard_state']['status']=='yellow'))" 2>/dev/null || echo "0")
    GREEN_COUNT=$(python -c "import json; d=json.load(open('visual_data.json')); print(sum(1 for s in d['steps'] if s['guard_state']['status']=='green'))" 2>/dev/null || echo "0")
    
    if [ "$STEPS" -gt 0 ]; then
        test_result "Hallucination guards" "pass" "🟢 $GREEN_COUNT green, 🟡 $YELLOW_COUNT yellow, 🔴 $RED_COUNT red"
    else
        test_result "Hallucination guards" "fail" "No steps to analyze"
    fi
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "  TEST SUMMARY"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo "  Total Tests:  $TOTAL_TESTS"
echo -e "  ${GREEN}Passed:       $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed:       $TESTS_FAILED${NC}"
else
    echo -e "  Failed:       $TESTS_FAILED"
fi
echo "  Pass Rate:    ${PASS_RATE}%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ✅ ALL TESTS PASSED ✅                               ║${NC}"
    echo -e "${GREEN}║                                                                        ║${NC}"
    echo -e "${GREEN}║  The BoR-SDK Visual Proof Pipeline is fully operational!              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "📁 View results:"
    if [ -d visual_proofs ]; then
        LATEST=$(ls -td visual_proofs/*/ | head -1)
        echo "   ${LATEST}visual_proof.md"
    fi
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    ❌ TESTS FAILED ❌                                   ║${NC}"
    echo -e "${RED}║                                                                        ║${NC}"
    echo -e "${RED}║  $TESTS_FAILED test(s) failed. Please review the errors above.                    ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "💡 Troubleshooting:"
    echo "   - Check dependencies: pip install -r requirements.txt -r requirements-viz.txt"
    echo "   - Install graphviz: brew install graphviz (macOS) or apt-get install graphviz (Linux)"
    echo "   - View pipeline log: cat /tmp/pipeline_output.log"
    exit 1
fi

