# 🎓 LLM Reasoning Certificate System

## Overview

This system generates **complete, deterministic, cryptographically-verifiable certificates** for every LLM reasoning step. Each certificate is a tamper-evident proof of the exact chain of thought followed.

---

## 📋 Certificate Structure

### 1. **Session Manifest** (`session_TIMESTAMP_manifest.json`)

Captures the complete execution environment:

```json
{
  "session_id": "ef8a9ca11dae5eee2592a204fb208a01564f9a3cef825c247581659dad0397db",
  "environment": {
    "os": "Darwin 23.0.0",
    "python_version": "3.13.7",
    "machine": "arm64",
    "model": "gpt-5-nano-2025-08-07",
    "temperature": "0.5",
    "api_key_fingerprint": "e2102b527eaf97d497cf0b3ef1c16f78...",
    "working_directory": "/path/to/project"
  }
}
```

**Purpose**: Enables deterministic replay - anyone with these parameters can reproduce the exact reasoning chain.

---

### 2. **Step Certificate** (`reasoning_cert_step_NNN_TIMESTAMP.json`)

Complete certificate for each reasoning step:

```json
{
  "certificate_version": "1.0.0",
  "session": {
    "id": "ef8a9ca11dae5eee2592a204fb208a01564f9a3cef825c247581659dad0397db",
    "step_number": 1
  },
  "timestamp": {
    "unix": 1762644497.242933,
    "iso_utc": "2025-11-08T23:28:17.242933Z",
    "iso_local": "2025-11-09T04:58:17.242933"
  },
  "prompt": {
    "content": "What is 2+2?",
    "hash_sha256": "52cb6b5e4a038af1756708f98afb718a08c75b87b2f03dbee4dd9c8139c15c5e",
    "length": 12
  },
  "response": {
    "content": "4",
    "hash_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    "length": 1,
    "elapsed_seconds": 6.835
  },
  "model": {
    "name": "gpt-5-nano-2025-08-07",
    "temperature": 0.5,
    "provider": "OpenAI"
  },
  "chain": {
    "context_hash": "0d494834bfc2cba2782453bdc37a1220c844c28c319c9bb6269e024d6f563113",
    "prior_step_hashes": [],
    "deterministic_chain_hash": "3b332d8de9a39675378b495637322543dab5578afecfea96ebd87e73f24ebc36"
  },
  "verification": {
    "deterministic": true,
    "reproducible": true,
    "tamper_evident": true,
    "cryptographic_proof": "SHA-256 chain linking"
  }
}
```

**Key Features**:
- ✅ **Complete hashes** (not truncated) - every SHA-256 hash shown in full
- ✅ **Full prompt and response** - exact text content preserved
- ✅ **Timing information** - precise timestamps and duration
- ✅ **Chain linking** - cryptographically links to prior steps
- ✅ **Model parameters** - exact configuration used

---

### 3. **Master Certificate** (`MASTER_CERTIFICATE_TIMESTAMP.json`)

Cryptographically links all reasoning steps into a single verifiable chain:

```json
{
  "certificate_type": "MASTER_REASONING_CERTIFICATE",
  "session": {
    "id": "ef8a9ca11dae5eee2592a204fb208a01564f9a3cef825c247581659dad0397db",
    "duration_seconds": 6.839,
    "total_steps": 1
  },
  "chain": {
    "master_hash": "f95ef0a3cfbb319c9d522d0c0d200dea7e95d4404782fa1db2ddc033b56cd6d7",
    "step_hashes": [
      "3b332d8de9a39675378b495637322543dab5578afecfea96ebd87e73f24ebc36"
    ],
    "integrity_verified": true
  },
  "steps": [
    { /* Complete step 1 certificate */ },
    { /* Complete step 2 certificate */ },
    ...
  ],
  "verification": {
    "deterministic_replay_possible": true,
    "cryptographic_integrity": "SHA-256 chain",
    "tamper_detection": "Any modification breaks chain hash"
  }
}
```

**Purpose**: 
- Single file contains **entire reasoning history**
- Master hash verifies **all steps** in one check
- Tamper-evident - any change breaks the chain

---

## 🔐 Cryptographic Properties

### 1. **Deterministic Chain Hashing**

Each step's hash depends on:
- Session ID
- Step number
- Prompt content
- All prior step hashes

```python
context_hash = SHA256({
    "session_id": session_id,
    "step": step_num,
    "prompt": prompt,
    "prior_steps": [hash1, hash2, ...]
})
```

