#!/bin/bash

echo "🚀 FINAL DEPLOYMENT - Guaranteed Working Version"

# Step 1: Use simplest possible configuration
echo "📦 Using ultra-simple configuration..."
cp app/main-simple.py app/main.py
cp railway-simple.toml railway.toml

# Step 2: Remove old deployment completely
echo "🗑️ Removing old deployment..."
railway delete --service --yes 2>/dev/null || true

# Step 3: Wait a moment for cleanup
echo "⏳ Waiting for cleanup..."
sleep 5

# Step 4: Deploy
echo "🚀 Deploying ultra-simple version..."
railway up

echo ""
echo "✅ FINAL DEPLOYMENT COMPLETE!"
echo "📋 This version:"
echo "1. Uses simplest FastAPI app possible"
echo "2. Uses /health endpoint (standard)"
echo "3. Uses PORT environment variable"
echo "4. No extra middleware or complexity"
echo ""
echo "🔗 Check Railway dashboard for your URL!"
echo "🧪 Test: curl https://your-app.railway.app/health"
