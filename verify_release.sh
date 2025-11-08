#!/usr/bin/env bash
set -euo pipefail

echo "🔁  Cleaning old build artifacts..."
rm -rf build dist *.egg-info

echo "📦  Building package..."
python -m build

echo "🧩  Checking metadata with twine..."
twine check dist/*

echo "🔐  Computing SHA256 checksums..."
python - <<'PY'
import hashlib, glob
for p in sorted(glob.glob("dist/*")):
    with open(p, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    print(f"{p}: {h}")
PY

echo "🧪  Installing wheel into fresh venv..."
python -m venv .venv_verify
source .venv_verify/bin/activate
pip install --quiet --no-cache-dir dist/*.whl

echo "🔍  Testing borp CLI..."
borp --help > /dev/null

echo "⚙️  Running deterministic proof test..."
borp prove --all --initial '7' --config '{"offset":4}' --version 'v1.0' \
  --stages examples.demo:add examples.demo:square --outdir out_test

echo "🔎  Verifying invariant..."
python evaluate_invariant.py --self-audit 1

echo "🧹  Cleaning up verify environment..."
deactivate
rm -rf .venv_verify out_test

echo ""
echo "✅  Manual pre-release verification complete!"
echo ""
echo "Next steps:"
echo "  1. Tag release: git tag v1.0.0"
echo "  2. Publish: python -m twine upload dist/*"

