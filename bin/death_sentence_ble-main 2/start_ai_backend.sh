#!/bin/bash

# Death Sentence AI Backend Startup Script

echo "========================================"
echo "  Death Sentence AI Backend"
echo "========================================"
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
    echo "⚠️  WARNING: OPENAI_API_KEY not set!"
    echo "Please set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

echo ""
echo "✅ Starting AI Backend on port 8000..."
echo "   Frontend: http://localhost:8080"
echo "   API: http://localhost:8000"
echo ""

# Run from project root using module path (fixes relative import issue)
uvicorn death_sentence.agents.app:app --reload --port 8000

