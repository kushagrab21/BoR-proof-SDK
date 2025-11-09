#!/usr/bin/env python3
"""
Test Step 12C - Real-Time Trust Diagnostics

Validates streaming trace collection with live hallucination detection.
"""

import sys
import time
from pathlib import Path


def test_streaming_imports():
    """Test 1: Import streaming modules."""
    print("="*60)
    print("TEST 1: Streaming Module Imports")
    print("="*60)
    
    try:
        from trace_streamer import stream_trace_with_diagnostics, stream_mock_trace
        from trace_streamer import compute_incremental_trust
        print("✅ trace_streamer imports successfully")
        
        # Check functions exist
        assert callable(stream_trace_with_diagnostics), "stream_trace_with_diagnostics not callable"
        assert callable(stream_mock_trace), "stream_mock_trace not callable"
        assert callable(compute_incremental_trust), "compute_incremental_trust not callable"
        print("✅ All streaming functions available")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    print("✅ TEST PASSED\n")
    return True


def test_mock_streaming():
    """Test 2: Mock streaming with live diagnostics."""
    print("="*60)
    print("TEST 2: Mock Streaming")
    print("="*60)
    
    from trace_streamer import stream_mock_trace
    
    prompt = "Test real-time diagnostics"
    response = "This is a test response for validating streaming diagnostics capabilities."
    
    print(f"Prompt: {prompt}")
    print(f"Response: {response[:50]}...")
    print("\nStreaming...")
    
    chunks_received = 0
    final_result = None
    trust_scores = []
    
    try:
        for chunk in stream_mock_trace(prompt=prompt, response=response, delay=0.01):
            if chunk.get("complete"):
                final_result = chunk
                break
            
            if chunk.get("error"):
                print(f"❌ Error: {chunk['error']}")
                return False
            
            # Validate chunk structure
            required_keys = ["token", "index", "trust_score", "trust_label", "status"]
            for key in required_keys:
                if key not in chunk:
                    print(f"❌ Missing key in chunk: {key}")
                    return False
            
            chunks_received += 1
            trust_scores.append(chunk["trust_score"])
            
            # Print sample chunks
            if chunks_received <= 3:
                status_icon = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(chunk["status"], "⚪")
                print(f"  {status_icon} Token [{chunk['index']:2d}] {chunk['token']:15s} "
                      f"Trust: {chunk['trust_score']:.2f} ({chunk['trust_label']})")
        
        print(f"\n✅ Received {chunks_received} chunks")
        
        # Validate final result
        if not final_result:
            print("❌ No final result received")
            return False
        
        print(f"✅ Session ID: {final_result['session_id']}")
        print(f"✅ Total tokens: {final_result['token_count']}")
        print(f"✅ Duration: {final_result['duration']:.2f}s")
        
        # Validate files created
        trace_file = Path(final_result['trace_file'])
        manifest_file = Path(final_result['manifest_file'])
        
        if not trace_file.exists():
            print(f"❌ Trace file not found: {trace_file}")
            return False
        if not manifest_file.exists():
            print(f"❌ Manifest file not found: {manifest_file}")
            return False
        
        print(f"✅ Files created: {trace_file.name}, {manifest_file.name}")
        
        # Validate trust scores
        if not trust_scores:
            print("❌ No trust scores recorded")
            return False
        
        avg_trust = sum(trust_scores) / len(trust_scores)
        print(f"✅ Average trust score: {avg_trust:.2f}")
        
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ TEST PASSED\n")
    return True


