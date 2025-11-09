#!/bin/bash
# ======================================================
# 🚀 Cursor Setup — Step 1: Initialize Environment
# ======================================================

echo "🚀 Step 1: Environment Setup"
echo "============================="
echo ""

# Activate venv or create
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

echo "✅ Virtual environment ready"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip >/dev/null 2>&1
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install langchain_openai python-dotenv >/dev/null 2>&1
echo "✅ Dependencies installed"
echo ""

# Check .env
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    if [ -f "env.example" ]; then
        echo "📝 Creating .env from template..."
        cp env.example .env
        echo "✅ Created .env - please add your API key"
    fi
else
    echo "✅ .env file exists"
fi

echo ""
echo "============================="
echo "✅ Step 1 Complete!"
echo "============================="
echo ""
echo "Next: Run ./cursor_step2_bootstrap.sh"
echo ""

