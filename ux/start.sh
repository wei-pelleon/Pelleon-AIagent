#!/bin/bash
# Quick start script for VE Agent UI

echo "🎨 Starting VE Agent UI..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start dev server
echo "🚀 Launching development server..."
echo "   UI will open at http://localhost:3000"
echo ""
npm run dev


