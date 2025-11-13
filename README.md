# BoR-Proof SDK — Deterministic, Replay-Verifiable Proof of Reasoning

The **BoR-Proof SDK** extends the Blockchain of Reasoning (BoR) framework into a system that turns every computation into a verifiable proof.  
Each reasoning step, configuration, and output is encoded deterministically so that the entire process can be **replayed and verified by anyone**.  
The SDK provides a command-line interface (CLI) and Python API for generating and checking these proofs.

---

## Introduction: Why We Built the Blockchain of Reasoning

### Understanding the Core Idea

The **Blockchain of Reasoning (BoR)** makes reasoning verifiable.

Modern systems can store and track data reliably, but the logic that processes that data remains a black box.  
BoR changes this by turning every computational step — in an accounting workflow, an AI pipeline, or a data transformation — into a deterministic, replayable proof.

- If a workflow is re-run with the same inputs, it produces the exact same result, bit-for-bit.
- If anything changes, the proof diverges immediately.

This shifts trust from **who computed something** to **what was computed**.

### What BoR Enables

BoR represents any process as a sequence of canonical reasoning steps:

1. Define the inputs
2. Apply a pure transformation
3. Capture the output
4. Hash it
5. Link it to the next step
6. Produce a single proof-fingerprint representing the entire workflow

This fingerprint can be verified across machines, environments, or time without relying on the original system.

Workflows that previously hid their logic now produce provable trails:

- financial reconciliation
- audit and compliance checks
- AI reasoning pipelines
- data transformation and cleaning steps

**Opaque logic becomes provable logic.**

### Why This Matters Now

Automation is accelerating, but verifiability is not.

Today's systems:

- verify data, not the logic behind it
- generate outputs, but not proofs
- flag changes, but not correctness
- automate workflows without exposing why decisions were made

With AI adoption, governance requirements, and automation complexity rising, systems need a way to prove their reasoning.

BoR provides that foundation: **deterministic, inspectable logic that can be trusted, replayed, and certified.**

### Key Advantages

#### Verifiability as a foundation for scale

Systems that can be proven correct scale more safely.  
BoR treats verification as a core building block rather than an afterthought.

#### A structured memory for reasoning

Once each step has a proof identity:

- reasoning trails can be stored, forked, merged, or reused
- long workflows retain their causal structure
- context becomes an explicit artifact, not an implicit side effect

This is the missing substrate for scalable, long-horizon reasoning.

#### A practical toolkit for deterministic logic

BoR functions like a combination of:

- **Git** (for tracking and branching logic)
- **a deterministic compiler** (for reproducible execution)
- **a blockchain** (for immutable linkage)

This creates a reusable base layer for building reliable reasoning systems.

#### Human–machine collaborative reasoning

Because each step is pure, inspectable, and replayable, humans and AI systems can safely co-develop reasoning trails.

#### A path toward trustworthy AI

BoR does not replace AI — it surrounds it with verifiability, ensuring that:

- deterministic parts remain provable
- AI-generated steps are sandboxed
- decisions can be replayed
- drift becomes detectable

This turns black-box pipelines into auditable systems.

### What This Unlocks

#### 1. Proof APIs for enterprise workflows

Reconciliation, compliance, ETL, fraud detection, and more can be verified with a single API call.

#### 2. Version control for reasoning

A shared environment where humans and machines can:

- build
- fork
- merge
- verify

entire reasoning trails.

#### 3. A general reasoning substrate

BoR establishes primitives for:

- context-aware systems
- long-horizon AI agents
- reusable logic modules
- audit-ready processing pipelines
- deterministic AI governance

#### 4. A new invariant: reasoning identity

Similar to how blockchain introduced transaction identity, BoR introduces:

- **reasoning identity** — a hash of logic
- **proof-of-reasoning** — a replayable audit trail
- **temporal invariance** — the guarantee that logic does not drift

This is the base layer automation and AI have been missing.

### Summary

BoR makes reasoning verifiable by converting each step into a deterministic, cryptographically provable unit of logic.  
It enables scalable automation, structured reasoning memory, human–AI collaborative logic, trustworthy AI workflows, and a new way to certify how systems think.

**It shifts computing from opaque execution to provable reasoning, allowing systems to not just run — but prove why they are correct.**

---

### 🧭 Run Instantly (Google Colab, Jupyter, or Any Python Environment)

