#!/bin/bash
# Run this from your HOST MACHINE (not devcontainer) to stop the old frontend container

echo "Stopping the old separate frontend container..."
docker stop job-portal-frontend 2>/dev/null || echo "Frontend container not running"
docker rm job-portal-frontend 2>/dev/null || echo "Frontend container already removed"

echo ""
echo "✅ Done!"
echo ""
echo "Now run the frontend from inside your devcontainer:"
echo "  /workspace/start-frontend.sh"

