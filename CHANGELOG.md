# Changelog

All notable changes to the BoR-Proof SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-06

### Added

**Primary Proof Chain (P₀-P₄)**
- P₀: Initialization proof with environment fingerprinting
- P₁: Step-level proofs with purity enforcement via `@step` decorator
- P₂: Master proof aggregation with domain separation (HMASTER)
- P₃: Verification surface with deterministic replay
- P₄: Persistence proof for JSON and SQLite backends (H_store)

**Rich Proof Bundle (8 Sub-proofs)**
- DIP: Deterministic Identity Proof
- DP: Divergence Proof
- PEP: Purity Enforcement Proof
- PoPI: Proof-of-Proof Integrity
- CCP: Canonicalization Consistency Proof
- CMIP: Cross-Module Integrity Proof
- PP: Persistence Proof
- TRP: Temporal Reproducibility Proof
- H_RICH: Master commitment over all sub-proofs

**CLI Commands**
- `borp prove --all`: Generate rich proof bundle
- `borp verify --primary`: Verify primary proof via replay
- `borp verify-bundle`: Verify rich bundle (structure + hashes + optional replay)
- `borp persist`: Persist proofs with P₄ integrity
- `borp show --trace`: Render human-readable trace

**Infrastructure**
- Comprehensive test suite (88 tests across all proof layers)
- Example stages for quickstart (`examples/demo.py`)
- Complete documentation (README, SECURITY, CONTRIBUTING)
- GitHub Actions CI for automated testing

### Technical Details

- Canonical JSON encoding (sorted keys, fixed float precision, UTF-8)
- SHA-256 hashing throughout
- Purity enforcement for all reasoning steps
- Cross-platform determinism guarantees
- Zero-trust public verification

### Testing

- 88/88 tests passing
- Coverage across all proof layers (P₀-P₄, sub-proofs, CLI)
- Success and failure path testing
- Tampering detection validation

## [Unreleased]

### Planned
- Additional sub-proofs for advanced verification scenarios
- Performance optimizations for large proof chains
- Enhanced trace rendering with visualization options
- PyPI distribution for easier installation