You can try **BoR-Proof SDK** instantly — no setup or cloning required.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/#create=true)

```python
# BoR-Proof SDK Quickstart (Colab / Jupyter)

# 1. Install from PyPI
!pip install -q bor-sdk

# 2. Check CLI help
!borp --help

# 3. Generate and verify a deterministic proof
!borp prove --all \
  --initial '7' \
  --config '{"offset": 4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out

# 4. Verify proof bundle (structural check)
!borp verify-bundle --bundle out/rich_proof_bundle.json

# 5. (Optional) Register proof node for consensus
!borp register-hash --user "colab-user" --label "demo-node"

# 6. Inspect the proof registry file
!cat proof_registry.json
```

**For terminal/bash environments:**

```bash
pip install bor-sdk
borp --help

# Example: Generate and verify a deterministic proof
borp prove --all \
  --initial '7' \
  --config '{"offset":4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out

borp verify-bundle --bundle out/rich_proof_bundle.json
```

✅ Works seamlessly on **Google Colab**, **Jupyter Notebook**, **VS Code**, or any terminal with Python ≥ 3.9.  
This demonstrates BoR-Proof's **environment-independent determinism** — identical inputs always yield identical proof hashes (`HMASTER`, `HRICH`).

---

## 1. Overview: The Proof Chain

Every reasoning run is represented as a 5-layer proof stack:

| Layer | Purpose | Conceptual Guarantee |
|-------|----------|---------------------|
| **P₀ — Initialization** | Hashes the environment and inputs | Same inputs → same start hash |
| **P₁ — Step Proofs** | Hashes each reasoning step `(f, S, C, V)` | Each step leaves a traceable fingerprint |
| **P₂ — Master Proof** | Aggregates all step hashes | Defines the identity of the reasoning chain (`HMASTER`) |
| **P₃ — Verification** | Replays and compares results | Proves reproducibility across time and machines |
| **P₄ — Persistence** | Hashes stored proof files | Detects any tampering in saved data (`H_store`) |

Together they form a cryptographically closed reasoning ledger.

---

## 2. Sub-Proofs (System-Level Validations)

Eight higher-order sub-proofs check that the system behaves as it should:

| ID | Proof Name | Validates |
|----|-------------|-----------|
| DIP | Deterministic Identity | identical runs → identical `HMASTER` |
| DP | Divergence | perturbations → different `HMASTER` |
| PEP | Purity Enforcement | impure functions rejected by `@step` |
| PoPI | Proof-of-Proof Integrity | SHA-256 hash of primary proof JSON |
| CCP | Canonicalization Consistency | dict/key order does not change hashes |
| CMIP | Cross-Module Integrity | core, verify, and store agree on results |
| PP | Persistence | JSON and SQLite stores produce identical `HMASTER` |
| TRP | Temporal Reproducibility | proofs stable across time delays |

The hashes of these eight sub-proofs are concatenated and re-hashed to produce **H_RICH**, the single commitment for the entire run.

---

## 3. Installation

### Quick Install (Recommended)

```bash
pip install bor-sdk
borp --help
```

### Developer Install (for Contributors)

```bash
git clone https://github.com/kushagrab21/BoR-proof-SDK.git
cd BoR-proof-SDK
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
borp --help
```

---

## 4. Generating and Verifying Proofs (from First Principles)

### 4.1 Generate a Proof (P₀–P₄ + Sub-Proofs)

Each command below corresponds directly to one logical assertion:

```bash
borp prove --all \
  --initial '7' \                   # S₀ (initial state)
  --config '{"offset": 4}' \         # C (configuration)
  --version 'v1.0' \                 # V (version string)
  --stages examples.demo:add examples.demo:square \
  --outdir out
```

This command:

1. Canonicalizes inputs (P₀)
2. Runs each step deterministically (P₁)
3. Aggregates fingerprints into `HMASTER` (P₂)
4. Executes all sub-proofs (DIP→TRP)
5. Produces the Rich Proof Bundle (`out/rich_proof_bundle.json`)

---

### 4.2 Verify a Proof (Fast Structural Check)

Checks the cryptographic integrity of the bundle without replaying computations:

```bash
borp verify-bundle --bundle out/rich_proof_bundle.json
```

This recomputes sub-proof hashes and verifies that the stored `H_RICH` matches the recomputed value.

---

### 4.3 Verify with Replay (Strong Check)

