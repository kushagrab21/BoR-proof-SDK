#!/bin/bash
# ======================================================
# 🧩 Cursor Prompt — Step 2: Bootstrap First Session
# ======================================================

echo "🚀 Step 2: Bootstrap First BoR-Verified Session"
echo "==============================================="
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ No .venv found. Run ./cursor_setup.sh first"
    exit 1
fi

# Load environment
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs 2>/dev/null)
    echo "✅ Environment variables loaded"
else
    echo "⚠️  No .env file"
fi

echo ""
echo "🧠 Running first BoR-verified reasoning chain..."
echo "==============================================="
echo ""

# Run first session
python - <<'EOF'
from bor_init import bor_chat, finalize_bor

print("🔍 Starting first BoR-verified reasoning chain...\n")

prompt = "Explain the purpose of BoR SDK proof logging in one sentence."
print(f"📝 Prompt: {prompt}\n")

print("⏳ Calling OpenAI API...")
print("="*60)

response = bor_chat(prompt)

print("\n" + "="*60)
print("🧠 LLM Response:")
print("="*60)
print(response)
print("="*60)
print(f"\n📊 Response length: {len(response)} characters")

finalize_bor()
print("\n✅ Proof session finalized and stored in ./proofs/")
EOF

echo ""
echo "==============================================="
echo "✅ Step 2 Complete!"
echo "==============================================="
echo ""
echo "Check proofs: ls -lh ./proofs/"
echo "Next: Run ./cursor_step3_verify.sh"
echo ""