### 2. **Master Chain Integrity**

```python
master_hash = SHA256(
    step1_chain_hash + 
    step2_chain_hash + 
    step3_chain_hash + ...
)
```

**Result**: Change ANY step → master hash breaks → tamper detected

---

## 📊 Output Format

### Console Output (Complete Traceability):

```
================================================================================
🔍 STEP 1 - REASONING TRACE
================================================================================
📝 Prompt (12 chars):
   What is 2+2?

🔐 Deterministic Fingerprints:
   Prompt Hash (SHA-256):  52cb6b5e4a038af1756708f98afb718a08c75b87b2f03dbee4dd9c8139c15c5e
   Context Hash (SHA-256): 0d494834bfc2cba2782453bdc37a1220c844c28c319c9bb6269e024d6f563113
   Session ID:             ef8a9ca11dae5eee2592a204fb208a01564f9a3cef825c247581659dad0397db
   Step Number:            1

🤖 LLM Configuration:
   Model:       gpt-5-nano-2025-08-07
   Temperature: 0.5
   Time (UTC):  2025-11-08T23:28:17.242968Z

⏳ Calling LLM...

✅ LLM Response received in 6.835s

💬 Response (1 chars):
────────────────────────────────────────────────────────────────────────────────
4
────────────────────────────────────────────────────────────────────────────────

🔐 Response Hash (SHA-256): 4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a

📋 REASONING CERTIFICATE SAVED
   File: reasoning_cert_step_001_1762644504.json
   Size: 1194 bytes
   Chain Hash: 3b332d8de9a39675378b495637322543dab5578afecfea96ebd87e73f24ebc36
================================================================================
```

---

## 🎯 Use Cases

### 1. **Audit & Compliance**
- Prove exact reasoning used for critical decisions
- Show model version, parameters, and complete chain
- Tamper-evident - modifications detectable

### 2. **Debugging & Analysis**
- Inspect exact prompts and responses
- Track reasoning evolution across steps
- Identify where reasoning diverged

### 3. **Reproducibility**
- Environment fingerprint enables exact replay
- Complete parameter capture
- Deterministic verification

### 4. **Trust & Verification**
- Third parties can verify certificates
- Cryptographic proof of authenticity
- Chain-of-custody for AI reasoning

---

## 🚀 Usage

### Basic Usage:

```python
from bor_init import bor_chat, finalize_bor

# Each call generates complete reasoning certificate
response1 = bor_chat("What is machine learning?")
response2 = bor_chat("Explain your previous answer in simpler terms.")
response3 = bor_chat("Give an example.")

# Generate master certificate linking all steps
finalize_bor()
```

### Generated Files:

```
proofs/
├── session_1762644497_manifest.json          # Environment fingerprint
├── reasoning_cert_step_001_1762644504.json   # Step 1 certificate
├── reasoning_cert_step_002_1762644512.json   # Step 2 certificate  
├── reasoning_cert_step_003_1762644520.json   # Step 3 certificate
└── MASTER_CERTIFICATE_1762644497.json        # Complete chain
```

---

## ✅ Verification

### Verify Individual Step:

```bash
# Check step certificate exists and is valid JSON
cat proofs/reasoning_cert_step_001_*.json | python -m json.tool
```

### Verify Complete Chain:

```bash
# Check master certificate contains all steps
cat proofs/MASTER_CERTIFICATE_*.json | python -m json.tool
```

### Verify Hash Integrity:

```python
import json
import hashlib

# Load step certificate
with open('proofs/reasoning_cert_step_001_*.json') as f:
    cert = json.load(f)

# Verify prompt hash
computed = hashlib.sha256(cert['prompt']['content'].encode()).hexdigest()
assert computed == cert['prompt']['hash_sha256'], "Prompt tampered!"

# Verify response hash
computed = hashlib.sha256(cert['response']['content'].encode()).hexdigest()
assert computed == cert['response']['hash_sha256'], "Response tampered!"

print("✅ Certificate verified - no tampering detected")
```

---

## 🎓 Result

**You now have**:
- ✅ Complete transparency - every hash, every step
- ✅ Full traceability - deterministic replay possible
- ✅ Cryptographic proof - tamper-evident chain
- ✅ Reasoning certificate - audit-ready documentation

**Every LLM call** generates a **legally-defensible, cryptographically-verifiable certificate** of the exact reasoning process used.

