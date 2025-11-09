#!/usr/bin/env python3
"""
Run all visualization generators.

This master script executes all four visualization generators in sequence.
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_name: str) -> bool:
    """
    Run a visualization script and return success status.
    
    Returns True if successful, False otherwise.
    """
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print('='*70)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Script not found: {script_name}")
        return False


def main():
    """Main execution."""
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║    BoR-SDK Visualization Pipeline - Complete Figure Generation   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    # Check if visual_data.json exists
    if not Path("visual_data.json").exists():
        print("\n❌ Error: visual_data.json not found")
        print("   Run these scripts first:")
        print("   1. python extract_trace_data.py")
        print("   2. python compute_hallucination_guards.py")
        return
    
    # List of visualization scripts
    scripts = [
        "generate_reasoning_chain.py",
        "generate_hash_flow.py",
        "generate_hallucination_guard.py",
        "generate_master_certificate_tree.py"
    ]
    
    # Track results
    results = {}
    
    # Run each script
    for script in scripts:
        success = run_script(script)
        results[script] = success
    
    # Summary
    print("\n" + "="*70)
    print("VISUALIZATION GENERATION SUMMARY")
    print("="*70)
    
    for script, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status:12s} - {script}")
    
    # Overall status
    all_success = all(results.values())
    print("\n" + "="*70)
    
    if all_success:
        print("✅ All visualizations generated successfully!")
        print("\n📁 Output directory: figures/")
        print("   - reasoning_chain.svg")
        print("   - hash_flow.png")
        print("   - hallucination_guard.png")
        print("   - master_certificate_tree.svg")
    else:
        failed_count = sum(1 for v in results.values() if not v)
        print(f"⚠️  {failed_count} visualization(s) failed")
    
    print("="*70)


if __name__ == "__main__":
    main()

