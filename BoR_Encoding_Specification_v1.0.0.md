# BoR-Proof SDK v1.0.0 — Complete Encoding Specification

**Document Version:** 1.0.0  
**SDK Version:** 1.0.0  
**Date:** 2025-11-08  
**Purpose:** Mathematical foundation ensuring provable identity across local, CI, and public consensus verification

---

## 📋 Executive Summary

This document enumerates **every deterministic encoding and hashing rule** used by the BoR-Proof SDK to compute proof identities across all layers (P₀–P₅) and sub-proofs (DIP→TRP). All rules are **code-verified** and extracted from the canonical implementation.

---

## 🔑 Core Canonicalization Functions

### 1. `canonical_bytes()` — Foundation Encoder

**Location:** `bor/hash_utils.py:32-50`

**Purpose:** Convert arbitrary Python objects to canonical JSON bytes

**Input:** Any Python object (dict, list, str, int, float, etc.)

**Canonicalization Rules:**
```python
# Float normalization: 12 digits precision
floats → Decimal(str(float)) → format(f".{12}g") → float

# JSON serialization
json.dumps(
    obj,
    sort_keys=True,           # Deterministic key ordering
    separators=(",", ":"),    # No whitespace
    ensure_ascii=False         # Support Unicode
).encode("utf-8")
```

**Output:** UTF-8 encoded bytes

**Hash Algorithm:** None (raw bytes)

**Code Snippet:**
```python
def canonical_bytes(obj) -> bytes:
    normalized = _normalize_floats(obj)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
```

---

### 2. `content_hash()` — Universal Hasher

**Location:** `bor/hash_utils.py:53-57`

**Purpose:** Compute SHA-256 hex digest of canonical bytes

**Input:** Any Python object

**Canonicalization:** Uses `canonical_bytes()`

**Hash Algorithm:** SHA-256

**Output:** Hex string (64 characters)

**Formula:**
```
H(obj) = SHA256(canonical_bytes(obj))
```

**Code Snippet:**
```python
def content_hash(obj) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()
```

---

## 🌍 Environment Fingerprinting

### 3. `env_fingerprint()` — Environment Capture

**Location:** `bor/hash_utils.py:60-72`

**Purpose:** Capture deterministic environment metadata for P₀

**Input:** Current system state

**Captured Fields:**
```python
{
    "python": sys.version.split()[0],     # Python version
    "os": platform.system(),              # OS name
    "arch": platform.machine(),           # Architecture
    "release": platform.release(),        # OS release
    "cwd": os.getcwd(),                   # Current directory
    "hashseed": os.environ.get("PYTHONHASHSEED", "not-set")
}
```

**Output:** Dict (not hashed)

**Note:** This dict is embedded in P₀ initialization proof and hashed via `content_hash()`

---

### 4. `capture_env_hash()` — Invariant Framework Environment

**Location:** `src/bor_core/env_utils.py:18-30`

**Purpose:** Hash environment for invariant tracking

**Input:** Current system state

**Captured Fields:**
```python
{
    "python": sys.version,                          # Full Python version
    "os": platform.platform(),                      # Full platform string
    "time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),   # UTC timestamp
    "bor_sdk": bor_version                          # BoR SDK version
}
```

**Hash Algorithm:** SHA-256

**Formula:**
```
H_env = SHA256(JSON.dumps(env, sort_keys=True).encode())
```

**Note:** **Contains timestamp** — this is for audit trails, not proof computation

---

## 🧩 Proof Layer Encodings

### Layer P₀: Initialization Proof

**Location:** `bor/core.py:84-88`

**Purpose:** Hash environment and inputs to establish starting fingerprint

**Input Dict:**
```python
{
    "S0": initial_state,
    "C": config,
    "V": version,
    "env": env_fingerprint()
}
```

**Hash Algorithm:** SHA-256 (via `content_hash()`)

**Formula:**
```
H₀ = SHA256(canonical_bytes({S0, C, V, env}))
```

**Code Snippet:**
```python
self.P0 = content_hash(
    {"S0": self.S0, "C": self.C, "V": self.V, "env": self.env}
)
```

**Domain Separator:** None

---

### Layer P₁: Step Proofs

**Location:** `bor/core.py:42-51`

**Purpose:** Hash each reasoning step to produce fingerprint hᵢ

**Input Dict:**
```python
{
    "fn": function_name,
    "input": input_state,
    "config": config,
    "version": version
}
```

**Hash Algorithm:** SHA-256 (via `content_hash()`)

