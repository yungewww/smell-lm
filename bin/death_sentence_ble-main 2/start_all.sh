#!/bin/bash

# Start All Death Sentence Services
# Opens 3 terminal tabs - one for each service

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Starting All Death Sentence Services                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set!"
    echo "Please run: export OPENAI_API_KEY='your-key-here'"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

echo "🚀 Launching services in separate Terminal tabs..."
echo ""

# Use AppleScript to open Terminal tabs (macOS)
osascript <<EOF
tell application "Terminal"
    activate
    
    -- Tab 1: BLE Backend
    do script "cd '$PROJECT_DIR' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '  🔵 BLE Backend (Port 5001)' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '' && ./start_ble_backend.sh"
    
    -- Wait a moment
    delay 1
    
    -- Tab 2: AI Backend
    tell application "System Events" to keystroke "t" using command down
    delay 0.5
    do script "cd '$PROJECT_DIR' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '  🟢 AI Backend (Port 8000)' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '' && export OPENAI_API_KEY='$OPENAI_API_KEY' && ./restart_ai_backend.sh" in front window
    
    -- Wait a moment
    delay 1
    
    -- Tab 3: Frontend
    tell application "System Events" to keystroke "t" using command down
    delay 0.5
    do script "cd '$PROJECT_DIR' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '  🟡 Frontend Server (Port 8080)' && echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' && echo '' && ./start_frontend.sh" in front window
    
end tell
EOF

echo ""
echo "✅ All services starting in new Terminal tabs!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 Service URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔵 BLE Backend:    http://localhost:5001"
echo "  🟢 AI Backend:     http://localhost:8000"
echo "  🟡 Frontend:       http://localhost:8080"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Open in browser: http://localhost:8080"
echo ""
echo "💡 To stop all services: ./kill_all.sh"
echo ""