Fully re-executes the reasoning steps and recomputes `HMASTER`:

```bash
borp verify-bundle --bundle out/rich_proof_bundle.json \
  --initial '7' --config '{"offset":4}' --version 'v1.0' \
  --stages examples.demo:add examples.demo:square
```

If the recomputed `HMASTER` equals the stored value, the reasoning process is proven identical.

---

### 4.4 Show the Proof Trace

Displays the reasoning sequence in plain text:

```bash
borp show --trace out/rich_proof_bundle.json --from bundle
```

Each line shows function, input, output, and hash — allowing step-by-step auditability.

---

### 4.5 Persist Proofs (P₄ Storage Integrity)

Stores and audits proofs across JSON and SQLite backends:

```bash
borp persist --label demo --primary out/primary.json --backend both
```

This ensures that saved proofs can later be checked for tampering using their `H_store` hashes.

---

## 5. Example Output

```
[BoR P₀] Initialization Proof Hash = ...
[BoR P₁] Step #1 'add' → hᵢ = ...
[BoR P₂] HMASTER = ...
[BoR RICH] Bundle created
{
  "H_RICH": "e9ac1524f4a318a3..."
}
[BoR RICH] VERIFIED
{
  "ok": true,
  "checks": {"H_RICH_match": true, "subproof_hashes_match": true}
}
```

---

## 6. Proof Validation Matrix

| Command | Proof Layer | Guarantee |
|---------|-------------|-----------|
| `borp prove --all` | P₀–P₄ + sub-proofs | Generates deterministic, verifiable reasoning chain |
| `borp verify-bundle` | P₃ | Validates proof structure and digest integrity |
| `borp verify-bundle ... --stages` | P₃ (Replay) | Confirms computational equivalence of reasoning |
| `borp persist` | P₄ | Confirms stored proof authenticity |
| `borp show --trace` | — | Renders human-readable logical sequence |

---

## 7. Troubleshooting

**Error:** `ModuleNotFoundError: No module named 'bor'`  
→ The global Python PATH is being used. Run CLI via the virtual environment:

```bash
.venv/bin/borp --help
```

**CLI command not found**  
→ Ensure you installed the SDK in editable mode within an activated environment:

```bash
pip install -e .
```

> **Note on Anaconda/venv conflicts**  
> If you see `ModuleNotFoundError: No module named 'bor'`, your shell is using Anaconda's global Python.
>
> **Fix:**
> ```bash
> conda deactivate
> source .venv/bin/activate
> pip install -e .
> which borp  # should point inside .venv/bin/
> ```
> Always run `borp` from the virtual environment, or call
> ```bash
> python -m bor.cli --help
> ```
> to guarantee correct imports.

---

## 8. Independent Verification Checklist

1. Clone the repository and install dependencies.
2. Run `pytest -q` → expect all 88 tests to pass.
3. Execute the Quickstart commands.
4. Observe `[BoR RICH] VERIFIED`.
5. Optionally, recompute SHA-256 of the proof JSON to confirm immutability.

---

## 9. Citation

```bibtex
@software{kushagra_bor_proof_sdk,
  author = {Kushagra Bhatnagar},
  title  = {BoR-Proof SDK: Deterministic, Replay-Verifiable Proof System},
  year   = {2025},
  url    = {https://github.com/kushagrab21/BoR-proof-SDK}
}
```

---

## 10. Architecture

```
bor/
├── core.py          # Proof engine (P₀–P₂)
├── decorators.py    # @step purity contract (P₁)
├── hash_utils.py    # Canonical encoding + environment hash (P₀)
├── store.py         # Persistence proofs (P₄)
├── verify.py        # Replay + bundle verification (P₃)
├── subproofs.py     # DIP→TRP system checks
├── bundle.py        # Bundle builder and index generator
└── cli.py           # Unified CLI interface

examples/
└── demo.py          # Demonstration stages
```

---

## 11. License

MIT License  
© 2025 Kushagra Bhatnagar. All rights reserved.

---

## 12. Understanding the Results: A First-Principled Explanation

### 12.1 How to Read the Verification Output

When you run any BoR-Proof command, every line corresponds to a layer in the logical proof ledger:

In BoR-Proof, **a reasoning chain is a closed deterministic system whose behavior is fully captured by its cryptographic invariants**.

