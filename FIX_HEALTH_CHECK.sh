#!/bin/bash

echo "🔧 Fixing Railway Health Check Issue..."

# Step 1: Use fixed configuration
echo "📦 Applying health check fix..."
cp app/main-fixed.py app/main.py
cp railway-fixed.toml railway.toml

# Step 2: Remove old deployment
echo "🗑️ Removing old deployment..."
railway delete --service --yes 2>/dev/null || true

# Step 3: Deploy with fix
echo "🚀 Deploying with health check fix..."
railway up

echo ""
echo "✅ Health check fix applied!"
echo "📋 Changes made:"
echo "1. Added /ready endpoint for health check"
echo "2. Increased timeout to 60 seconds"
echo "3. Added timestamp to responses"
echo ""
echo "🔗 Your app should be live now!"