**Formula:**
```
hᵢ = SHA256(canonical_bytes({fn, input, config, version}))
```

**Code Snippet:**
```python
def compute_fingerprint(self):
    payload = {
        "fn": self.fn_name,
        "input": self.input_state,
        "config": self.config,
        "version": self.code_version,
    }
    self.fingerprint = content_hash(payload)
```

**Note:** Output state is NOT included in fingerprint (only input)

---

### Layer P₂: Master Proof (HMASTER)

**Location:** `bor/core.py:146-150`

**Purpose:** Aggregate all step fingerprints into master identity

**Input:** List of step fingerprints `[h₁, h₂, ..., hₙ]`

**Aggregation Method:** **TEXT CONCATENATION**

**Domain Separator:** `"P2|"`

**Formula:**
```
concat = "P2|" + "|".join([h₁, h₂, ..., hₙ])
HMASTER = SHA256(canonical_bytes(concat))
```

**Expanded:**
```
concat = "P2|h₁|h₂|...|hₙ"
HMASTER = SHA256(JSON.dumps("P2|h₁|h₂|...|hₙ").encode())
```

**Code Snippet:**
```python
stage_hashes = self._stage_hashes()
concat = "P2|" + "|".join(stage_hashes)
HMASTER = content_hash(concat)
```

**Critical Details:**
- Uses **pipe `|` separator** between hashes
- Each hᵢ is a **hex string** (not binary)
- `content_hash()` wraps the string in JSON quotes: `"P2|h₁|h₂|..."`
- Final hash is SHA-256 of JSON-encoded concatenation

---

### Layer P₃: Verification (Replay)

**Location:** `bor/verify.py:59-69`

**Purpose:** Recompute HMASTER and compare with stored value

**Input:** Same as original run (S₀, C, V, stages)

**Method:** 
1. Rebuild `BoRRun` with identical inputs
2. Execute same stage functions
3. Call `finalize()` to recompute HMASTER
4. Compare: `stored_HMASTER == recomputed_HMASTER`

**Hash Algorithm:** Same as P₂

**Code Snippet:**
```python
def replay_master(S0, C, V, stage_fns):
    r = BoRRun(S0=S0, C=C, V=V)
    for fn in stage_fns:
        r.add_step(fn)
    proof = r.finalize()
    return proof.master
```

**Invariant Check:**
```python
stored_master = proof_obj["master"]
recomputed_master = replay_master(S0, C, V, stages)
ok = stored_master == recomputed_master
```

---

### Layer P₄: Persistence Proofs

#### P₄a: JSON Storage Hash

**Location:** `bor/store.py:49-74`

**Purpose:** Compute integrity hash for stored JSON proof

**Input:** 
1. Proof dict (already canonical)
2. Timestamp (UNIX seconds)

**Canonicalization:**
```python
data = json.dumps(
    proof,
    separators=(",", ":"),
    sort_keys=True
).encode("utf-8")
```

**Hash Algorithm:** SHA-256

**Formula:**
```
H_store_json = SHA256(proof_bytes || timestamp_bytes)
```

**Code Snippet:**
```python
data = json.dumps(proof, separators=(",", ":"), sort_keys=True).encode("utf-8")
ts = int(time.time())
h_store = hashlib.sha256(data + str(ts).encode("utf-8")).hexdigest()
```

**Note:** Timestamp is concatenated **as string** to the proof bytes

---

#### P₄b: SQLite Storage Hash

**Location:** `bor/store.py:107-153`

**Purpose:** Compute integrity hash for SQLite-persisted proof

**Input:**
1. Proof components (meta, steps, stage_hashes, master)
2. Timestamp (UNIX seconds)

**Canonicalization:**
```python
row_obj = {
    "label": label,
    "meta": json.loads(meta),
    "steps": json.loads(steps),
    "stage_hashes": json.loads(stage_hashes),
    "master": master
}
row_blob = json.dumps(
    row_obj,
    separators=(",", ":"),
    sort_keys=True
).encode("utf-8")
```

**Hash Algorithm:** SHA-256

**Formula:**
```
H_store_sqlite = SHA256(row_blob || timestamp_bytes)
```

**Code Snippet:**
```python
row_blob = json.dumps(row_obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
h_store = hashlib.sha256(row_blob + str(ts).encode("utf-8")).hexdigest()
```

---

### Layer P₅: Meta-Layer (Consensus & Self-Audit)

#### P₅a: Consensus Ledger

