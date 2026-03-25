#!/bin/bash

# Restart AI Backend - Kills any existing process on port 8000 first

echo "========================================"
echo "  Restarting AI Backend"
echo "========================================"
echo ""

# Kill any process using port 8000
echo "🔍 Checking for processes on port 8000..."
PID=$(lsof -ti:8000)

if [ ! -z "$PID" ]; then
    echo "⚠️  Found process(es) using port 8000: $PID"
    echo "🔪 Killing process(es)..."
    kill -9 $PID 2>/dev/null
    sleep 1
    echo "✅ Port 8000 cleared"
else
    echo "✅ Port 8000 is free"
fi

echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install AI backend dependencies
echo "📦 Installing AI backend dependencies..."
cd death_sentence/agents
pip install -q -r requirements.txt
cd ../..

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: OPENAI_API_KEY not set!"
    echo "Please set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
    read -p "Press Enter to continue anyway (will fail) or Ctrl+C to exit..."
fi

echo ""
echo "✅ Starting AI Backend on port 8000..."
echo "   Frontend: http://localhost:8080"
echo "   API: http://localhost:8000"
echo ""

# Run from project root using module path (fixes relative import issue)
uvicorn death_sentence.agents.app:app --reload --port 8000

