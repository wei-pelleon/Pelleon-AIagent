#!/bin/bash
# Quick start script for VE Agent

echo "🚀 VE Agent - Value Engineering Optimizer"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import pandas" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Run workflow
echo ""
echo "🔄 Running VE workflow..."
echo ""
python3 agent/workflow.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Workflow completed successfully!"
    echo ""
    echo "📊 To view the dashboard, run:"
    echo "   streamlit run app.py"
    echo ""
else
    echo ""
    echo "❌ Workflow failed. Please check the error messages above."
    echo ""
    exit 1
fi