| Output Prefix | Proof Layer | Interpretation |
|---------------|-------------|----------------|
| `[BoR P₀]` | Initialization | System has canonicalized and hashed `(S₀, C, V, env)` → establishes the starting fingerprint |
| `[BoR P₁]` | Step Proofs | Each reasoning function `fᵢ(Sᵢ₋₁, C, V)` executed deterministically; its input and output were hashed → produces `hᵢ` |
| `[BoR P₂]` | Master Proof | All step fingerprints concatenated and hashed → defines the unique chain identity `HMASTER` |
| `[BoR P₃]` | Verification | System recomputed `HMASTER'` and compared to stored value → confirms reproducibility |
| `[BoR P₄]` | Persistence | Proof stored in canonical JSON and SQLite forms; file integrity hashes `H_store` computed |
| `[BoR RICH]` | Sub-Proof Integrity | Eight higher-order sub-proofs re-hashed to form `HRICH`, the single immutable commitment for the entire reasoning run |

If you see `[BoR RICH] VERIFIED`, it means **every hash, sub-proof, and master digest matched**.  

This is equivalent to a mathematical proof of identity:

```
HMASTER' = HMASTER  and  HRICH' = HRICH
```

---

### 12.2 Why These Results Hold Mathematically

BoR-Proof relies on three foundational axioms of deterministic computation:

**1. Referential Transparency**

Each function `f(S, C, V)` always produces the same output given the same input—no randomness, no hidden state.

```
f(S, C, V) = S'  ⇒  H(f, S, C, V) is constant
```

**2. Cryptographic Hash Collision Resistance**

The probability that two different inputs produce the same hash is negligible (≈ 2⁻²⁵⁶ for SHA-256).  
Thus if two proofs have identical hashes, they are indistinguishable at the bit level.

```
H(x) = H(y)  ⇒  x = y  (with overwhelming probability)
```

**3. Deterministic Composition**

The master proof is built by hashing hashes in sequence:

```
HMASTER = H(h₁ || h₂ || ... || hₙ)
```

Any change in any step (even one bit) alters the aggregate hash entirely.  
Hence reproducibility is equivalent to equality of master hashes.

**Result:** When the replayed chain recomputes the same `HMASTER` and all sub-proofs match their stored values, the reasoning process is **mathematically guaranteed to be identical** to the original.

---

### 12.3 Conceptual Model: Proof as a Chain of Invariants

```
                    Inputs (S₀, C, V)
                           │
                           ▼
                ┌──────────────────────┐
                │  Canonical Encoder   │ ──→ H₀
                │        (P₀)          │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Deterministic Steps │ ──→ h₁, h₂, ..., hₙ
                │        (P₁)          │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │     Aggregator       │ ──→ HMASTER
                │        (P₂)          │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Verification Replay  │ ──→ HMASTER'
                │        (P₃)          │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Persistence / Audit  │ ──→ H_store
                │        (P₄)          │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │     Sub-Proofs       │ ──→ HRICH
                │      DIP→TRP         │
                └──────────────────────┘
```

**Figure 1:** Logical flow from inputs to HRICH.

Every arrow represents a **deterministic and hash-preserving transformation**.  
Therefore, identical arrows (executions) always produce identical end-states.

---

### 12.4 Mathematical Summary

| Property | Formal Statement | Consequence |
|----------|------------------|-------------|
| **Determinism** | `f(S, C, V) = S'` is pure | Repeatable computation |
| **Canonicalization** | JSON sorted, fixed precision | Platform-independent results |
| **Hash Integrity** | `H(x) = SHA256(x)` | Bit-level tamper detection |
| **Chain Aggregation** | `HMASTER = H(h₁ ‖ ... ‖ hₙ)` | Global reasoning identity |
| **Rich Proof Integrity** | `HRICH = H(H(DIP), ..., H(TRP))` | Compound integrity across all meta-proofs |

**Conclusion:** Proof validity is grounded in mathematics, not authority.  
Verification is a direct comparison between observed and expected invariants — a **proof of equality** rather than an **assertion of trust**.

---

### 12.5 Interpreting a Verified Proof (Example)

```
[BoR P₂] HMASTER = dde71a3e4391...
[BoR RICH] VERIFIED
{
  "checks": {
    "H_RICH_match": true,
    "primary_master_replay_match": true,
    "subproof_hashes_match": true
  },
  "ok": true
}
```

**Interpretation:**

