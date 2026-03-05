#!/bin/bash

# teams-dashboard launcher script
# Starts the Agent Teams monitoring dashboard

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Kill any existing server on port 4747
lsof -ti:4747 | xargs kill -9 2>/dev/null

echo "Starting Agent Teams Dashboard..."
echo "Server: http://localhost:4747"
echo "WebSocket: ws://localhost:4747"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server in the background
node backend/server.js &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Open browser
if command -v open &> /dev/null; then
  open http://localhost:4747
elif command -v xdg-open &> /dev/null; then
  xdg-open http://localhost:4747
fi

# Wait for Ctrl+C
trap "kill $SERVER_PID 2>/dev/null; exit" INT TERM

# Keep script running
wait $SERVER_PID
