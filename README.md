# BoR-Application: LLM Reasoning Certificate System

Complete verifiable AI reasoning with cryptographic proof chains.

---

## 🎯 Overview

This project integrates the **Blockchain of Reasoning (BoR) SDK** with **LangChain OpenAI** to generate **cryptographically-verifiable certificates** for every LLM reasoning step. Each certificate is a tamper-evident, deterministic proof of the exact chain of thought followed.

**Key Features**:
- ✅ **Complete Transparency**: Full SHA-256 hashes (not truncated), complete prompts & responses
- ✅ **Deterministic Replay**: Environment fingerprints enable exact reproduction
- ✅ **Cryptographic Chain**: Each step links to prior steps, tamper-evident
- ✅ **Audit-Ready**: Legally-defensible certificates for compliance

---

## 📁 Project Structure

```
BoR-proof-SDK/
├── bor_init.py                    # Core: LLM wrapper with reasoning certificates
├── init_llm.py                    # Core: LLM initialization module
├── verify_proofs.py               # Core: Custom proof validator
│
├── cursor_setup.sh                # Setup: Initial environment configuration
├── cursor_step2_bootstrap.sh      # Setup: First proof generation
├── cursor_step3_verify.sh         # Setup: Proof verification
│
├── REASONING_CERTIFICATE_GUIDE.md # Documentation: Complete guide
├── README.md                      # Documentation: This file
│
├── proofs/                        # Generated reasoning certificates
│   ├── session_*_manifest.json          # Environment fingerprint
│   ├── reasoning_cert_step_001_*.json   # Individual step certificates
│   └── MASTER_CERTIFICATE_*.json        # Complete chain
│
└── bor/                           # BoR SDK Core (Python package)
    ├── core.py
    ├── verify.py
    └── ...
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Run initial setup
./cursor_setup.sh
```

This will:
- Create virtual environment
- Install dependencies (`langchain_openai`, `python-dotenv`, `bor-sdk`)
- Verify `.env` exists

### 2. Configure API Key

Create `.env`:
```bash
OPENAI_API_KEY="your-key-here"
OPENAI_MODEL="gpt-4o"
OPENAI_TEMPERATURE=0.5
```

### 3. Generate First Reasoning Certificate

```bash
# Run proof generation
./cursor_step2_bootstrap.sh
```

### 4. Verify Proofs

```bash
# Verify proof chain integrity
./cursor_step3_verify.sh

# Or use custom verifier
python verify_proofs.py Cursor-Integrated-LLM
```

---

## 💻 Usage

### Basic Example

```python
from bor_init import bor_chat, finalize_bor

# Each call generates complete reasoning certificate
response = bor_chat("What is machine learning?")

# Generate master certificate
finalize_bor()
```

### Multi-Step Reasoning Chain

```python
from bor_init import bor_chat, finalize_bor

# Step 1
answer1 = bor_chat("What is 2+2?")

# Step 2 - cryptographically linked to step 1
answer2 = bor_chat("Multiply your previous answer by 3.")

# Step 3 - linked to all prior steps
answer3 = bor_chat("What is the final result?")

# Finalize and generate master certificate
finalize_bor()
```

**Generated Files**:
```
proofs/
├── session_1762644497_manifest.json          # Environment state
├── reasoning_cert_step_001_1762644504.json   # Step 1: "What is 2+2?"
├── reasoning_cert_step_002_1762644512.json   # Step 2: "Multiply by 3"
├── reasoning_cert_step_003_1762644520.json   # Step 3: "Final result?"
└── MASTER_CERTIFICATE_1762644497.json        # Complete chain
```

---

## 📋 Certificate Structure

### Individual Step Certificate

```json
{
  "certificate_version": "1.0.0",
  "session": {
    "id": "ef8a9ca11dae5eee2592a204fb208a01564f9a3cef825c247581659dad0397db",
    "step_number": 1
  },
  "prompt": {
    "content": "What is 2+2?",
    "hash_sha256": "52cb6b5e4a038af1756708f98afb718a08c75b87b2f03dbee4dd9c8139c15c5e",
    "length": 12
  },
  "response": {
    "content": "4",
    "hash_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    "elapsed_seconds": 6.835
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

### Master Certificate

```json
{
  "certificate_type": "MASTER_REASONING_CERTIFICATE",
  "chain": {
    "master_hash": "f95ef0a3cfbb319c9d522d0c0d200dea7e95d4404782fa1db2ddc033b56cd6d7",
    "step_hashes": ["3b332d8de9a39675378b495637322543dab5578afecfea96ebd87e73f24ebc36"],
    "integrity_verified": true
  },
  "steps": [ /* All step certificates */ ],
  "verification": {
    "deterministic_replay_possible": true,
    "tamper_detection": "Any modification breaks chain hash"
  }
}
```

---

## 🔐 Cryptographic Properties

### Deterministic Chain Hashing

Each step's hash depends on:
- Session ID
- Step number  
- Prompt content
- **All prior step hashes**

```python
context_hash = SHA256({
    "session_id": session_id,
    "step": step_num,
    "prompt": prompt,
    "prior_steps": [hash1, hash2, ...]
})
```

### Tamper Detection

Modify any step → entire chain hash changes → tampering detected

```python
master_hash = SHA256(
    step1_hash + step2_hash + step3_hash + ...
)
```

---

## 📊 Console Output Example

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

🤖 LLM Configuration:
   Model:       gpt-4o
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
   Chain Hash: 3b332d8de9a39675378b495637322543dab5578afecfea96ebd87e73f24ebc36
================================================================================
```

---

## ✅ Verification

### Verify Hash Integrity

```python
import json
import hashlib

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

### Verify Complete Chain

```bash
# Use custom verifier
python verify_proofs.py Cursor-Integrated-LLM
```

Output:
```
🔍 Verifying 3 proof(s)...
✅ All proofs structurally valid
✅ Found 3 proof(s) for session 'Cursor-Integrated-LLM'
✅ Hash integrity verified
```

---

## 🎯 Use Cases

| Use Case | Benefit |
|----------|---------|
| **Audit & Compliance** | Prove exact reasoning for critical decisions |
| **Debugging** | Inspect exact prompts, responses, and chain |
| **Reproducibility** | Environment fingerprints enable exact replay |
| **Trust & Verification** | Third-party verification of AI reasoning |
| **Legal Defense** | Tamper-evident certificates for liability |

---

## 📚 Documentation

- **[REASONING_CERTIFICATE_GUIDE.md](REASONING_CERTIFICATE_GUIDE.md)** - Complete technical guide
- **[BoR Encoding Specification](BoR_Encoding_Specification_v1.0.0.md)** - BoR SDK specs
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute

---

## 🛠️ Requirements

- Python 3.9+
- OpenAI API key
- Dependencies: `langchain_openai`, `python-dotenv`, `bor-sdk`

---

## 📝 License

See [LICENSE](LICENSE)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🎓 Result

**Every LLM call generates a cryptographically-verifiable, legally-defensible certificate** with:

✅ Complete transparency (full hashes, not truncated)  
✅ Deterministic replay (environment fingerprints)  
✅ Tamper-evident chain (SHA-256 linking)  
✅ Audit-ready documentation (JSON certificates)

**The reasoning certificate system provides complete traceability and accountability for AI decision-making.**