- `HMASTER` identifies the reasoning chain uniquely
- Matching `primary_master_replay_match` proves that the reasoning logic can be replayed exactly
- `HRICH_match` ensures every sub-proof (DIP→TRP) agrees with stored commitments
- Together, they constitute **a cryptographic certificate of logical identity**

---

### 12.6 Why Integrity Matters Beyond Code

**1. Scientific Reproducibility**

Any researcher can rerun the reasoning and obtain identical hashes, establishing *proof of scientific consistency*.

**2. Auditable AI and Computation**

Decisions and outputs become verifiable artifacts, preventing silent alteration or drift.

**3. Legal and Regulatory Trust**

A signed proof ledger acts as immutable evidence of computation, admissible without third-party validation.

**4. Philosophical Shift**

Trust migrates from *who* computed to *what* was computed — a move from belief to verifiable knowledge.

---

### 12.7 In Essence

BoR-Proof SDK establishes a new baseline for reasoning integrity:

> **Correctness = Equality of Hashes**  
> **Trust = Deterministic Reproducibility**

Every `[VERIFIED]` message you see is not a subjective approval — it is a **mathematical identity proof** between two complete reasoning universes.

---

### 12.8 Where Function Details Live

Each reasoning function used in a BoR-Proof run (for example `examples.demo:add` and `examples.demo:square`) is **automatically embedded inside the proof artifact itself**.

During execution, each step records:

```json
{
  "fn": "add",
  "input": 7,
  "output": 11,
  "config": {"offset": 4},
  "version": "v1.0",
  "fingerprint": "ac971c1ddacb80d4c117bc4..."
}
```

When verification occurs, these same functions are **re-imported and re-executed** to recompute identical fingerprints.  
If `HMASTER` remains unchanged, that means — by mathematical necessity — **the same functions produced the same outputs**.

**Therefore:**

- The **README** defines the logical framework
- The **proof bundle** contains the function-level evidence

---

## 12.9 Quickstart for New Nodes

If you only want to reproduce the official proof and register your node, you can do it in two commands.

**Option A: Using pip (fastest)**

```bash
pip install bor-sdk

# Clone repo for examples
git clone https://github.com/kushagrab21/BoR-proof-SDK.git
cd BoR-proof-SDK

borp prove --all \
  --initial '7' \
  --config '{"offset":4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out

borp register-hash --user "<your-github-handle>" --label "demo-node"
```

**Option B: From source (for contributors)**

```bash
git clone https://github.com/kushagrab21/BoR-proof-SDK.git
cd BoR-proof-SDK
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

borp prove --all \
  --initial '7' \
  --config '{"offset":4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out

borp register-hash --user "<your-github-handle>" --label "demo-node"
```

Check the file `proof_registry.json`; it now contains your node entry.
Then submit it via pull request or GitHub issue (see Step 2 submission details).
Average time ≈ 60 seconds.

---

> **Note:** Future versions of BoR-Proof will extend this into a full deterministic reasoning compiler, where each reasoning step is not only hashed but also represented as a canonical intermediate form, allowing reasoning graphs to be recompiled, diffed, and verified like code.

---

## 12.10 Avalanche Verification Experiment

The **avalanche effect** is a fundamental property of cryptographic hash functions: even a tiny change in input should cause approximately 50% of the output bits to flip. This experiment demonstrates that BoR-Proof SDK exhibits this property — a single-line logic change causes massive cryptographic divergence in `HMASTER`.

### Purpose

This experiment proves that:
1. **Small logic changes** (e.g., adding `+1` to a function) produce **completely different** master hashes
2. The divergence is **cryptographic** — approximately 50% bit flips (avalanche property)
3. BoR-Proof SDK correctly detects and quantifies reasoning divergence

### Copy-Paste Ready Code (Google Colab)

Copy this entire cell into Google Colab to reproduce the avalanche effect demonstration independently:

```python
# ==========================================================
# ⚡ BoR-Proof SDK — Avalanche Verification Experiment (Colab)
# ==========================================================
# Copy-paste this entire cell into Google Colab to reproduce
# the avalanche effect demonstration independently.
# ==========================================================

# Install dependencies
!pip install -q bor-sdk==1.0.0 matplotlib numpy

import json, hashlib, numpy as np, matplotlib.pyplot as plt

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
```

### What This Demonstrates