**Location:** `src/bor_consensus/ledger.py:12-15`

**Purpose:** Write consensus epochs with deterministic formatting

**Canonicalization:**
```python
json.dump(
    obj,
    f,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
)
```

**Hash Algorithm:** None (ledger is written, not hashed)

**Output Format:** Deterministic JSON file

**Note:** Epochs are sorted by status (CONFIRMED first) then by hash

---

#### P₅b: Self-Audit

**Location:** `src/bor_consensus/self_audit.py:30-41`

**Purpose:** Replay bundles to detect drift

**Method:** Calls `verify.verify_bundle_file()` which uses P₃ verification

**Hash Algorithm:** Reuses P₂ and P₃ algorithms

---

## 📊 Sub-Proof Encodings

### Sub-Proof Hash Function

**Location:** `bor/subproofs.py:28-31`

**Purpose:** Hash individual sub-proof results

**Canonicalization:**
```python
json.dumps(
    obj,
    separators=(",", ":"),
    sort_keys=True
).encode("utf-8")
```

**Hash Algorithm:** SHA-256

**Formula:**
```
H_sub = SHA256(JSON_minified(subproof_obj))
```

**Code Snippet:**
```python
def _sha256_minified_json(obj: Dict[str, Any]) -> str:
    b = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()
```

---

### Sub-Proof Identities

| Sub-Proof | Purpose | Input | Hash Method |
|-----------|---------|-------|-------------|
| **DIP** | Deterministic Identity | Two identical runs | `_sha256_minified_json({"ok": bool, "master_a": str, "master_b": str})` |
| **DP** | Divergence | Run with perturbation | `_sha256_minified_json({"diverged": bool, "master_a": str, "master_b": str, "perturb": dict})` |
| **PEP** | Purity Enforcement | Bad signature test | `_sha256_minified_json({"ok": bool, "exception": str})` |
| **PoPI** | Proof-of-Proof Integrity | Primary proof hash | `_sha256_minified_json({"proof_hash": str})` |
| **CCP** | Canonicalization | Key-order test | `_sha256_minified_json({"equal": bool, "master_a": str, "master_b": str})` |
| **CMIP** | Cross-Module Integrity | Core vs verify vs persist | `_sha256_minified_json({"equal": bool, "core": str, "verify": str, "json": str})` |
| **PP** | Persistence | JSON vs SQLite equality | `_sha256_minified_json({"equal": bool, "H_store_json": str, "H_store_sqlite": str, ...})` |
| **TRP** | Temporal Reproducibility | Run with delay | `_sha256_minified_json({"equal": bool, "master_t0": str, "master_t1": str})` |

---

### H_RICH: Rich Proof Commitment

**Location:** `bor/bundle.py:96-101`

**Purpose:** Single commitment over all sub-proof hashes

**Input:** Dict of sub-proof hashes `{subproof_name: hash_hex}`

**Aggregation Method:** **TEXT CONCATENATION** (pipe-separated)

**Formula:**
```
sorted_keys = sorted(sub_hashes.keys())
h_concat = "|".join([sub_hashes[k] for k in sorted_keys])
H_RICH = SHA256(h_concat.encode("utf-8"))
```

**Code Snippet:**
```python
sub_hashes = {k: h_sub(v) for k, v in subproofs.items()}
H_RICH = hashlib.sha256(
    "|".join([sub_hashes[k] for k in sorted(sub_hashes.keys())]).encode("utf-8")
).hexdigest()
```

**Order:** Alphabetically sorted sub-proof names: `CCP|CMIP|DIP|DP|PEP|PoPI|PP|TRP`

**Critical Details:**
- Uses **pipe `|` separator**
- Keys sorted **alphabetically**
- Direct UTF-8 encoding (no JSON wrapper)
- SHA-256 of raw concatenated string

---

## 🧪 Bundle Verification

**Location:** `bor/verify.py:154-200`

**Purpose:** Verify Rich Proof Bundle integrity

**Verification Steps:**

1. **Sub-proof hash recomputation:**
   ```python
   recomputed_hashes = {k: _sha256_minified(v) for k, v in subproofs.items()}
   ```

2. **H_RICH recomputation:**
   ```python
   h_concat = "|".join([recomputed_hashes[k] for k in sorted(recomputed_hashes.keys())])
   H_RICH_re = hashlib.sha256(h_concat.encode("utf-8")).hexdigest()
   ```

3. **Comparison:**
   ```python
   H_RICH == H_RICH_re
   ```

