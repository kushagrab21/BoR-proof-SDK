import os, json, numpy as np, matplotlib.pyplot as plt, hashlib, re, textwrap, subprocess, sys

README_PATH = "README.md"
IMG_DIR = "docs"
IMG_PATH = os.path.join(IMG_DIR, "avalanche_bitdiff_report.png")

AVA_START = "<!-- AVA_SECTION_START -->"
AVA_END   = "<!-- AVA_SECTION_END -->"

SECTION_MD_TEMPLATE = """{start}
## 🧠 Deterministic Baseline & Bit-Level Avalanche Verification

This figure visualizes the **256-bit SHA-256 fingerprints** (HMASTER) before and after a single-line logic change, and their bitwise XOR difference. It demonstrates the **avalanche property** (~50% bits flip) — a cryptographic guarantee that even tiny logic edits produce a completely new reasoning identity.

**Hashes**
- Official HMASTER: `{HMASTER_ref}`
- Modified HMASTER: `{HMASTER_mod}`
- Bitwise flips: **{flips}/256** (**{pct:.2f}%**)

![Avalanche Verification](docs/avalanche_bitdiff_report.png)

**How it's computed**
- Official logic: `examples.demo:add`
- Modified logic: `demo_modified:add` (adds **+1**)
- XOR map: red = flipped bit; overlay: green=same, red=flipped.

{end}
"""

def run(cmd):
    res = subprocess.run(cmd, text=True, capture_output=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        raise SystemExit(f"Command failed: {' '.join(cmd)}")
    return res.stdout

def bit_array(hex_hash):
    return np.array(list(bin(int(hex_hash,16))[2:].zfill(256))).astype(int)

def ensure_demo_modified():
    # Create modified logic (+1) deterministically
    with open("demo_modified.py","w") as f:
        f.write("from bor.decorators import step\n"
                "@step\ndef add(x,C,V): return x+C['offset']+1\n"
                "@step\ndef square(x,C,V): return x*x\n")

def gen_bundles():
    # Official
    print("Generating official proof bundle...")
    run(["borp","prove","--all",
         "--initial","7","--config",'{"offset":4}',"--version","v1.0",
         "--stages","examples.demo:add","examples.demo:square","--outdir","out_ref"])
    with open("out_ref/rich_proof_bundle.json") as f:
        ref = json.load(f)
    HMASTER_ref = ref["primary"]["master"]

    # Modified
    print("Generating modified proof bundle...")
    ensure_demo_modified()
    # Add current directory to PYTHONPATH so demo_modified can be imported
    env = os.environ.copy()
    current_dir = os.getcwd()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = current_dir + os.pathsep + env['PYTHONPATH']
    else:
        env['PYTHONPATH'] = current_dir
    
    res = subprocess.run(
        ["borp","prove","--all",
         "--initial","7","--config",'{"offset":4}',"--version","v1.0",
         "--stages","demo_modified:add","demo_modified:square","--outdir","out_mod"],
        text=True, capture_output=True, env=env
    )
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        raise SystemExit(f"Command failed: borp prove (modified)")
    
    with open("out_mod/rich_proof_bundle.json") as f:
        mod = json.load(f)
    HMASTER_mod = mod["primary"]["master"]
    return HMASTER_ref, HMASTER_mod

def render_figure(HMASTER_ref, HMASTER_mod, save_path):
    ref_bits = bit_array(HMASTER_ref)
    mod_bits = bit_array(HMASTER_mod)
    xor_bits = (ref_bits != mod_bits).astype(int)
    flips = int(xor_bits.sum())
    pct = flips/256.0*100

    ref_grid = ref_bits.reshape(16,16)
    mod_grid = mod_bits.reshape(16,16)
    xor_grid = xor_bits.reshape(16,16)

    overlay = np.zeros((16,16,3), dtype=float)
    overlay[...,0] = xor_grid         # red: flipped bits
    overlay[...,1] = 1 - xor_grid     # green: same bits

    fig, axs = plt.subplots(1,4,figsize=(14,4))
    axs[0].imshow(ref_grid, cmap="Greens", interpolation="nearest"); axs[0].set_title("Official HMASTER")
    axs[1].imshow(xor_grid, cmap="Reds",   interpolation="nearest"); axs[1].set_title("Bit Flips (XOR)")
    axs[2].imshow(mod_grid, cmap="Blues",  interpolation="nearest"); axs[2].set_title("Modified HMASTER")
    axs[3].imshow(overlay,                 interpolation="nearest"); axs[3].set_title("Overlay (Green=same, Red=flip)")
    for ax in axs: ax.axis("off")
    plt.suptitle("⚡ Avalanche Verification — BoR-Proof SDK v1.0.0\nSingle-line logic change (+1) causes massive cryptographic divergence", y=1.02)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return flips, pct

def update_readme(HMASTER_ref, HMASTER_mod, flips, pct):
    if not os.path.exists(README_PATH):
        raise SystemExit("README.md not found")

    with open(README_PATH,"r",encoding="utf-8") as f:
        readme = f.read()

    section = SECTION_MD_TEMPLATE.format(
        start=AVA_START, end=AVA_END,
        HMASTER_ref=HMASTER_ref, HMASTER_mod=HMASTER_mod,
        flips=flips, pct=pct
    )

    if AVA_START in readme and AVA_END in readme:
        # Replace existing block
        pattern = re.compile(re.escape(AVA_START) + r".*?" + re.escape(AVA_END), re.DOTALL)
        new_readme = pattern.sub(section, readme)
    else:
        # Append new block at end with spacing
        new_readme = readme.rstrip() + "\n\n" + section + "\n"

    with open(README_PATH,"w",encoding="utf-8") as f:
        f.write(new_readme)

def main():
    # Defensive: ensure borp exists
    try:
        _ = run(["borp","--help"])
    except SystemExit:
        print("ERROR: borp CLI not found. Install with: pip install bor-sdk==1.0.0")
        raise

    HMASTER_ref, HMASTER_mod = gen_bundles()
    flips, pct = render_figure(HMASTER_ref, HMASTER_mod, IMG_PATH)
    update_readme(HMASTER_ref, HMASTER_mod, flips, pct)

    print("\n=== Avalanche assets updated ===")
    print(f"Image : {IMG_PATH}")
    print(f"README: section between markers updated")
    print(f"Flips : {flips}/256 ({pct:.2f}%)")

if __name__ == "__main__":
    main()

