#!/usr/bin/env python
"""
Test script to verify invariant framework integration with BoR proof chain.
Builds a complete bundle and checks that hooks are working.
"""

import json
import os
from bor.bundle import build_bundle
from examples.demo import add, square

if __name__ == "__main__":
    print("=" * 70)
    print("Testing BoR Invariant Framework Integration")
    print("=" * 70)
    print()
    
    # Build a complete bundle
    print("Building proof bundle with add→square chain...")
    print()
    
    bundle = build_bundle(
        S0=7,
        C={"offset": 4},
        V="v1.0",
        stages=[add, square]
    )
    
    # Save bundle
    os.makedirs("out", exist_ok=True)
    with open("out/rich_proof_bundle.json", "w") as f:
        json.dump(bundle, f, indent=2)
    
    print()
    print("=" * 70)
    print("Bundle saved to out/rich_proof_bundle.json")
    print("=" * 70)
    print()
    
    # Check if state.json and metrics.json exist
    if os.path.exists("state.json"):
        print("✓ state.json generated")
        with open("state.json") as f:
            state = json.load(f)
            print(f"  - {len(state)} state entries logged")
    else:
        print("✗ state.json not found")
    
    if os.path.exists("metrics.json"):
        print("✓ metrics.json generated")
        with open("metrics.json") as f:
            metrics = json.load(f)
            print(f"  - Metrics: {list(metrics.keys())}")
    else:
        print("✗ metrics.json not found (this is okay if not created yet)")
    
    print()
    print("Bundle details:")
    print(f"  H_MASTER: {bundle.get('H_MASTER', 'N/A')[:16]}...")
    print(f"  H_RICH: {bundle['H_RICH'][:16]}...")
    print(f"  Subproofs: {len(bundle['subproofs'])}")
    print()
    
    print("=" * 70)
    print("Integration test complete!")
    print("=" * 70)

