#!/bin/bash
# BoR Trace Verification Pipeline
# Converts LLM trace to BoR format and runs full verification

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Help message
show_help() {
    cat << EOF
🔐 BoR Trace Verification Pipeline

Usage:
    ./verify_trace.sh <session_id>
    ./verify_trace.sh --trace llm_traces/trace_<id>.json
    
Examples:
    ./verify_trace.sh bfd64e85
    ./verify_trace.sh --trace llm_traces/trace_bfd64e85.json

Steps:
    1. Convert trace to BoR visual_data.json format
    2. Compute hallucination guards
    3. Generate proof visualizations
    4. Display verification summary

Output:
    bor_inputs/visual_data_trace.json    - BoR-formatted data
    figures/                             - Generated visualizations
EOF
}

# Parse arguments
SESSION_ID=""
TRACE_FILE=""

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

if [ "$1" == "--trace" ]; then
    TRACE_FILE="$2"
    # Extract session ID from trace file
    SESSION_ID=$(basename "$TRACE_FILE" .json | sed 's/trace_//')
else
    SESSION_ID="$1"
fi

echo -e "${YELLOW}🔐 BoR Trace Verification Pipeline${NC}"
echo -e "Session ID: ${GREEN}$SESSION_ID${NC}"
echo ""

# Step 1: Extract trace to BoR format
echo -e "${YELLOW}⚙️  Step 1/3: Converting trace to BoR format...${NC}"
if [ -n "$TRACE_FILE" ]; then
    python extract_trace_for_bor.py --trace "$TRACE_FILE"
else
    python extract_trace_for_bor.py --session "$SESSION_ID"
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Extraction failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Trace converted to BoR format${NC}"
echo ""

# Step 2: Compute hallucination guards
echo -e "${YELLOW}⚙️  Step 2/3: Computing hallucination guards...${NC}"
python compute_hallucination_guards.py --input bor_inputs/visual_data_trace.json 2>&1 | grep -v "Some weights of the model checkpoint"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Guard computation may have issues (check output above)${NC}"
else
    echo -e "${GREEN}✅ Hallucination guards computed${NC}"
fi
echo ""

# Step 3: Generate visualizations
echo -e "${YELLOW}⚙️  Step 3/3: Generating proof visualizations...${NC}"
python generate_all_visualizations.py --visual-data bor_inputs/visual_data_trace.json 2>&1 | head -20

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Visualization generation may have issues${NC}"
else
    echo -e "${GREEN}✅ Visualizations generated${NC}"
fi
echo ""

# Display summary
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Verification Complete${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Extract and display summary stats
if [ -f bor_inputs/visual_data_trace.json ]; then
    python -c "
import json
with open('bor_inputs/visual_data_trace.json', 'r') as f:
    data = json.load(f)
    steps = data.get('steps', [])
    status_counts = {'green': 0, 'yellow': 0, 'red': 0}
    for step in steps:
        status = step.get('guard_state', {}).get('status', 'green')
        status_counts[status] += 1
    
    print(f'📊 Verification Summary:')
    print(f'   Total Steps: {len(steps)}')
    print(f'   🟢 Trusted: {status_counts[\"green\"]}')
    print(f'   🟡 Review: {status_counts[\"yellow\"]}')
    print(f'   🔴 Untrusted: {status_counts[\"red\"]}')
    
    if status_counts['red'] > 0:
        alert_rate = (status_counts['red'] / len(steps)) * 100
        print(f'   🚨 Alert Rate: {alert_rate:.1f}%')
"
fi

echo ""
echo -e "${YELLOW}📋 Output Files:${NC}"
echo "   • bor_inputs/visual_data_trace.json"
echo "   • figures/ (visualizations)"
echo ""
echo -e "${YELLOW}🚀 Next Steps:${NC}"
echo "   • View in dashboard: streamlit run interactive_visual_dashboard.py"
echo "   • Inspect figures: ls -la figures/"
echo "   • Review data: cat bor_inputs/visual_data_trace.json | jq"

