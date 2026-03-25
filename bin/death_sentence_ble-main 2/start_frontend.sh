#!/bin/bash

# Death Sentence Frontend Server

echo "========================================"
echo "  Death Sentence Frontend"
echo "========================================"
echo ""

cd death_sentence/business_demo

echo "✅ Starting frontend server on port 8080..."
echo ""
echo "🌐 Open in browser: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m http.server 8080