**Hash Algorithm:** SHA-256

**Code Snippet:**
```python
def _sha256_minified(obj: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
```

---

## 🛠️ Utility Functions

### `djson.dumps()` — Deterministic JSON Serializer

**Location:** `src/bor_utils/djson.py:10-15`

**Purpose:** Canonical JSON serialization for meta-layer

**Canonicalization:**
```python
json.dumps(
    obj,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
)
```

**Output:** JSON string (not hashed)

**Usage:** Consensus ledger, invariant state logging

---

### Registry Write Functions

**Location:** `src/bor_core/registry.py:21-24`

**Purpose:** Write state logs with deterministic formatting

**Canonicalization:**
```python
json.dump(
    data,
    f,
    indent=2,          # Readable formatting
    sort_keys=True
)
```

**Note:** Uses **indentation** (not minified) for human readability

---

## 📐 Encoding Hierarchy Table

| Layer / Proof | Function | Canonicalization Rule | Hash Algorithm | Domain Separator | Output |
|---------------|----------|----------------------|----------------|------------------|--------|
| **P₀ Init** | `content_hash()` | `json.dumps(sort_keys=True, separators=(",", ":"))` | SHA-256 | None | hex (64 chars) |
| **P₁ Step** | `content_hash()` | `json.dumps(sort_keys=True, separators=(",", ":"))` | SHA-256 | None | hex (64 chars) |
| **P₂ Master** | `content_hash(concat)` | `"P2\|" + "\|".join(stage_hashes)` → JSON | SHA-256 | `"P2\|"` | hex (64 chars) |
| **P₃ Replay** | Same as P₂ | Rerun pipeline | SHA-256 | `"P2\|"` | hex (64 chars) |
| **P₄a JSON** | `hashlib.sha256()` | Minified JSON + timestamp string | SHA-256 | None | hex (64 chars) |
| **P₄b SQLite** | `hashlib.sha256()` | Row object JSON + timestamp string | SHA-256 | None | hex (64 chars) |
| **P₅ Consensus** | None | Deterministic JSON write | None | N/A | JSON file |
| **P₅ Self-Audit** | Reuses P₃ | Bundle replay | SHA-256 | N/A | Report dict |
| **Sub-Proofs (DIP-TRP)** | `_sha256_minified_json()` | Minified JSON | SHA-256 | None | hex (64 chars) |
| **H_RICH** | `hashlib.sha256()` | `"\|".join(sorted_hashes)` (raw string) | SHA-256 | None | hex (64 chars) |
| **H_env (invariant)** | `hashlib.sha256()` | `json.dumps(sort_keys=True)` | SHA-256 | None | hex (64 chars) |

---

## 🔐 Hash Algorithm Summary

**All hashes use:** SHA-256

**Output format:** Hexadecimal (lowercase, 64 characters)

**Encoding:** UTF-8

---

## ⚠️ Non-Deterministic Sources

### Sanitized (Made Deterministic)

1. **Float precision:** Normalized to 12 digits via `_normalize_floats()`
2. **Dict key order:** Forced deterministic via `sort_keys=True`
3. **JSON whitespace:** Removed via `separators=(",", ":")`
4. **Environment variation:** Captured as part of P₀ hash

### Captured But Not Hashed Into Proofs

1. **Timestamps:** 
   - Used in `H_store` (P₄) but **not** in `HMASTER` (P₂)
   - Used in `capture_env_hash()` but **not** in `env_fingerprint()`
   - **Impact:** P₄ hashes vary by time, but P₂ (HMASTER) does not

2. **Current working directory:**
   - Captured in `env_fingerprint()` → affects P₀
   - **Impact:** Different directories → different P₀ → different proof chain

3. **PYTHONHASHSEED:**
   - Captured in `env_fingerprint()`
   - **Recommendation:** Set `PYTHONHASHSEED=0` for reproducibility

---

## 🧮 Mathematical Proof Equations

### Complete Proof Chain

