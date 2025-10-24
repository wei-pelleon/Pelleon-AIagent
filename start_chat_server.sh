#!/bin/bash
# Start the VE Agent Chat Server

echo "🚀 Starting VE Agent Chat Server..."
echo ""

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo ""
    echo "To use the chat feature, you need to set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Or create a .env file with:"
    echo "  OPENAI_API_KEY=your-api-key-here"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate venv
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

# Start server
echo "📡 Starting chat server on http://localhost:8000"
echo "📝 API docs at http://localhost:8000/docs"
echo ""
cd agent && python3 chat_server.py


