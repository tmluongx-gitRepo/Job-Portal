#!/bin/bash
# Backend diagnostic script

echo "🔍 Checking Backend Status..."
echo ""

# Check if backend container exists and is running
echo "1. Checking Docker containers..."
if command -v docker &> /dev/null; then
    echo "Backend container status:"
    docker ps --filter "name=job-portal-backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    echo "Backend container logs (last 20 lines):"
    docker logs --tail 20 job-portal-backend 2>&1
    echo ""
else
    echo "⚠️  Docker command not available in this shell"
    echo "   Please run this from your host machine or a shell with docker access"
    echo ""
fi

# Check port accessibility
echo "2. Checking port accessibility..."
echo "From container network (backend:8000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" --max-time 5 http://backend:8000/health || echo "❌ Connection failed"
echo ""

echo "From localhost (localhost:8000):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" --max-time 5 http://localhost:8000/health || echo "❌ Connection failed"
echo ""

# Check environment
echo "3. Environment variables:"
echo "BACKEND_PORT: ${BACKEND_PORT:-8000 (default)}"
echo "NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-not set}"
echo ""

echo "4. Suggested fixes:"
echo "   - Check backend logs: docker logs job-portal-backend"
echo "   - Restart backend: docker-compose restart backend"
echo "   - Rebuild if architecture issue: docker-compose build --no-cache backend"
echo "   - Check if backend dependencies (MongoDB, Redis, ChromaDB) are running"

