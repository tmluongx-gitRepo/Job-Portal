#!/bin/bash

# Restart Frontend Application Script
# This script stops the frontend, clears all caches, and restarts it

set -e  # Exit on error

echo "============================================"
echo "🔄 Restarting Frontend Application"
echo "============================================"
echo ""

# Step 1: Stop existing processes
echo "📛 Step 1: Stopping existing Next.js processes..."
pkill -f "next dev" 2>/dev/null || echo "   No Next.js process found (that's okay)"
pkill -f "bun run dev" 2>/dev/null || echo "   No Bun process found (that's okay)"
sleep 2
echo "   ✓ Processes stopped"
echo ""

# Step 2: Clear Next.js build cache
echo "🧹 Step 2: Clearing Next.js build cache..."
cd /workspace/frontend
if [ -d ".next" ]; then
    rm -rf .next
    echo "   ✓ Removed .next directory"
else
    echo "   ℹ️  .next directory doesn't exist (already clean)"
fi
echo ""

# Step 3: Clear Bun cache
echo "🧹 Step 3: Clearing Bun package cache..."
bun pm cache rm 2>/dev/null || echo "   ℹ️  Bun cache already clear"
echo "   ✓ Bun cache cleared"
echo ""

# Step 4: Clear node_modules/.cache if it exists
echo "🧹 Step 4: Clearing node_modules cache..."
if [ -d "node_modules/.cache" ]; then
    rm -rf node_modules/.cache
    echo "   ✓ Removed node_modules/.cache"
else
    echo "   ℹ️  No node_modules/.cache found"
fi
echo ""

# Step 5: Reinstall dependencies (optional but ensures fresh state)
echo "📦 Step 5: Ensuring dependencies are up to date..."
bun install --frozen-lockfile 2>&1 | tail -n 5
echo "   ✓ Dependencies verified"
echo ""

# Step 6: Start the development server
echo "🚀 Step 6: Starting Next.js development server..."
echo "   This will run in the background..."
nohup bun run dev > /tmp/nextjs.log 2>&1 &
NEXT_PID=$!
echo "   ✓ Dev server started (PID: $NEXT_PID)"
echo ""

# Step 7: Wait for server to be ready
echo "⏳ Step 7: Waiting for server to be ready..."
COUNTER=0
MAX_ATTEMPTS=30

while [ $COUNTER -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "   ✓ Server is ready!"
        break
    fi
    echo -n "."
    sleep 1
    COUNTER=$((COUNTER + 1))
done

echo ""

if [ $COUNTER -eq $MAX_ATTEMPTS ]; then
    echo "   ⚠️  Server did not respond within 30 seconds"
    echo "   Check logs: tail -f /tmp/nextjs.log"
    exit 1
fi

echo ""

# Step 8: Test the routes
echo "🧪 Step 8: Testing routes..."
echo ""

# Test home page
echo -n "   • Testing / (home)... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ (200 OK)"
else
    echo "✗ (HTTP $HTTP_CODE)"
fi

# Test login page
echo -n "   • Testing /login... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/login)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ (200 OK)"
else
    echo "✗ (HTTP $HTTP_CODE)"
fi

# Test signup page
echo -n "   • Testing /signup... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/signup)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ (200 OK)"
else
    echo "✗ (HTTP $HTTP_CODE)"
fi

# Test company-registration page
echo -n "   • Testing /company-registration... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/company-registration)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ (200 OK)"
else
    echo "✗ (HTTP $HTTP_CODE)"
fi

echo ""
echo "============================================"
echo "✅ Frontend Application Restart Complete!"
echo "============================================"
echo ""
echo "📊 Status:"
echo "   • Server running at: http://localhost:3000"
echo "   • Process ID: $NEXT_PID"
echo "   • Logs: tail -f /tmp/nextjs.log"
echo ""
echo "🌐 Test in browser:"
echo "   • Home: http://localhost:3000"
echo "   • Login: http://localhost:3000/login"
echo "   • Signup: http://localhost:3000/signup"
echo "   • Company Registration: http://localhost:3000/company-registration"
echo ""
echo "To view live logs, run: tail -f /tmp/nextjs.log"
echo ""