```
Given:
  S₀ = initial state
  C = config
  V = version
  env = env_fingerprint()
  stages = [f₁, f₂, ..., fₙ]

Compute:

1. P₀ (Initialization):
   H₀ = SHA256(canonical_bytes({S₀, C, V, env}))

2. P₁ (Step Proofs):
   For i = 1 to n:
     Sᵢ = fᵢ(Sᵢ₋₁, C, V)
     hᵢ = SHA256(canonical_bytes({fn: fᵢ, input: Sᵢ₋₁, config: C, version: V}))

3. P₂ (Master Proof):
   concat = "P2|" + "|".join([h₁, h₂, ..., hₙ])
   HMASTER = SHA256(canonical_bytes(concat))

4. Sub-Proofs:
   For each subproof s ∈ {DIP, DP, PEP, PoPI, CCP, CMIP, PP, TRP}:
     result_s = run_s(S₀, C, V, stages)
     H_s = SHA256(JSON_minified(result_s))

5. H_RICH (Rich Proof):
   keys = sorted([DIP, DP, PEP, PoPI, CCP, CMIP, PP, TRP])
   concat_rich = "|".join([H_s for s in keys])
   H_RICH = SHA256(concat_rich.encode())

6. P₃ (Verification):
   HMASTER' = replay_master(S₀, C, V, stages)
   verified = (HMASTER == HMASTER')

7. P₄ (Persistence):
   proof_bytes = JSON_minified(proof)
   ts = unix_timestamp()
   H_store = SHA256(proof_bytes || str(ts))
```

---

## 🎯 Canonical Test Case

**Reproduce this exact HMASTER:**

```bash
borp prove --all \
  --initial '7' \
  --config '{"offset":4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out
```

**Expected Proof Chain:**

```
S₀ = 7
C = {"offset": 4}
V = "v1.0"

Step 1: add(7, C, V) → 11
  h₁ = SHA256(canonical_bytes({"fn": "add", "input": 7, "config": {"offset": 4}, "version": "v1.0"}))

Step 2: square(11, C, V) → 121
  h₂ = SHA256(canonical_bytes({"fn": "square", "input": 11, "config": {"offset": 4}, "version": "v1.0"}))

HMASTER = SHA256(canonical_bytes("P2|" + h₁ + "|" + h₂))
```

**To verify determinism:**

Run twice and assert: `HMASTER₁ == HMASTER₂`

---

## 📌 Key Invariants

1. **Referential Transparency:** `f(S, C, V) = S'` is pure
2. **Cryptographic Hash Collision Resistance:** SHA-256 provides ~2⁻²⁵⁶ collision probability
3. **Deterministic Composition:** `HMASTER = H(h₁ || h₂ || ... || hₙ)` is order-preserving
4. **Canonical Encoding:** `sort_keys=True` ensures dict order invariance
5. **Float Normalization:** 12-digit precision ensures numeric stability

---

## ✅ Validation Checklist

To verify encoding compliance:

- [ ] All JSON serialization uses `sort_keys=True`
- [ ] All JSON serialization uses `separators=(",", ":")`
- [ ] All hashes use SHA-256
- [ ] All hash outputs are lowercase hex
- [ ] All text concatenations use UTF-8 encoding
- [ ] All floats normalized to 12 digits precision
- [ ] HMASTER uses `"P2|"` prefix
- [ ] H_RICH uses alphabetically sorted sub-proof keys
- [ ] Timestamps only in P₄ (not in P₂)
- [ ] Environment captured but not modified

---

## 🔗 Cross-References

| Concept | Primary Implementation | Verification Surface |
|---------|----------------------|---------------------|
| `canonical_bytes()` | `bor/hash_utils.py:32` | All layers |
| `content_hash()` | `bor/hash_utils.py:53` | P₀, P₁, P₂ |
| `HMASTER` | `bor/core.py:146` | `bor/verify.py:59` |
| `H_RICH` | `bor/bundle.py:99` | `bor/verify.py:196` |
| `H_store` | `bor/store.py:63,138` | `bor/verify.py:125` |
| Sub-proof hashes | `bor/subproofs.py:28` | `bor/verify.py:192` |

---

## 📖 Conclusion

The BoR-Proof SDK v1.0.0 implements a **fully deterministic encoding hierarchy** with:

- **Single hash algorithm:** SHA-256 exclusively
- **Consistent canonicalization:** `sort_keys=True`, `separators=(",", ":")`
- **Text-based aggregation:** Pipe-separated hex strings
- **Domain separation:** `"P2|"` prefix for master proof
- **Hierarchical composition:** P₀ → P₁ → P₂ → sub-proofs → H_RICH

**Mathematical Guarantee:**

```
∀ (S₀, C, V, stages) : identical inputs → identical HMASTER
```

This specification provides the **BoR Encoding Constitution** — the mathematical foundation for provable reasoning identity.

---

**End of Encoding Specification**

*Generated from BoR-Proof SDK v1.0.0 codebase inspection*  
*All code snippets are exact quotes from the implementation*

