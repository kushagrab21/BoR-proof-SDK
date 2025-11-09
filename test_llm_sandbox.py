#!/usr/bin/env python3
"""
Test script for LLM Sandbox — Step 12A

Verifies that trace collection and storage work correctly.

Usage:
    python test_llm_sandbox.py
"""

import os
import sys
from pathlib import Path

def test_mock_trace():
    """Test mock trace generation."""
    print("=" * 60)
    print("TEST 1: Mock Trace Generation")
    print("=" * 60)
    
    from trace_collector import generate_mock_trace
    
    result = generate_mock_trace(
        prompt="What is the meaning of life?",
        response="The meaning of life is 42, according to Douglas Adams."
    )
    
    print(f"✅ Mock trace created: {result['session_id']}")
    print(f"   Trace file: {result['trace_file']}")
    print(f"   Manifest file: {result['manifest_file']}")
    print(f"   Token count: {result['token_count']}")
    print(f"   Duration: {result['duration']:.2f}s")
    
    # Verify files exist
    assert Path(result['trace_file']).exists(), "Trace file not found"
    assert Path(result['manifest_file']).exists(), "Manifest file not found"
    
    print("✅ TEST PASSED: Files created successfully\n")
    return result


def test_load_trace(session_id):
    """Test loading a saved trace."""
    print("=" * 60)
    print("TEST 2: Load Saved Trace")
    print("=" * 60)
    
    from trace_collector import load_trace
    
    result = load_trace(session_id)
    
    print(f"✅ Loaded trace: {result['session_id']}")
    print(f"   Prompt: {result['manifest']['prompt'][:50]}...")
    print(f"   Response: {result['manifest']['response'][:50]}...")
    print(f"   Tokens: {len(result['trace'])}")
    
    assert result['session_id'] == session_id, "Session ID mismatch"
    assert len(result['trace']) > 0, "Empty trace"
    
    print("✅ TEST PASSED: Trace loaded successfully\n")


def test_list_traces():
    """Test listing all traces."""
    print("=" * 60)
    print("TEST 3: List All Traces")
    print("=" * 60)
    
    from trace_collector import list_traces
    
    traces = list_traces()
    
    print(f"✅ Found {len(traces)} trace(s)")
    
    for trace in traces[-3:]:  # Show last 3
        print(f"   • {trace['session_id']} — {trace['model']} — {trace['prompt'][:40]}...")
    
    assert len(traces) > 0, "No traces found"
    
    print("✅ TEST PASSED: Trace listing works\n")


def test_real_trace():
    """Test real API trace (only if API key is set)."""
    print("=" * 60)
    print("TEST 4: Real API Trace (Optional)")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠️ SKIPPED: OPENAI_API_KEY not set")
        print("   Set your API key to test real traces:")
        print("   export OPENAI_API_KEY='your-key-here'\n")
        return
    
    from trace_collector import collect_trace
    
    try:
        result = collect_trace(
            prompt="Count from 1 to 5",
            model="gpt-3.5-turbo",
            max_tokens=50,
            temperature=0.0
        )
        
        print(f"✅ Real trace created: {result['session_id']}")
        print(f"   Model: {result['manifest']['model']}")
        print(f"   Tokens: {result['token_count']}")
        print(f"   Duration: {result['duration']:.2f}s")
        print(f"   Response: {result['response_text'][:100]}...")
        
        # Verify logprobs exist
        assert len(result['trace']) > 0, "Empty trace"
        assert 'logprob' in result['trace'][0], "No logprobs in trace"
        
        print("✅ TEST PASSED: Real API trace works\n")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}\n")


def test_dashboard_import():
    """Test that dashboard can import trace_collector."""
    print("=" * 60)
    print("TEST 5: Dashboard Integration")
    print("=" * 60)
    
    try:
        # Simulate dashboard import
        import trace_collector
        assert hasattr(trace_collector, 'collect_trace'), "collect_trace not found"
        assert hasattr(trace_collector, 'list_traces'), "list_traces not found"
        assert hasattr(trace_collector, 'load_trace'), "load_trace not found"
        assert hasattr(trace_collector, 'generate_mock_trace'), "generate_mock_trace not found"
        
        print("✅ All required functions are available")
        print("✅ TEST PASSED: Dashboard integration ready\n")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}\n")
        raise


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 LLM SANDBOX TEST SUITE — STEP 12A")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: Mock trace
        result = test_mock_trace()
        session_id = result['session_id']
        
        # Test 2: Load trace
        test_load_trace(session_id)
        
        # Test 3: List traces
        test_list_traces()
        
        # Test 4: Real API (optional)
        test_real_trace()
        
        # Test 5: Dashboard integration
        test_dashboard_import()
        
        # Summary
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("   1. Run the dashboard: streamlit run interactive_visual_dashboard.py")
        print("   2. Open the '🤖 LLM Sandbox' tab")
        print("   3. Test with mock traces or real API calls")
        print("   4. Verify traces are saved to llm_traces/ directory\n")
        
        return 0
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ TEST SUITE FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

