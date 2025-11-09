#!/bin/bash
# BoR-SDK Visual Proof Pipeline Orchestrator
# Runs the complete extraction → guards → visualization → verification → docs pipeline

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
STRICT_MODE=false
SESSION_ID=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --strict)
            STRICT_MODE=true
            shift
            ;;
        --session)
            SESSION_ID="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --strict       Fail on verification warnings (strict mode)"
            echo "  --session ID   Specify session ID (for future use)"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         BoR-SDK Visual Proof Pipeline Orchestrator                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Starting pipeline execution at $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Create timestamp for bundle
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
BUNDLE_DIR="visual_proofs/${TIMESTAMP}"

# Track timing
START_TIME=$(date +%s)

# Step 1: Extract trace data
echo -e "${YELLOW}[1/5]${NC} Extracting trace data..."
STEP_START=$(date +%s)
if python extract_trace_data.py; then
    STEP_END=$(date +%s)
    echo -e "${GREEN}✅ Extraction complete${NC} ($(($STEP_END - $STEP_START))s)"
    echo ""
else
    echo -e "${RED}❌ Extraction failed${NC}"
    exit 1
fi

# Step 2: Compute hallucination guards
echo -e "${YELLOW}[2/5]${NC} Computing hallucination guards..."
STEP_START=$(date +%s)
if python compute_hallucination_guards.py; then
    STEP_END=$(date +%s)
    echo -e "${GREEN}✅ Guard computation complete${NC} ($(($STEP_END - $STEP_START))s)"
    echo ""
else
    echo -e "${RED}❌ Guard computation failed${NC}"
    exit 1
fi

# Step 3: Generate visualizations
echo -e "${YELLOW}[3/5]${NC} Generating visualizations..."
STEP_START=$(date +%s)
if python generate_all_visualizations.py; then
    STEP_END=$(date +%s)
    echo -e "${GREEN}✅ Visualization generation complete${NC} ($(($STEP_END - $STEP_START))s)"
    echo ""
else
    echo -e "${RED}❌ Visualization generation failed${NC}"
    exit 1
fi

# Step 4: Verify visual integrity
echo -e "${YELLOW}[4/5]${NC} Verifying visual integrity..."
STEP_START=$(date +%s)

VERIFY_ARGS=""
if [ "$STRICT_MODE" = true ]; then
    echo "   (Running in strict mode - warnings will fail)"
    VERIFY_ARGS="--fail-on-warn"
fi

if python verify_visual_integrity.py $VERIFY_ARGS; then
    STEP_END=$(date +%s)
    echo -e "${GREEN}✅ Verification complete${NC} ($(($STEP_END - $STEP_START))s)"
    echo ""
else
    VERIFY_EXIT=$?
    echo -e "${RED}❌ Verification failed (exit code: $VERIFY_EXIT)${NC}"
    exit $VERIFY_EXIT
fi

# Step 5: Assemble documentation
echo -e "${YELLOW}[5/5]${NC} Assembling documentation..."
STEP_START=$(date +%s)
if python assemble_visual_proof.py; then
    STEP_END=$(date +%s)
    echo -e "${GREEN}✅ Documentation assembly complete${NC} ($(($STEP_END - $STEP_START))s)"
    echo ""
else
    echo -e "${RED}❌ Documentation assembly failed${NC}"
    exit 1
fi

# Create bundle directory
echo "📦 Creating timestamped artifact bundle..."
mkdir -p "$BUNDLE_DIR"

# Copy artifacts
cp -r figures "$BUNDLE_DIR/"
cp visual_data.json "$BUNDLE_DIR/"
cp visual_verification_report.json "$BUNDLE_DIR/"
cp docs/visual_proof.md "$BUNDLE_DIR/"

# Create a manifest
cat > "$BUNDLE_DIR/manifest.json" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "pipeline_version": "1.0.0",
  "strict_mode": $STRICT_MODE,
  "session_id": "${SESSION_ID:-null}",
  "artifacts": [
    "visual_data.json",
    "visual_verification_report.json",
    "visual_proof.md",
    "figures/reasoning_chain.svg",
    "figures/hash_flow.png",
    "figures/hallucination_guard.png",
    "figures/master_certificate_tree.svg",
    "figures/*.spec.json"
  ]
}
EOF

echo -e "${GREEN}✅ Bundle created: ${BUNDLE_DIR}${NC}"
echo ""

# Calculate total time
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

# Print final summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     PIPELINE EXECUTION COMPLETE                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Total execution time: ${TOTAL_TIME}s"
echo ""
echo "📁 Artifacts bundled in: ${BUNDLE_DIR}/"
echo "   - visual_data.json (canonical reasoning trace)"
echo "   - visual_verification_report.json (verification results)"
echo "   - visual_proof.md (complete documentation)"
echo "   - figures/ (4 visualizations + 4 sidecar specs)"
echo ""
echo "📊 Quick stats:"
cat visual_verification_report.json | python -c "import sys, json; d=json.load(sys.stdin); print(f'   - Verification status: {d[\"overall_status\"]}'); print(f'   - Checks passed: {d[\"checks_passed\"]}'); print(f'   - Checks warned: {d[\"checks_warned\"]}'); print(f'   - Checks failed: {d[\"checks_failed\"]}')" 2>/dev/null || echo "   (stats unavailable)"
echo ""
echo "🎉 Visual proof pipeline completed successfully!"
echo "   View results: open ${BUNDLE_DIR}/visual_proof.md"