1. **Official Proof**: Runs the standard `examples.demo:add` function with `offset=4`
2. **Modified Proof**: Creates `demo_modified.py` with a single-line change (`+1` added)
3. **Bitwise Analysis**: Computes Hamming distance between the two `HMASTER` hashes
4. **Visualization**: Shows side-by-side comparison of hash bits (16×16 grids)
5. **Avalanche Confirmation**: Verifies that ~50% of bits flipped

### Expected Results

- **Bit Flip Percentage**: Approximately **50%** (128/256 bits)
- **Visual Output**: Three heatmaps showing:
  - Left: Official `HMASTER` (green)
  - Center: Bit flips (red) — should show widespread divergence
  - Right: Modified `HMASTER` (blue)
- **Conclusion**: ✅ Avalanche property confirmed

### Why This Matters

The avalanche effect proves that BoR-Proof SDK's cryptographic hashing is **cryptographically sound**:
- **Tiny logic changes** produce **completely different** proof identities
- **No silent failures** — any reasoning modification is immediately detectable
- **Mathematical guarantee** — hash collision resistance ensures uniqueness

This experiment provides **independent verification** that BoR-Proof SDK correctly implements cryptographic reasoning integrity.

---

## 13. Consensus Verification Protocol (v1.0)

**Establishing Public Consensus on Deterministic Reasoning Proofs**

### Step 0 — Purpose of Consensus

The BoR-Proof SDK already guarantees *local determinism*: identical inputs always yield identical proofs.  
This section extends that guarantee to *public consensus* — multiple independent verifiers reproducing the same proof hash (`HRICH`) and confirming it publicly.  
In short:

> **If multiple users obtain the same `HRICH`, the reasoning process itself has reached consensus.**

Consensus here is epistemic, not social — a collective proof that logic, not opinion, determines correctness.

---

### Step 1 — Overview (1-Minute Summary)

Adding your proof to the public consensus ledger takes **less than one minute**.

| Step | Action | Time |
|------|---------|------|
| 1 | Run `borp prove --all` to generate proof | 10 s |
| 2 | Run `borp register-hash` to record metadata | 1 s |
| 3 | Verify your `proof_registry.json` entry | 1 s |
| 4 | Submit via GitHub PR or issue | 30 s |
| 5 | Wait for 2+ identical hashes → consensus reached | passive |

That's all — **two commands, one file, under a minute**.

No networking protocols, blockchain mining, or complex configuration required.

---

### Step 2 — Run Your Node

#### **Prerequisites**

Ensure you have installed the SDK in a virtual environment:

```bash
git clone https://github.com/kushagrab21/BoR-proof-SDK.git
cd BoR-proof-SDK
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -e .
```

---

#### **Step 1 — Generate a Deterministic Proof**

Run the proof generation command with your chosen inputs:

```bash
borp prove --all \
  --initial '7' \
  --config '{"offset":4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out
```

**What this does:**
- Creates a complete proof bundle with `HMASTER` and `HRICH`
- Executes all 8 sub-proofs (DIP, DP, PEP, PoPI, CCP, CMIP, PP, TRP)
- Saves `out/rich_proof_bundle.json` and `out/rich_proof_index.json`

**Expected output (final lines):**

```
[BoR RICH] Bundle created
{
  "HRICH": "78ead3960f3d4fdfc9bd8acac7dd01b2a5b16c589f8bcdcacfc56a2fb0e985c7"
}
```

**Time:** ~10 seconds

---

#### **Step 2 — Register Your Consensus Node**

Automatically record your proof metadata:

```bash
borp register-hash \
  --user "your-github-handle" \
  --label "demo-quickstart"
```

**What this does:**
- Extracts `HRICH` from `out/rich_proof_bundle.json` automatically
- Detects your OS, Python version, timestamp
- Creates `proof_registry.json` with your entry

**Expected output:**

```
[BoR Consensus] Registered proof hash: 78ead3960f3d4fdf...
[BoR Consensus] Metadata written to proof_registry.json
[BoR Consensus] User: your-github-handle  |  OS: macOS-14.0-...  |  Python: 3.12.2
```

**Time:** ~1 second

---

#### **Step 3 — Verify Your Registry Entry**

Check the generated file:

```bash
cat proof_registry.json
```

**You should see:**

