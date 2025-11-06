# BoR-Proof SDK — Public, Replay-Verifiable Reasoning

The BoR-Proof SDK extends the Blockchain of Reasoning (BoR) framework into a verifiable proof system for computational reasoning.  
Each logical or mathematical computation becomes a cryptographic event whose integrity can be independently verified.  
This SDK enables developers and researchers to generate, verify, and replay proofs of reasoning across time, platforms, and participants — ensuring trust without central authority.

## What You Get

P₀ Init proof (env + inputs)  
P₁ Step proofs (per-step fingerprints)  
P₂ Master proof (HMASTER)  
P₃ Deterministic replay verify  
P₄ Persistence integrity (H_store)  

8 Sub-Proofs: DIP, DP, PEP, PoPI, CCP, CMIP, PP, TRP  
Bundle: rich_proof_bundle.json + rich_proof_index.json  
CLI: borp prove, borp verify, borp verify-bundle, borp persist, borp show

## Installation

```bash
git clone https://github.com/kushagrab21/BoR-proof-SDK.git
cd BoR-proof-SDK
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
borp --help
```

## Quickstart (5 Commands)

```bash
# 1. Generate a proof bundle (uses example stages)
borp prove --all \
  --initial '7' \
  --config '{"offset": 4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out

# 2. Verify bundle fast (structure + digests)
borp verify-bundle --bundle out/rich_proof_bundle.json

# 3. Strong verify — includes replay
borp verify-bundle --bundle out/rich_proof_bundle.json \
  --initial '7' --config '{"offset":4}' --version 'v1.0' \
  --stages examples.demo:add examples.demo:square

# 4. Human-readable trace
borp show --trace out/rich_proof_bundle.json --from bundle
```

## Example Output

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

## Artifact Anatomy

primary.master = HMASTER (chain identity)  
subproofs/* → each hashed, collected into H_RICH  
rich_proof_index.json = minimal {H_RICH, subproof_hashes}  
*.json.p4.json (sidecar) stores H_store + timestamp

## Tests

```bash
pytest -q    # 88/88 passing
```

## Determinism & Purity

All steps are pure functions f(state, C, V) -> state'.  
Encoding is canonical JSON (sorted keys, fixed float print, UTF-8).

## Proof Chain

| Proof | Description | Output |
|-------|-------------|--------|
| P₀ | Initialization | H(S₀, C, V, env) → H0 |
| P₁ | Step-level | h₁, h₂, ..., hₙ |
| P₂ | Master aggregation | HMASTER = H("P2\|h₁\|...\|hₙ") |
| P₃ | Verification | Replay + compare HMASTER |
| P₄ | Persistence | H_store = H(bytes \|\| timestamp) |

### Sub-proofs (8 total)

| Sub-proof | Validates |
|-----------|-----------|
| DIP | Deterministic Identity: identical runs → same HMASTER |
| DP | Divergence: perturbation → different HMASTER |
| PEP | Purity Enforcement: @step rejects invalid signatures |
| PoPI | Proof-of-Proof Integrity: SHA-256(primary JSON) |
| CCP | Canonicalization Consistency: dict order invariance |
| CMIP | Cross-Module Integrity: core/verify/store agree |
| PP | Persistence: JSON + SQLite H_store equivalence |
| TRP | Temporal Reproducibility: time-invariant HMASTER |

H_RICH = SHA-256 of sorted concatenation of all sub-proof hashes.

## Proof Validation Matrix

| Command | Proof Layer | Guarantees |
|---------|-------------|------------|
| `borp prove --all` | P₀–P₄ + sub-proofs | Deterministic proof generation |
| `borp verify-bundle` | P₃ | Proof integrity (structure + digests) |
| `borp verify-bundle ... --stages` | P₃ | Full replay verification |
| `borp persist` | P₄ | Persistence integrity (H_store) |
| `borp show --trace` | — | Human-readable reasoning chain |

## Troubleshooting

**Error: `ModuleNotFoundError: No module named 'bor'`**  
The system PATH is pointing to another Python environment.  
Run the command from your virtual environment explicitly:

```bash
.venv/bin/borp --help
```

**CLI command not found**  
Ensure you ran `pip install -e .` inside an activated virtual environment.

## Independent Verification Checklist

1. Clone the repository and install.
2. Run `pytest -q` — expect **88/88 tests passing**.
3. Execute the Quickstart commands exactly as shown.
4. Confirm `[BoR RICH] VERIFIED` appears in terminal.
5. (Optional) Inspect `out/rich_proof_bundle.json` manually and validate hashes.

## Citation

If you use BoR-Proof SDK in research or publications:

```bibtex
@software{kushagra_bor_proof_sdk,
  author = {Kushagra Bhatnagar},
  title  = {BoR-Proof SDK: Deterministic, Replay-Verifiable Proof System},
  year   = {2025},
  url    = {https://github.com/kushagrab21/BoR-proof-SDK}
}
```

## Architecture Overview

```
bor/
├── core.py          # BoRRun, BoRStep, Proof (P₀-P₂)
├── decorators.py    # @step with purity enforcement (P₁)
├── hash_utils.py    # Canonical encoding + env fingerprint (P₀)
├── store.py         # JSON/SQLite persistence (P₄)
├── verify.py        # Replay, verification, bundle check, trace (P₃)
├── subproofs.py     # All 8 sub-proofs (DIP→TRP)
├── bundle.py        # Bundle builder + index
└── cli.py           # Complete CLI interface

examples/
└── demo.py          # Simple demonstration stages

tests/
├── test_p0_init.py
├── test_p1_steps.py
├── test_p2_master.py
├── test_p3_verify.py
├── test_p4_persistence.py
├── test_e_subproofs_bundle.py
├── test_e2_remaining_subproofs.py
└── test_f_bundle_verify_and_trace.py
```

## License

MIT License
