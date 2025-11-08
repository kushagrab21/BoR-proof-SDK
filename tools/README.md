# Tools Directory

This directory contains utility scripts for maintaining the BoR-Proof SDK documentation and assets.

## update_avalanche_assets.py

**Purpose:** Idempotently generate/update the avalanche verification figure and README section.

**What it does:**
1. Generates two proof bundles (official and modified logic)
2. Computes bitwise XOR difference between HMASTER hashes
3. Creates visualization: `docs/avalanche_bitdiff_report.png`
4. Updates README.md section between `<!-- AVA_SECTION_START -->` and `<!-- AVA_SECTION_END -->` markers

**Usage:**

```bash
# Direct invocation
python tools/update_avalanche_assets.py

# Via Makefile
make avalanche-verify
```

**Idempotency:**
- If image exists → overwrites it
- If README section exists → replaces it
- If neither exists → creates them
- Safe to run multiple times without duplication

**Requirements:**
- bor-sdk installed (borp CLI available)
- matplotlib, numpy
- Python ≥3.9

**Output:**
- Image: `docs/avalanche_bitdiff_report.png` (67KB, 4-panel visualization)
- README: Section appended/updated at end of file
- Console: Reports flip statistics (e.g., 117/256 bits = 45.70%)

**Example Output:**

```
=== Avalanche assets updated ===
Image : docs/avalanche_bitdiff_report.png
README: section between markers updated
Flips : 117/256 (45.70%)
```

---

## How the Avalanche Verification Works

**Official Logic:**
```python
def add(x, C, V):
    return x + C['offset']
```

**Modified Logic (single-line change):**
```python
def add(x, C, V):
    return x + C['offset'] + 1  # ← Added +1
```

**Inputs:** Both use `S₀=7`, `C={"offset":4}`, `V="v1.0"`

**Result:**
- Official: `7 + 4 = 11` → HMASTER = `dde71a3e...`
- Modified: `7 + 4 + 1 = 12` → HMASTER = `14b8903f...`
- **Bitwise flips: 117/256 (45.70%)** — demonstrates cryptographic avalanche property

This proves that even a single-line logic change causes massive hash divergence, making tampering immediately detectable.

---

## Maintenance

Run this script after:
- SDK version updates
- Changes to core proof logic
- Updates to demo examples
- Before publishing releases

The script is designed to be run frequently without side effects.

