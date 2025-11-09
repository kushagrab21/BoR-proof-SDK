# BoR-SDK Visual Proof Pipeline - README Updates

## Add to README.md

### CI/CD Badge

```markdown
[![Visual Proof CI](https://github.com/YOUR-USERNAME/BoR-proof-SDK/workflows/Visual%20Proof%20Pipeline%20CI/badge.svg)](https://github.com/YOUR-USERNAME/BoR-proof-SDK/actions)
```

### Quickstart Section

```markdown
## 🚀 Quickstart: Visual Proof Generation

The BoR-SDK includes a complete visualization pipeline that transforms reasoning traces into verified visual proofs with hallucination detection.

### Three Ways to Run

#### 1. Using Make (Recommended)
```bash
# Run complete pipeline (non-strict mode)
make visualize

# Run with strict verification (fail on warnings)
make visualize-strict

# Create timestamped artifact bundle
make bundle
```

#### 2. Using the Orchestrator Script
```bash
# Non-strict mode
./run_visual_pipeline.sh

# Strict mode (warnings treated as failures)
./run_visual_pipeline.sh --strict

# With session ID
./run_visual_pipeline.sh --strict --session SESSION_ID
```

#### 3. Using the CLI
```bash
# Install CLI entry point
pip install -e .

# Run pipeline
bor visualize

# Run with strict verification
bor visualize --strict

# With session ID
bor visualize --session SESSION_ID
```

### Pipeline Stages

The visual proof pipeline consists of 5 stages:

1. **Data Extraction** (`extract_trace_data.py`)
   - Extracts canonical reasoning trace from proof certificates
   - Output: `visual_data.json`

2. **Guard Computation** (`compute_hallucination_guards.py`)
   - Computes 4 hallucination detection metrics per step
   - Metrics: semantic similarity, entropy change, logical consistency, token overlap
   - Output: Updated `visual_data.json` with guard states

3. **Visualization Generation** (`generate_all_visualizations.py`)
   - Generates 4 publication-ready figures:
     - `reasoning_chain.svg` - Sequential reasoning flow
     - `hash_flow.png` - Cryptographic hash propagation
     - `hallucination_guard.png` - Guard metrics timeline
     - `master_certificate_tree.svg` - Certificate hierarchy
   - Output: `figures/` directory with SVG/PNG + JSON sidecar specs

4. **Visual Integrity Verification** (`verify_visual_integrity.py`)
   - Cross-checks visualizations against cryptographic proofs
   - 5 verification checks (hash correspondence, node count, chain integrity, guard accuracy, determinism)
   - Output: `visual_verification_report.json`

5. **Documentation Assembly** (`assemble_visual_proof.py`)
   - Generates complete markdown documentation
   - Embeds figures with verification summary
   - Output: `docs/visual_proof.md`

### Outputs

All artifacts are bundled in timestamped directories:

```
visual_proofs/YYYYmmdd-HHMMSS/
├── visual_data.json                     # Canonical reasoning trace
├── visual_verification_report.json      # Verification results
├── visual_proof.md                      # Complete documentation
└── figures/
    ├── reasoning_chain.svg
    ├── hash_flow.png
    ├── hallucination_guard.png
    ├── master_certificate_tree.svg
    └── *.spec.json                      # Sidecar verification specs
```

View results:
```bash
# Open the generated documentation
open visual_proofs/$(ls -t visual_proofs | head -1)/visual_proof.md
```
```

### Determinism & Verification Section

```markdown
## 🔐 Determinism & Verification

### Strict vs Non-Strict Mode

The visual proof pipeline supports two verification modes:

#### Non-Strict Mode (Default)
- Exit code 0: All checks passed OR warnings only (partial verification)
- Exit code 1: Not used in non-strict mode
- Exit code 2: Critical failures detected

Warnings are informational but don't cause pipeline failure. Suitable for development and exploratory analysis.

#### Strict Mode
- Exit code 0: All checks passed (complete verification)
- Exit code 1: Warnings detected (treated as failures)
- Exit code 2: Critical failures detected

All warnings must be resolved for pipeline to succeed. Suitable for CI/CD and production deployments.

### Exit Codes

| Code | Status | Meaning |
|------|--------|---------|
| 0 | ✅ Success | All verification checks passed |
| 1 | ⚠️ Warnings | Non-critical issues detected (fails in strict mode) |
| 2 | ❌ Failure | Critical verification failures |

### Verification Checks

The pipeline performs 5 independent verification checks:

1. **Hash Correspondence**: Verifies all SHA-256 hash prefixes in visualizations match `visual_data.json`
2. **Node Count Match**: Confirms correct number of nodes in hash flow graph (step nodes vs master nodes)
3. **Chain Integrity**: Validates parent→child hash linkage across reasoning chain
4. **Guard Status Accuracy**: Verifies guard metrics (4 per step) match computed values
5. **Determinism Verification**: Ensures no duplicate steps and correct master certificate aggregation

### Reproducibility

All visualization outputs are **deterministic** given the same input:
- Same `visual_data.json` → same figures
- Same proofs → same verification report
- Sidecar JSON specs enable non-OCR verification

To verify reproducibility:
```bash
# Run pipeline twice
make visualize
cp -r visual_proofs/$(ls -t visual_proofs | head -1) /tmp/run1

