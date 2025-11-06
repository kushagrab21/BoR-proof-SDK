# Contributing to BoR-Proof SDK

Thank you for your interest in contributing! This document provides guidelines for contributing to the BoR-Proof SDK.

## Development Setup

### Prerequisites
- Python 3.9+
- pip
- git

### Setup Steps

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/bor-sdk.git
cd bor-sdk

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install in editable mode with dev dependencies
python -m pip install -e .
python -m pip install pytest black isort

# 5. Run tests to verify setup
pytest -q
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- Add/modify code
- Add/update tests
- Update documentation if needed

### 3. Run Tests

```bash
# Run all tests
pytest -q

# Run specific test file
pytest tests/test_p2_master.py -v

# Run with coverage
pytest --cov=bor --cov-report=html
```

### 4. Format Code

```bash
# Format with black
black .

# Sort imports with isort
isort .

# Or use both
black . && isort .
```

### 5. Commit Changes

```bash
git add .
git commit -m "type: brief description"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/modifications
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 6. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a Pull Request on GitHub.

## Contribution Guidelines

### Code Quality

1. **Tests Required**
   - All new features must include tests
   - Bug fixes should include regression tests
   - Maintain or improve test coverage (currently 88 tests)

2. **Purity Contracts**
   - All `@step` functions must be pure: `f(state, C, V) → state'`
   - No side effects (I/O, network, global mutations, randomness)
   - Signature must match exactly: 3 parameters, returns new state

3. **Determinism**
   - All operations must be deterministic
   - Use canonical encoding for JSON serialization
   - Fixed float precision (12 significant digits)
   - Sorted keys for dict serialization

4. **Breaking Changes**
   - Avoid breaking P₀-P₄ contracts
   - Maintain file format compatibility
   - Version bump if proof format changes
   - Document migration path

### Testing Guidelines

```python
# Test file naming: test_<module>_<feature>.py
# Test function naming: test_<functionality>_<scenario>

def test_verify_bundle_success():
    """verify_bundle_dict should pass for valid bundle."""
    b = _bundle()
    rep = verify_bundle_dict(b)
    assert rep["ok"] is True
```

### Documentation Guidelines

1. **Docstrings**
   - All public functions/classes need docstrings
   - Follow numpy/Google docstring style
   - Include parameters, returns, and examples

2. **README Updates**
   - Update if adding new CLI commands
   - Update if changing quickstart workflow
   - Add examples for new features

3. **CHANGELOG**
   - Add entry for all user-facing changes
   - Follow Keep a Changelog format

## Areas for Contribution

### High Priority
- [ ] Additional sub-proofs (verification dimensions)
- [ ] Performance optimizations (large proof chains)
- [ ] Enhanced trace rendering (visualization)
- [ ] CLI UX improvements

### Medium Priority
- [ ] Python API documentation (Sphinx)
- [ ] Tutorial notebooks
- [ ] Integration examples
- [ ] Proof archival/retrieval utilities

### Low Priority
- [ ] Alternative hash functions (experimental)
- [ ] Proof compression
- [ ] Distributed verification
- [ ] Web-based trace viewer

## Code Review Process

### What We Look For
1. **Correctness**: Does it work as intended?
2. **Tests**: Are there adequate tests?
3. **Determinism**: Is it deterministic?
4. **Purity**: Do steps remain pure?
5. **Documentation**: Is it documented?
6. **Style**: Does it follow conventions?

### Review Timeline
- Initial feedback: 48-72 hours
- Follow-up: 24-48 hours
- Merge: After approval from maintainer

## Proof Format Stability

### Critical Contracts (DO NOT BREAK)

1. **P₀ Structure**
   ```python
   {"S0": ..., "C": ..., "V": ..., "env": {...}}
   ```

2. **P₂ Domain Separation**
   ```python
   "P2|" + "|".join(stage_hashes)
   ```

3. **Bundle Structure**
   ```python
   {"primary": {...}, "subproofs": {...}, 
    "subproof_hashes": {...}, "H_RICH": "..."}
   ```

4. **Canonical Encoding**
   - Sorted keys
   - 12 significant digits for floats
   - UTF-8 encoding
   - Minified JSON

### Versioning Strategy
- Proof format version in `meta.proof_version` (future)
- Backward compatibility for readers
- Migration tools for format changes

## Debugging Tips

### Common Issues

**Determinism Failures**
```bash
# Set PYTHONHASHSEED for reproducibility
PYTHONHASHSEED=0 pytest tests/test_p1_steps.py

# Check float precision
python -c "import json; print(json.dumps(0.123456789012345))"
```

**Purity Violations**
```python
# BAD: Side effects
@step
def impure(x, C, V):
    print("side effect")  # ← I/O
    return x + 1

# GOOD: Pure function
@step
def pure(x, C, V):
    return x + 1
```

**Hash Mismatches**
```python
# Check canonical encoding
from bor.hash_utils import canonical_bytes
data = {"b": 2, "a": 1}
print(canonical_bytes(data))  # Should be sorted
```

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: See SECURITY.md
- **Chat**: (Discord/Slack link if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

Be respectful, professional, and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

---

Thank you for contributing to verifiable AI reasoning! 🎉

