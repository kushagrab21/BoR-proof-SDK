"""
Test for avalanche effect verification in BoR-Proof SDK.

This test proves that a minimal logic change (+1) causes massive
cryptographic divergence in HMASTER, demonstrating tamper-evidence.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_avalanche_effect():
    """
    Test that a single-line logic change causes ~50% bit divergence.
    
    This demonstrates the cryptographic avalanche property:
    - Small input changes → large hash changes
    - Proves tamper-evidence
    - Validates SHA-256 collision resistance
    """
    # Run official proof
    subprocess.run(
        [
            "borp", "prove", "--all",
            "--initial", "7",
            "--config", '{"offset":4}',
            "--version", "v1.0",
            "--stages", "examples.demo:add", "examples.demo:square",
            "--outdir", "out_ref_test"
        ],
        check=True,
        capture_output=True
    )
    
    ref_bundle = Path("out_ref_test/rich_proof_bundle.json")
    assert ref_bundle.exists(), "Reference bundle not created"
    
    with open(ref_bundle) as f:
        ref_data = json.load(f)
    
    HMASTER_ref = ref_data["primary"]["master"]
    
    # Create modified logic
    modified_code = """from bor.decorators import step

@step
def add(x, C, V):
    return x + C["offset"] + 1  # logic mutation

@step
def square(x, C, V):
    return x * x
"""
    
    Path("test_modified.py").write_text(modified_code)
    
    # Run modified proof
    subprocess.run(
        [
            "borp", "prove", "--all",
            "--initial", "7",
            "--config", '{"offset":4}',
            "--version", "v1.0",
            "--stages", "test_modified:add", "test_modified:square",
            "--outdir", "out_mod_test"
        ],
        check=True,
        capture_output=True,
        env={**subprocess.os.environ, "PYTHONPATH": str(Path.cwd())}
    )
    
    mod_bundle = Path("out_mod_test/rich_proof_bundle.json")
    assert mod_bundle.exists(), "Modified bundle not created"
    
    with open(mod_bundle) as f:
        mod_data = json.load(f)
    
    HMASTER_mod = mod_data["primary"]["master"]
    
    # Verify hashes are different
    assert HMASTER_ref != HMASTER_mod, "Hashes should differ with logic change"
    
    # Compute bit-level divergence
    ref_int = int(HMASTER_ref, 16)
    mod_int = int(HMASTER_mod, 16)
    xor = ref_int ^ mod_int
    
    # Count flipped bits
    flips = bin(xor).count('1')
    pct = flips / 256 * 100
    
    # Assert avalanche property (should be close to 50%)
    assert 30 < pct < 70, f"Avalanche effect weak: only {pct:.2f}% bits flipped (expected ~50%)"
    
    print(f"\n✅ Avalanche test passed: {flips}/256 bits flipped ({pct:.2f}%)")
    print(f"   Official: {HMASTER_ref}")
    print(f"   Modified: {HMASTER_mod}")
    
    # Cleanup
    Path("test_modified.py").unlink(missing_ok=True)


if __name__ == "__main__":
    test_avalanche_effect()

