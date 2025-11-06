# BoR-Proof SDK — Deterministic, Replay-Verifiable Proof of Reasoning

The **BoR-Proof SDK** extends the Blockchain of Reasoning (BoR) framework into a system that turns every computation into a verifiable proof.  
Each reasoning step, configuration, and output is encoded deterministically so that the entire process can be **replayed and verified by anyone**.  
The SDK provides a command-line interface (CLI) and Python API for generating and checking these proofs.

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

```bash
git clone https://github.com/kushagrab21/BoR-proof-SDK.git
cd BoR-proof-SDK
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -e .
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

| Output Prefix | Proof Layer | Interpretation |
|---------------|-------------|----------------|
| `[BoR P₀]` | Initialization | System has canonicalized and hashed `(S₀, C, V, env)` → establishes the starting fingerprint |
| `[BoR P₁]` | Step Proofs | Each reasoning function `fᵢ(Sᵢ₋₁, C, V)` executed deterministically; its input and output were hashed → produces `hᵢ` |
| `[BoR P₂]` | Master Proof | All step fingerprints concatenated and hashed → defines the unique chain identity `HMASTER` |
| `[BoR P₃]` | Verification | System recomputed `HMASTER'` and compared to stored value → confirms reproducibility |
| `[BoR P₄]` | Persistence | Proof stored in canonical JSON and SQLite forms; file integrity hashes `H_store` computed |
| `[BoR RICH]` | Sub-Proof Integrity | Eight higher-order sub-proofs re-hashed to form `H_RICH`, the single immutable commitment for the entire reasoning run |

If you see `[BoR RICH] VERIFIED`, it means **every hash, sub-proof, and master digest matched**.  

This is equivalent to a mathematical proof of identity:

```
H_MASTER' = H_MASTER  and  H_RICH' = H_RICH
```

---

### 12.2 Why These Results Hold Mathematically

BoR-Proof relies on three foundational axioms of deterministic computation:

**1. Referential Transparency**

Each function `f(S, C, V)` always produces the same output given the same input—no randomness, no hidden state.

```
f(S, C, V) = S'  ⟹  H(f, S, C, V) is constant
```

**2. Cryptographic Hash Collision Resistance**

The probability that two different inputs produce the same hash is negligible (≈ 2⁻²⁵⁶ for SHA-256).  
Thus if two proofs have identical hashes, they are indistinguishable at the bit level.

```
H(x) = H(y)  ⟹  x = y  (with overwhelming probability)
```

**3. Deterministic Composition**

The master proof is built by hashing hashes in sequence:

```
H_MASTER = H(h₁ || h₂ || ... || hₙ)
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
│ Canonical Encoder    │  → H₀
│       (P₀)           │
└──────────┬───────────┘
           ▼
    Deterministic
       Steps (P₁)       → h₁, h₂, ...
           │
           ▼
      Aggregator        → H_MASTER
         (P₂)
           │
           ▼
    Verification        → H_MASTER'
    Replay (P₃)
           │
           ▼
    Persistence/        → H_store
    Audit (P₄)
           │
           ▼
    Sub-Proofs          → H_RICH
    DIP→TRP
```

Every arrow represents a **deterministic and hash-preserving transformation**.  
Therefore, identical arrows (executions) always produce identical end-states.

---

### 12.4 Mathematical Summary

| Property | Formal Statement | Consequence |
|----------|------------------|-------------|
| **Determinism** | `f(S, C, V) = S'` is pure | Repeatable computation |
| **Canonicalization** | JSON sorted, fixed precision | Platform-independent results |
| **Hash Integrity** | `H(x) = SHA256(x)` | Bit-level tamper detection |
| **Chain Aggregation** | `H_MASTER = H(h₁ ‖ ... ‖ hₙ)` | Global reasoning identity |
| **Rich Proof Integrity** | `H_RICH = H(H(DIP), ..., H(TRP))` | Compound integrity across all meta-proofs |

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
- `H_RICH_match` ensures every sub-proof (DIP→TRP) agrees with stored commitments
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
