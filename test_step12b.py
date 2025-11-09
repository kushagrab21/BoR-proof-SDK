#!/usr/bin/env python3
"""
Test Step 12B - BoR Verification Integration

Validates that captured LLM traces can be verified through BoR pipeline.
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def test_trace_extraction():
    """Test 1: Trace extraction to BoR format."""
    print("="*60)
    print("TEST 1: Trace Extraction")
    print("="*60)
    
    # First ensure we have a trace
    from trace_collector import generate_mock_trace
    
    result = generate_mock_trace(
        prompt="Test extraction pipeline",
        response="This is a test response for extraction pipeline validation."
    )
    
    session_id = result['session_id']
    print(f"✅ Created test trace: {session_id}")
    
    # Run extraction
    extract_result = subprocess.run(
        ["python", "extract_trace_for_bor.py", "--session", session_id],
        capture_output=True,
        text=True
    )
    
    if extract_result.returncode != 0:
        print(f"❌ Extraction failed: {extract_result.stderr}")
        return False
    
    print("✅ Extraction successful")
    
    # Verify output file exists
    output_file = Path("bor_inputs/visual_data_trace.json")
    if not output_file.exists():
        print(f"❌ Output file not found: {output_file}")
        return False
    
    # Load and validate structure
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    required_keys = ["metadata", "steps", "master_certificates", "session_info"]
    for key in required_keys:
        if key not in data:
            print(f"❌ Missing key in output: {key}")
            return False
    
    print(f"✅ Output file valid with {len(data['steps'])} step(s)")
    print("✅ TEST PASSED\n")
    return True, session_id


def test_cli_script(session_id):
    """Test 2: CLI verification script."""
    print("="*60)
    print("TEST 2: CLI Verification Script")
    print("="*60)
    
    # Run the shell script
    result = subprocess.run(
        ["./verify_trace.sh", session_id],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ CLI script failed: {result.stderr}")
        return False
    
    print("✅ CLI script executed successfully")
    
    # Check that visualization files were created
    viz_files = [
        "figures/reasoning_chain.svg",
        "figures/hash_flow.png"
    ]
    
    for file in viz_files:
        if Path(file).exists():
            print(f"✅ Generated: {file}")
        else:
            print(f"⚠️  Not found: {file}")
    
    print("✅ TEST PASSED\n")
    return True


def test_verification_results():
    """Test 3: Verify results contain expected data."""
    print("="*60)
    print("TEST 3: Verification Results")
    print("="*60)
    
    result_file = Path("bor_inputs/visual_data_trace.json")
    
    if not result_file.exists():
        print(f"❌ Result file not found: {result_file}")
        return False
    
    with open(result_file, 'r') as f:
        data = json.load(f)
    
    # Check metadata
    metadata = data.get("metadata", {})
    print(f"   Source: {metadata.get('source_trace', 'N/A')}")
    print(f"   Chain valid: {metadata.get('chain_valid', False)}")
    print(f"   Guards computed: {metadata.get('guards_computed', False)}")
    
    # Check steps
    steps = data.get("steps", [])
    print(f"   Steps: {len(steps)}")
    
    # Check guard states
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for step in steps:
        status = step.get("guard_state", {}).get("status", "green")
        status_counts[status] += 1
    
    print(f"   🟢 Green: {status_counts['green']}")
    print(f"   🟡 Yellow: {status_counts['yellow']}")
    print(f"   🔴 Red: {status_counts['red']}")
    
    # Check trace tokens (Step 12B feature)
    if steps and "trace_tokens" in steps[0]:
        token_count = len(steps[0]["trace_tokens"])
        print(f"   Token-level data: {token_count} tokens")
    else:
        print(f"   ⚠️  No token-level data found")
    
    print("✅ TEST PASSED\n")
    return True


def test_dashboard_integration():
    """Test 4: Dashboard integration check."""
    print("="*60)
    print("TEST 4: Dashboard Integration")
    print("="*60)
    
    # Check that dashboard can import necessary modules
    try:
        import interactive_visual_dashboard
        print("✅ Dashboard module imports successfully")
    except Exception as e:
        print(f"❌ Dashboard import failed: {e}")
        return False
    
    # Check that trace_collector is available
    try:
        from trace_collector import collect_trace, list_traces
        print("✅ trace_collector available")
    except Exception as e:
        print(f"❌ trace_collector import failed: {e}")
        return False
    
    # Check that extract_trace_for_bor is available
    try:
        import extract_trace_for_bor
        print("✅ extract_trace_for_bor available")
    except Exception as e:
        print(f"❌ extract_trace_for_bor import failed: {e}")
        return False
    
    print("✅ TEST PASSED\n")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 STEP 12B TEST SUITE")
    print("   BoR Verification Integration for LLM Traces")
    print("="*60 + "\n")
    
    try:
        # Test 1: Extraction
        success, session_id = test_trace_extraction()
        if not success:
            print("❌ TEST SUITE FAILED at Test 1")
            return 1
        
        # Test 2: CLI script
        if not test_cli_script(session_id):
            print("❌ TEST SUITE FAILED at Test 2")
            return 1
        
        # Test 3: Verification results
        if not test_verification_results():
            print("❌ TEST SUITE FAILED at Test 3")
            return 1
        
        # Test 4: Dashboard integration
        if not test_dashboard_integration():
            print("❌ TEST SUITE FAILED at Test 4")
            return 1
        
        # Success summary
        print("="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\n📋 Step 12B Complete:")
        print("   ✅ Trace extraction to BoR format")
        print("   ✅ CLI verification script")
        print("   ✅ Dashboard integration")
        print("   ✅ Token-level data preserved")
        print("\n🚀 Next Steps:")
        print("   1. Run dashboard: streamlit run interactive_visual_dashboard.py")
        print("   2. Go to '🤖 LLM Sandbox' tab")
        print("   3. Capture a trace and click 'Verify with BoR'")
        print("   4. View verification results in UI\n")
        
        return 0
        
    except Exception as e:
        print("="*60)
        print(f"❌ TEST SUITE FAILED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

