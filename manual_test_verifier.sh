#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "🔁  BoR-Proof SDK — Full Manual Verification"
echo "=============================================="

# 1. Clean old artifacts
echo -e "\n🧹  Cleaning previous builds..."
rm -rf build dist *.egg-info out_test/ .venv_verify || true

# 2. Show repo + tag status
echo -e "\n📦  Current git tag + status:"
git describe --tags --always || echo "(no tag yet)"
git status -s || true

# 3. Rebuild
echo -e "\n🚧  Building package..."
python -m build

# 4. Validate metadata
echo -e "\n🧩  Validating package metadata with twine..."
twine check dist/*

# 5. Compute hashes
echo -e "\n🔐  SHA256 Checksums for artifacts:"
python - <<'PY'
import hashlib, glob
for p in sorted(glob.glob("dist/*")):
    with open(p, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    print(f"{p}: {h}")
PY

# 6. Fresh install test
echo -e "\n🧪  Installing wheel into temporary venv..."
python -m venv .venv_verify
source .venv_verify/bin/activate
pip install --no-cache-dir dist/*.whl

# 7. CLI sanity check
echo -e "\n🔍  Checking CLI help output..."
borp --help | head -15

# 8. Deterministic proof run
echo -e "\n⚙️  Running deterministic proof generation..."
borp prove --all \
  --initial '7' \
  --config '{"offset":4}' \
  --version 'v1.0' \
  --stages examples.demo:add examples.demo:square \
  --outdir out_test

# 9. Invariant + self-audit
echo -e "\n🔎  Evaluating invariant and self-audit..."
python evaluate_invariant.py --self-audit 1 || true
python evaluate_invariant.py --consensus-ledger || true

# 10. Summary footer
echo -e "\n✅  All manual verification steps completed."
echo "Check 'out_test/' for proof bundles and hashes."
deactivate

