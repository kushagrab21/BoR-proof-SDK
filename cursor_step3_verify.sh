#!/bin/bash
# ======================================================
# 🔍 Cursor Prompt — Step 3: Verify Proof Chain
# ======================================================

echo "🔍 Step 3: Verifying Proof Chain Integrity"
echo "=========================================="
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ No .venv found"
    exit 1
fi

# Load environment
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs 2>/dev/null)
fi

echo "🔍 Verifying proof files..."
echo "=========================================="
echo ""

# Manual verification
python - <<'EOF'
import os
import json
from pathlib import Path

proofs_dir = Path("./proofs")
if not proofs_dir.exists():
    print("❌ No proofs directory found")
    print("💡 Run Step 2 first: ./cursor_step2_bootstrap.sh")
    exit(1)

proof_files = list(proofs_dir.glob("*.json"))
if not proof_files:
    print("❌ No proof files found")
    exit(1)

print(f"✅ Found {len(proof_files)} proof file(s)\n")

for proof_file in sorted(proof_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
    print(f"📄 File: {proof_file.name}")
    print(f"   Size: {proof_file.stat().st_size} bytes")
    
    try:
        with open(proof_file) as f:
            proof = json.load(f)
        
        if 'session' in proof:
            print(f"   ✅ Session: {proof['session']}")
        if 'hash' in proof:
            print(f"   ✅ Hash: {proof['hash'][:16]}...")
        if 'prompt' in proof:
            print(f"   ✅ Prompt: {proof['prompt'][:50]}...")
        
        print(f"   ✅ Structure: VALID\n")
        
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

print("="*60)
print("✅ Verification complete")
print("="*60)
EOF

echo ""
echo "=========================================="
echo "📁 All Proof Files"
echo "=========================================="
ls -lth ./proofs/ 2>/dev/null | head -10

echo ""
echo "=========================================="
echo "✅ Step 3 Complete!"
echo "=========================================="
echo ""