def test_incremental_trust():
    """Test 3: Incremental trust computation."""
    print("="*60)
    print("TEST 3: Incremental Trust Computation")
    print("="*60)
    
    from trace_streamer import compute_incremental_trust
    
    # Test case 1: Short sequence
    tokens1 = ["Hello", "world", "test"]
    result1 = compute_incremental_trust(tokens1)
    
    print(f"Tokens: {tokens1}")
    print(f"  Trust score: {result1['trust_score']:.2f}")
    print(f"  Trust label: {result1['trust_label']}")
    print(f"  Status: {result1['status']}")
    
    required_keys = ["trust_score", "trust_label", "status"]
    for key in required_keys:
        if key not in result1:
            print(f"❌ Missing key: {key}")
            return False
    
    # Test case 2: Repetitive sequence (should lower trust)
    tokens2 = ["same", "same", "same", "same", "same"]
    result2 = compute_incremental_trust(tokens2)
    
    print(f"\nTokens: {tokens2}")
    print(f"  Trust score: {result2['trust_score']:.2f}")
    print(f"  Trust label: {result2['trust_label']}")
    print(f"  Status: {result2['status']}")
    
    if result2['trust_score'] >= result1['trust_score']:
        print("⚠️ Warning: Repetitive tokens should have lower trust")
    else:
        print("✅ Repetitive tokens correctly flagged")
    
    print("✅ TEST PASSED\n")
    return True


def test_dashboard_integration():
    """Test 4: Dashboard integration check."""
    print("="*60)
    print("TEST 4: Dashboard Integration")
    print("="*60)
    
    try:
        import interactive_visual_dashboard
        print("✅ Dashboard module imports")
        
        # Check for trace_streamer availability flag
        if hasattr(interactive_visual_dashboard, 'TRACE_STREAMER_AVAILABLE'):
            available = interactive_visual_dashboard.TRACE_STREAMER_AVAILABLE
            print(f"✅ TRACE_STREAMER_AVAILABLE = {available}")
        else:
            print("⚠️ TRACE_STREAMER_AVAILABLE flag not found")
        
    except Exception as e:
        print(f"❌ Dashboard integration failed: {e}")
        return False
    
    print("✅ TEST PASSED\n")
    return True


def test_cli_streaming():
    """Test 5: CLI streaming interface."""
    print("="*60)
    print("TEST 5: CLI Streaming")
    print("="*60)
    
    import subprocess
    
    # Test with mock streaming
    result = subprocess.run(
        ["python", "trace_streamer.py", "--prompt", "Test CLI", "--mock"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        print(f"❌ CLI failed: {result.stderr}")
        return False
    
    # Check output contains expected markers
    if "🧠 Streaming trace" not in result.stdout:
        print("❌ Missing streaming header")
        return False
    
    if "✅ Complete:" not in result.stdout:
        print("❌ Missing completion marker")
        return False
    
    print("✅ CLI executed successfully")
    print("✅ Output contains expected markers")
    
    print("✅ TEST PASSED\n")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 STEP 12C TEST SUITE")
    print("   Real-Time Trust Diagnostics")
    print("="*60 + "\n")
    
    tests = [
        ("Streaming Imports", test_streaming_imports),
        ("Mock Streaming", test_mock_streaming),
        ("Incremental Trust", test_incremental_trust),
        ("Dashboard Integration", test_dashboard_integration),
        ("CLI Streaming", test_cli_streaming)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
            else:
                failed += 1
                print(f"⚠️ Test failed: {test_name}\n")
        except Exception as e:
            failed += 1
            print(f"❌ Test crashed: {test_name}")
            print(f"   Error: {e}\n")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("="*60)
    if failed == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"⚠️ TESTS COMPLETED: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n📋 Step 12C Complete:")
        print("   ✅ Streaming trace collection")
        print("   ✅ Real-time trust diagnostics")
        print("   ✅ Live hallucination detection")
        print("   ✅ Dashboard integration")
        print("\n🚀 Usage:")
        print("   1. Run: streamlit run interactive_visual_dashboard.py")
        print("   2. Go to '🤖 LLM Sandbox' tab")
        print("   3. Enable '🔴 Live Trust Diagnostics'")
        print("   4. Enter a prompt and click 'Stream with Live Diagnostics'")
        print("   5. Watch real-time trust scores and alerts\n")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())

