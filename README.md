# BoR-Proof SDK — Deterministic, Replay-Verifiable Proof of Reasoning

The **BoR-Proof SDK** extends the Blockchain of Reasoning (BoR) framework into a system that turns every computation into a verifiable proof.  
Each reasoning step, configuration, and output is encoded deterministically so that the entire process can be **replayed and verified by anyone**.  
The SDK provides a command-line interface (CLI) and Python API for generating and checking these proofs.

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
