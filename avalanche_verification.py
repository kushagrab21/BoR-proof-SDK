#!/usr/bin/env python3
"""
==========================================================
⚡ BoR-Proof SDK — Avalanche Verification Experiment
==========================================================

This script demonstrates the cryptographic avalanche effect in the BoR-Proof SDK.
A single-line logic change (+1) causes massive divergence in the HMASTER hash,
proving that SHA-256's avalanche property ensures tamper-evidence.

Usage:
    python avalanche_verification.py

Requirements:
    - bor-sdk installed
    - matplotlib, numpy
"""

import json
import hashlib
import subprocess
import sys
import os
from pathlib import Path

try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError:
    print("❌ Missing dependencies. Installing matplotlib and numpy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"])
    import numpy as np
    import matplotlib.pyplot as plt


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n=== {description} ===")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout


def bit_array(hex_hash):
    """Convert hex hash to binary bit array (256 bits for SHA-256)."""
    return np.array(list(bin(int(hex_hash, 16))[2:].zfill(256))).astype(int)


def main():
    print("=" * 60)
    print("⚡ BoR-Proof SDK — Avalanche Verification Experiment")
    print("=" * 60)

    # ----------------------------------------------------------
    # 1️⃣ Run official proof
    # ----------------------------------------------------------
    run_command(
        "borp prove --all "
        "--initial '7' "
        "--config '{\"offset\":4}' "
        "--version 'v1.0' "
        "--stages examples.demo:add examples.demo:square "
        "--outdir out_ref",
        "🧩 Running Official Proof"
    )

    ref_bundle_path = Path("out_ref/rich_proof_bundle.json")
    if not ref_bundle_path.exists():
        print(f"❌ Reference bundle not found: {ref_bundle_path}")
        sys.exit(1)

    with open(ref_bundle_path) as f:
        ref = json.load(f)

    HMASTER_ref = ref["primary"]["master"]
    H_RICH_ref = ref["H_RICH"]
    print(f"\n✓ HMASTER_ref = {HMASTER_ref}")
    print(f"✓ H_RICH_ref  = {H_RICH_ref}")

    # ----------------------------------------------------------
    # 2️⃣ Create modified logic (+1) and rerun
    # ----------------------------------------------------------
    print("\n=== ⚙️ Creating Modified Logic (+1) ===")

    modified_script = """from bor.decorators import step

@step
def add(x, C, V):
    return x + C["offset"] + 1  # logic mutation: adds +1

@step
def square(x, C, V):
    return x * x
"""

    # Ensure current directory is in PYTHONPATH
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    with open("demo_modified.py", "w") as f:
        f.write(modified_script)

    print("✓ Created demo_modified.py with +1 mutation")

    run_command(
        f'PYTHONPATH="{current_dir}:$PYTHONPATH" borp prove --all '
        "--initial '7' "
        "--config '{\"offset\":4}' "
        "--version 'v1.0' "
        "--stages demo_modified:add demo_modified:square "
        "--outdir out_mod",
        "🧩 Running Modified Proof"
    )

    mod_bundle_path = Path("out_mod/rich_proof_bundle.json")
    if not mod_bundle_path.exists():
        print(f"❌ Modified bundle not found: {mod_bundle_path}")
        sys.exit(1)

    with open(mod_bundle_path) as f:
        mod = json.load(f)

    HMASTER_mod = mod["primary"]["master"]
    H_RICH_mod = mod["H_RICH"]
    print(f"\n✓ HMASTER_mod = {HMASTER_mod}")
    print(f"✓ H_RICH_mod  = {H_RICH_mod}")

    # ----------------------------------------------------------
    # 3️⃣ Bitwise analysis of divergence
    # ----------------------------------------------------------
    print("\n=== 🔬 Bitwise Divergence Analysis ===")

    ref_bits = bit_array(HMASTER_ref)
    mod_bits = bit_array(HMASTER_mod)
    xor_bits = (ref_bits != mod_bits).astype(int)

    flips = xor_bits.sum()
    pct = flips / 256 * 100

    print(f"\nBitwise Hamming Distance: {flips}/256 bits ({pct:.2f}% flipped)")
    print(f"Expected for ideal avalanche: ~50% (128/256 bits)")
    print(f"Observed: {pct:.2f}%")

    # ----------------------------------------------------------
    # 4️⃣ Visualization (side-by-side)
    # ----------------------------------------------------------
    print("\n=== 🎨 Generating Visualization ===")

    ref_grid = ref_bits.reshape(16, 16)
    mod_grid = mod_bits.reshape(16, 16)
    xor_grid = xor_bits.reshape(16, 16)

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    axs[0].imshow(ref_grid, cmap="Greens", interpolation="nearest")
    axs[0].set_title("Official HMASTER\n(examples.demo:add)", fontsize=10)

    axs[1].imshow(xor_grid, cmap="Reds", interpolation="nearest")
    axs[1].set_title(f"Bit Flips\n{flips}/256 bits ({pct:.2f}%)", fontsize=10)

    axs[2].imshow(mod_grid, cmap="Blues", interpolation="nearest")
    axs[2].set_title("Modified HMASTER\n(demo_modified:add +1)", fontsize=10)

    for ax in axs:
        ax.axis("off")

    plt.suptitle(
        "⚡ Avalanche Verification — BoR-Proof SDK v1.0.0\n"
        "Single-line logic change (+1) causes massive cryptographic divergence",
        fontsize=12,
        fontweight="bold"
    )

    plt.tight_layout()

    # Save visualization
    output_path = Path("avalanche_report.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ Visualization saved to: {output_path}")

    # Display if running interactively
    try:
        plt.show()
    except:
        pass

    # ----------------------------------------------------------
    # 5️⃣ Summary and Verdict
    # ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("⚡ AVALANCHE DIVERGENCE REPORT")
    print("=" * 60)
    print(f"\nOfficial HMASTER  : {HMASTER_ref}")
    print(f"Modified HMASTER  : {HMASTER_mod}")
    print(f"\nOfficial H_RICH   : {H_RICH_ref}")
    print(f"Modified H_RICH   : {H_RICH_mod}")
    print(f"\nBitwise Hamming Distance: {flips}/256 bits ({pct:.2f}% flipped)")

    if pct > 40:
        print("\n✅ VERDICT: Avalanche property confirmed — cryptographic divergence is massive.")
        print("   Even a single-line logic change (+1) causes ~50% bit flips in HMASTER.")
        print("   This proves tamper-evidence and deterministic integrity.")
    else:
        print(f"\n⚠️ VERDICT: Divergence ({pct:.2f}%) below expected threshold (>40%).")
        print("   This may indicate unexpected behavior or hash collision (extremely unlikely).")

    print("\n" + "=" * 60)
    print("✓ Avalanche verification complete.")
    print(f"✓ Report saved to: {output_path.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()

