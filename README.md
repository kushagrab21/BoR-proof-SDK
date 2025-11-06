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
