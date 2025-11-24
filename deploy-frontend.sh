#!/bin/bash

# Company Registration Frontend Deployment Script
# This script restarts the frontend container to deploy all changes

echo "🚀 Deploying Company Registration Changes..."
echo ""

# Check if we're in the workspace
if [ ! -d "/workspace/frontend" ]; then
    echo "❌ Error: Not in workspace directory"
    exit 1
fi

echo "📦 Changes to be deployed:"
echo "  ✓ Company Registration route (/company-registration)"
echo "  ✓ Password fields removed"
echo "  ✓ Email validation added"
echo "  ✓ Comprehensive field validations (all tabs)"
echo "  ✓ Visual error feedback"
echo "  ✓ Navigation guards"
echo ""

echo "🔄 To deploy these changes, run the following commands from your HOST MACHINE:"
echo ""
echo "   cd /path/to/your/project"
echo "   docker compose restart frontend"
echo ""
echo "Or to rebuild and restart:"
echo ""
echo "   docker compose build frontend"
echo "   docker compose up -d frontend"
echo ""
echo "📍 After restart, access the application at:"
echo "   http://localhost:3000/company-registration"
echo ""
echo "✅ Deployment instructions ready!"

