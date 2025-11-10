#!/bin/bash
# Start the frontend development server from within the devcontainer

cd /workspace/frontend

echo "🚀 Starting Next.js development server..."
echo ""
echo "This will run on http://localhost:3000"
echo ""

# Ensure dependencies are installed
if [ ! -d "node_modules" ] || [ ! -d "node_modules/lucide-react" ]; then
  echo "📦 Installing dependencies first..."
  bun install
  echo ""
fi

# Start the dev server
bun run dev