```json
[
  {
    "user": "your-github-handle",
    "timestamp": "2025-11-06T14:22:47.940056Z",
    "os": "macOS-14.0-x86_64-i386-64bit",
    "python": "3.12.2",
    "sdk_version": "v1.0",
    "label": "demo-quickstart",
    "hash": "78ead3960f3d4fdfc9bd8acac7dd01b2a5b16c589f8bcdcacfc56a2fb0e985c7"
  }
]
```

**Time:** ~1 second

---

#### **Step 4 — Submit to Public Registry**

You can contribute your consensus entry in two ways:

**Option A: Pull Request (Recommended)**

1. Fork the repository: https://github.com/kushagrab21/BoR-proof-SDK
2. Add your `proof_registry.json` entry to the repo's `proof_registry.json`
3. Create a pull request titled: `Consensus Submission – <your-handle>`

**Option B: GitHub Issue**

1. Create a new issue: https://github.com/kushagrab21/BoR-proof-SDK/issues
2. Title: `Consensus Submission – <your-handle>`
3. Paste the contents of your `proof_registry.json` file

**Time:** ~30 seconds

---

#### **Step 5 — Consensus Confirmation (Passive)**

Once **3 or more independent verifiers** produce the same `HRICH`, the consensus epoch is confirmed.

**You're done!** Your entry now acts as one *verifier node* in the reasoning consensus network.

**Total Active Time:** < 1 minute

---

### Step 3 — Understand the Genesis Block

The first verifier creates the *genesis entry*:

```json
[
  {
    "epoch": "2025-11-06",
    "hash": "e9ac1524f4a318a3...",
    "verifiers": ["kushagrab21"],
    "status": "GENESIS_PROOF"
  }
]
```

When two or more additional verifiers independently reproduce the same hash, the entry updates to:

```json
{
  "epoch": "2025-11-06",
  "hash": "e9ac1524f4a318a3...",
  "verifiers": ["kushagrab21", "alice-node", "bob-node"],
  "status": "CONSENSUS_CONFIRMED"
}
```

This marks the **first consensus epoch** — proof that reasoning reproducibility holds across machines and observers.

---

### Step 4 — Optional CLI Parameters

The `register-hash` command supports additional configuration:

```bash
borp register-hash \
  --bundle out/rich_proof_bundle.json \
  --registry custom_registry.json \
  --user "custom-username" \
  --label "my-experiment-v2"
```

**Options:**
- `--bundle`: Path to proof bundle (default: `out/rich_proof_bundle.json`)
- `--registry`: Registry file to create/append (default: `proof_registry.json`)
- `--user`: Override auto-detected username
- `--label`: Custom label for this proof (default: `unlabeled`)

**Multiple Entries:**

Run `register-hash` multiple times to append additional proof entries to the same registry. Each run adds one verifier node entry.

---

### Step 5 — What Your Proof Means

A verified consensus run means:

- Every participant's environment produced the same `HRICH`
- No hidden or nondeterministic variance exists
- Logical replayability has been independently validated

Mathematically:

```
HRICH(v₁) = HRICH(v₂) = ... = HRICH(vₙ)
  ⇒  Collective Proof of Reasoning Identity
```

Consensus, therefore, is **equality of invariants across observers** — extending blockchain's *data immutability* into *reasoning immutability*.

---

### 13.7 Summary Table

| Artifact | Role | Guarantee |
|----------|------|-----------|
| `rich_proof_bundle.json` | Local deterministic proof | Cryptographic identity |
| `proof_manifest.json` | Verifier metadata | Environment transparency |
| `proof_registry.json` | Public ledger of submissions | Cross-verifier equality |
| Consensus Epoch | ≥ 3 identical `HRICH` | Public reasoning consensus |

---

### 13.8 Closing Principle

BoR-Proof consensus transforms determinism into trust:

> **Correctness = Equality of Hashes**  
> **Trust = Equality across Observers**

When these equalities hold, reasoning itself has reached consensus — the first reproducible proof of logic as a shared invariant.

---

### 13.9 Common Pitfalls

| Issue | Symptom | Fix |
|-------|----------|-----|
| Wrong Python interpreter | `ModuleNotFoundError: No module named 'bor'` | Run inside `.venv` |
| Old `borp` on PATH | `which borp` → `/opt/anaconda3/bin/borp` | Reactivate venv or run `.venv/bin/borp` |
| No `proof_registry.json` created | Forgot `register-hash` step | Run `borp register-hash --label my-node` |
| Different H_RICH from others | Changed inputs/config | Use exact demo parameters |
