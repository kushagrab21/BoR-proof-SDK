# Project Structure - BoR-Application

## Core Files (6)

### Python Modules
- **`bor_init.py`** - Main integration: LLM wrapper with complete reasoning certificate generation
- **`init_llm.py`** - LLM initialization helper using `langchain_openai`
- **`verify_proofs.py`** - Custom proof validator for certificate verification

### Shell Scripts
- **`cursor_setup.sh`** - Initial environment setup (venv, dependencies, .env check)
- **`cursor_step2_bootstrap.sh`** - Generate first reasoning certificate
- **`cursor_step3_verify.sh`** - Verify proof chain integrity

---

## Documentation (2)

- **`README.md`** - Complete project overview, quick start, usage examples
- **`REASONING_CERTIFICATE_GUIDE.md`** - Technical deep-dive into certificate structure and cryptographic properties

---

## Generated Artifacts

### `proofs/` directory (auto-generated)
- `session_*_manifest.json` - Environment fingerprint for deterministic replay
- `reasoning_cert_step_NNN_*.json` - Individual step certificates with full hashes
- `MASTER_CERTIFICATE_*.json` - Complete reasoning chain with master hash

---

## Existing BoR SDK Files (unchanged)

### Core SDK
- `bor/` - BoR Python package
  - `core.py`, `verify.py`, `bundle.py`, `store.py`, etc.

### Tests
- `tests/` - Original BoR SDK test suite

### Configuration
- `pyproject.toml` - Project metadata and dependencies
- `requirements.txt` - Python dependencies
- `.env` - API keys and configuration (gitignored)

---

## Architecture

```
User Code
    ↓
bor_init.py (reasoning certificate wrapper)
    ↓
init_llm.py (LangChain OpenAI)
    ↓
OpenAI API (gpt-4o, etc.)
    ↓
Reasoning Certificate (JSON)
    ↓
Cryptographic Chain (SHA-256)
    ↓
Master Certificate (tamper-evident)
```

---

## Certificate Flow

```
1. Session Start → Generate session_manifest.json
   ↓
2. First LLM Call → reasoning_cert_step_001.json
   ↓
3. Second LLM Call → reasoning_cert_step_002.json (linked to step 1)
   ↓
4. Third LLM Call → reasoning_cert_step_003.json (linked to steps 1-2)
   ↓
5. Session End → MASTER_CERTIFICATE.json (all steps + master hash)
```

---

## Clean Structure Achieved

**Removed**:
- ❌ Redundant test scripts (example_usage.py, test_*.py)
- ❌ Multiple verification variants (quick_verify.sh, full_verification*.sh)
- ❌ Temporary summaries (STATUS.md, FIXES_SUMMARY.md, etc.)
- ❌ Old changelogs (STEP*_COMPLETE.md, AVALANCHE_*.md)
- ❌ Setup prompt docs (CURSOR_*_PROMPT.md)

**Kept**:
- ✅ 3 core Python modules
- ✅ 3 essential shell scripts
- ✅ 2 comprehensive documentation files
- ✅ Original BoR SDK (untouched)

---

## File Count

- **Core files**: 6 (3 Python + 3 Shell)
- **Documentation**: 2 (README + Guide)
- **Total working files**: 8
- **Plus**: Original BoR SDK structure (~50 files preserved)

---

**Result**: Clean, precise, comprehensive structure with no redundancy.