make clean && make visualize
cp -r visual_proofs/$(ls -t visual_proofs | head -1) /tmp/run2

# Compare outputs (should be identical)
diff -r /tmp/run1 /tmp/run2
```
```

### CI/CD Integration Section

```markdown
## 🔄 CI/CD Integration

### GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/visual-proof.yml`) that automatically:

1. Runs on every push and pull request
2. Tests on Python 3.11 and 3.12
3. Executes the complete pipeline in strict mode
4. Uploads artifacts (figures, reports, documentation)
5. Comments on PRs with verification results

### Artifacts

CI artifacts are retained for 30 days and include:
- Complete visual proof documentation
- All generated figures (SVG + PNG)
- Verification report (JSON)
- Canonical reasoning trace (JSON)
- Sidecar verification specs (JSON)

Download artifacts from the Actions tab or PR comments.

### Local CI Simulation

Test the CI workflow locally before pushing:

```bash
# Simulate CI environment
docker run -it --rm -v $(pwd):/workspace -w /workspace python:3.11
apt-get update && apt-get install -y graphviz make
pip install -r requirements.txt -r requirements-viz.txt
make visualize-strict
```

### Integration with Other CI Systems

The pipeline is CI-agnostic. Adapt the workflow for your CI platform:

**GitLab CI** (`.gitlab-ci.yml`):
```yaml
visual-proof:
  image: python:3.11
  before_script:
    - apt-get update && apt-get install -y graphviz
    - pip install -r requirements.txt -r requirements-viz.txt
  script:
    - make visualize-strict
  artifacts:
    paths:
      - visual_proofs/
      - visual_verification_report.json
      - docs/visual_proof.md
    expire_in: 30 days
```

**Jenkins** (Jenkinsfile):
```groovy
pipeline {
    agent { docker { image 'python:3.11' } }
    stages {
        stage('Setup') {
            steps {
                sh 'apt-get update && apt-get install -y graphviz'
                sh 'pip install -r requirements.txt -r requirements-viz.txt'
            }
        }
        stage('Visual Proof') {
            steps {
                sh 'make visualize-strict'
            }
        }
    }
    post {
        always {
            archiveArtifacts 'visual_proofs/**,visual_verification_report.json,docs/visual_proof.md'
        }
    }
}
```
```

### Troubleshooting Section

```markdown
## 🔧 Troubleshooting

### Common Issues

#### "graphviz not found"
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
choco install graphviz
```

#### "Permission denied: ./run_visual_pipeline.sh"
```bash
chmod +x run_visual_pipeline.sh
```

#### "No module named 'sentence_transformers'"
```bash
pip install -r requirements-viz.txt
```

#### Verification warnings in strict mode
Review the verification report to understand which checks warned:
```bash
cat visual_verification_report.json | python -m json.tool
```

Common warnings:
- **Node count mismatch**: Fixed in v1.0+ (separate step vs master nodes)
- **Chain integrity**: Check for multi-session data or broken parent links
- **Guard metrics**: Ensure `compute_hallucination_guards.py` completed successfully

### Debug Mode

Run individual pipeline stages with verbose output:
```bash
python extract_trace_data.py
python compute_hallucination_guards.py
python generate_all_visualizations.py
python verify_visual_integrity.py --fail-on-warn
python assemble_visual_proof.py
```

Check intermediate outputs:
```bash
# Verify data structure
cat visual_data.json | python -m json.tool | head -50

# Check guard computation
cat visual_data.json | python -c "import json, sys; d=json.load(sys.stdin); print(d['steps'][0]['guard_state'])"

# List generated figures
ls -lh figures/
```
```

---

## Installation

Add this to your existing README.md after the main description and before existing sections.

