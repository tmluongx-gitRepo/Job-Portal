#!/bin/bash
# Startup script for devcontainer - auto-starts frontend dev server

echo "🚀 Starting devcontainer services..."

# Install frontend dependencies if needed
if [ ! -d "/workspace/frontend/node_modules" ]; then
  echo "📦 Installing frontend dependencies..."
  cd /workspace/frontend && bun install
fi

# Start frontend dev server in background
echo "🎨 Starting Next.js dev server on port 3000..."
cd /workspace/frontend
bun run dev &

# Keep container alive
echo "✅ Devcontainer ready!"
echo "   - Frontend: http://localhost:3000"
echo "   - Logs: docker compose logs -f devcontainer"
echo ""

# Wait indefinitely
wait

