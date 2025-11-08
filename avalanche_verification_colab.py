# ==========================================================
# ⚡ BoR-Proof SDK — Avalanche Verification Experiment (Colab)
# ==========================================================
# Copy-paste this entire cell into Google Colab to reproduce
# the avalanche effect demonstration independently.
# ==========================================================

# Install dependencies
!pip install -q bor-sdk==1.0.0 matplotlib numpy

import os, json, hashlib, numpy as np, matplotlib.pyplot as plt

# ----------------------------------------------------------
# 1️⃣  Run official proof
# ----------------------------------------------------------
print("=== 🧩 Running Official Proof ===")
!borp prove --all \
  --initial '7' \
  --config '{"offset":4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out_ref

ref = json.load(open("out_ref/rich_proof_bundle.json"))
HMASTER_ref = ref["primary"]["master"]
H_RICH_ref  = ref["H_RICH"]
print(f"HMASTER_ref = {HMASTER_ref}")
print(f"H_RICH_ref  = {H_RICH_ref}\n")

# ----------------------------------------------------------
# 2️⃣  Create modified logic (+1) and rerun
# ----------------------------------------------------------
print("=== ⚙️ Creating Modified Logic (+1) ===")

with open("demo_modified.py", "w") as f:
    f.write("""
from bor.decorators import step

@step
def add(x, C, V):
    return x + C["offset"] + 1  # logic mutation: adds +1

@step
def square(x, C, V):
    return x * x
""")

print("=== 🧩 Running Modified Proof ===")
# Set PYTHONPATH to include current directory so demo_modified can be imported
os.environ['PYTHONPATH'] = os.getcwd() + os.pathsep + os.environ.get('PYTHONPATH', '')

!borp prove --all \
  --initial '7' \
  --config '{"offset":4}' \
  --version 'v1.0' \
  --stages demo_modified:add demo_modified:square \
  --outdir out_mod

mod = json.load(open("out_mod/rich_proof_bundle.json"))
HMASTER_mod = mod["primary"]["master"]
H_RICH_mod  = mod["H_RICH"]
print(f"HMASTER_mod = {HMASTER_mod}")
print(f"H_RICH_mod  = {H_RICH_mod}\n")

# ----------------------------------------------------------
# 3️⃣  Bitwise analysis of divergence
# ----------------------------------------------------------
def bit_array(hex_hash):
    return np.array(list(bin(int(hex_hash,16))[2:].zfill(256))).astype(int)

ref_bits = bit_array(HMASTER_ref)
mod_bits = bit_array(HMASTER_mod)
xor_bits = (ref_bits != mod_bits).astype(int)

flips = xor_bits.sum()
pct = flips / 256 * 100
print(f"Bitwise Hamming Distance : {flips}/256 bits ({pct:.2f}% flipped)")

# ----------------------------------------------------------
# 4️⃣  Visualization (side-by-side)
# ----------------------------------------------------------
ref_grid = ref_bits.reshape(16,16)
mod_grid = mod_bits.reshape(16,16)
xor_grid = xor_bits.reshape(16,16)

fig, axs = plt.subplots(1, 3, figsize=(15,5))
axs[0].imshow(ref_grid, cmap="Greens", interpolation="nearest")
axs[0].set_title("Official HMASTER\n(examples.demo:add)", fontsize=10)
axs[1].imshow(xor_grid, cmap="Reds", interpolation="nearest")
axs[1].set_title(f"Bit Flips\n{flips}/256 bits ({pct:.2f}%)", fontsize=10)
axs[2].imshow(mod_grid, cmap="Blues", interpolation="nearest")
axs[2].set_title("Modified HMASTER\n(demo_modified:add +1)", fontsize=10)

for ax in axs: ax.axis("off")
plt.suptitle("⚡ Avalanche Verification — BoR-Proof SDK v1.0.0", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.show()

# ----------------------------------------------------------
# 5️⃣  Summary
# ----------------------------------------------------------
print("\n=== ⚡ Avalanche Divergence Report ===\n")
print(f"Official HMASTER : {HMASTER_ref}")
print(f"Modified HMASTER : {HMASTER_mod}")
print(f"Bitwise Hamming Distance : {flips}/256 bits ({pct:.2f}% flipped)\n")

if pct > 40:
    print("✅ Avalanche property confirmed — cryptographic divergence is massive.")
    print("   Even a single-line logic change (+1) causes ~50% bit flips in HMASTER.")
else:
    print("⚠️ Divergence below threshold, recheck configuration.")

