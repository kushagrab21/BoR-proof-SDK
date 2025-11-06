# Security Policy

## Cryptographic Guarantees

### Hashing
- **Algorithm**: SHA-256 only
- **Encoding**: Canonical JSON (sorted keys, fixed float precision to 12 significant digits, UTF-8)
- **Domain Separation**: P₂ uses `"P2|"` prefix to prevent collision attacks
- **Commitment**: H_RICH computed from sorted concatenation of sub-proof hashes

### Purity Enforcement
- All reasoning steps must be pure functions: `f(state, C, V) → state'`
- No side effects (I/O, network, global mutations, randomness) allowed in steps
- Signature validation enforced by `@step` decorator
- Invalid signatures rejected at decoration time

### Determinism
- Environment fingerprint captured in P₀ (Python version, OS, architecture, etc.)
- Fixed `PYTHONHASHSEED` required for reproducibility
- Canonical encoding ensures cross-platform consistency
- No floating-point arithmetic issues (fixed precision)

## Verification Process

### Levels of Verification

1. **Fast Verification** (no code execution)
   - Validates bundle structure
   - Recomputes sub-proof hashes
   - Validates H_RICH commitment
   - Exit code: 0=success, 1=mismatch

2. **Strong Verification** (with replay)
   - Executes reasoning chain with provided code
   - Recomputes HMASTER from scratch
   - Compares with stored primary.master
   - Requires trust in code execution environment

### Replay Integrity
- Deterministic replay must produce identical HMASTER
- Any mismatch indicates:
  - Tampering with proof data
  - Non-deterministic code
  - Environment differences
  - Purity violations

## Threat Model

### In Scope
- **Proof tampering**: Detected by hash mismatches
- **Non-determinism**: Caught by replay verification
- **Impurity**: Rejected by @step decorator
- **Commitment collision**: Mitigated by SHA-256 + domain separation

### Out of Scope
- Supply chain attacks on dependencies
- Execution environment compromise
- Side-channel attacks
- Quantum computing threats (SHA-256 assumption)

## Reporting a Vulnerability

If you discover a security vulnerability in the BoR-Proof SDK:

1. **Do NOT** open a public GitHub issue
2. Email the maintainers privately (see AUTHORS or CONTACT)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

4. Allow reasonable time for response (48-72 hours)

### What to Report
- Hash collision attacks
- Proof forgery techniques
- Purity enforcement bypasses
- Determinism violations
- Replay integrity issues

### What NOT to Report
- Denial of service (large inputs causing slowdown)
- Social engineering attacks
- Issues in dependencies (report to upstream)

## Best Practices for Users

### For Provers
1. Set `PYTHONHASHSEED=0` for determinism
2. Use virtual environments for reproducibility
3. Version-lock all dependencies
4. Test proof generation in clean environment
5. Verify your own proofs before sharing

### For Verifiers
1. Obtain proof bundle from trusted/signed source
2. Verify H_RICH before any code execution
3. Execute replay in isolated environment (sandbox/VM)
4. Compare HMASTER values byte-for-byte
5. Inspect trace output for sanity checks

### For Developers
1. Never disable purity checks
2. Avoid floating-point arithmetic where possible
3. Use canonical encoding for all serialization
4. Test determinism across platforms
5. Keep proof format stable (versioning)

## Secure Workflow Example

```bash
# 1. Generate proof in controlled environment
PYTHONHASHSEED=0 borp prove --all \
  --initial '...' --config '...' --version 'v1.0' \
  --stages module:fn --outdir proofs/

# 2. Self-verify before sharing
borp verify-bundle --bundle proofs/rich_proof_bundle.json \
  --initial '...' --config '...' --version 'v1.0' \
  --stages module:fn

# 3. Share bundle + index (sign with GPG/similar)
gpg --sign proofs/rich_proof_bundle.json

# 4. Verifier checks signature + verifies bundle
gpg --verify rich_proof_bundle.json.gpg
borp verify-bundle --bundle rich_proof_bundle.json
```

## Audit History

- **v0.1.0** (2025-11-06): Initial security policy
- No external audits completed yet

## Security Roadmap

### Planned
- [ ] Formal verification of core hash functions
- [ ] Fuzzing for proof parser
- [ ] Supply chain security (SBOM)
- [ ] Post-quantum hash migration plan

### Under Consideration
- [ ] Proof signature framework (GPG integration)
- [ ] Timestamping service integration
- [ ] Merkle tree optimization for large chains
- [ ] Zero-knowledge proof exploration

## Contact

For security concerns: Open a GitHub issue (public) or contact maintainers privately for sensitive issues.

---

**Note**: This SDK provides cryptographic integrity, not confidentiality. All proof data is public by design.

