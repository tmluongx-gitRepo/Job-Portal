#!/bin/bash
# Quick script to restart just the frontend dev server without restarting the container

echo "🔄 Restarting frontend dev server..."

# Find and kill the Next.js dev server process
echo "🛑 Stopping Next.js dev server..."
pkill -f "next dev" || echo "   (No Next.js process found to kill)"

# Wait a moment for process to fully stop
sleep 1

# Start the dev server again
echo "🚀 Starting Next.js dev server..."
cd /workspace/frontend
bun run dev > /tmp/frontend-dev.log 2>&1 &

# Wait a moment and check if it started
sleep 2
if pgrep -f "next dev" > /dev/null; then
    echo "✅ Frontend dev server restarted successfully!"
    echo "   Logs: tail -f /tmp/frontend-dev.log"
    echo "   Or check: ps aux | grep 'next dev'"
else
    echo "❌ Failed to start dev server. Check logs: cat /tmp/frontend-dev.log"
    exit 1
fi

