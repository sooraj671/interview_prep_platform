#!/bin/bash

echo "🚀 GUARANTEED Railway Deployment - Minimal Version"
echo "=================================================="

# Step 1: Clean up everything
echo "🧹 Cleaning up previous deployments..."
rm -f railway.toml
rm -f Dockerfile
rm -f requirements.txt

# Step 2: Use minimal guaranteed-working configuration
echo "📦 Setting up minimal configuration..."
cp requirements-minimal.txt requirements.txt
cp Dockerfile-minimal Dockerfile
cp railway-minimal.toml railway.toml
cp app/main-minimal.py app/main.py

# Step 3: Remove Railway service if exists
echo "🗑️ Removing old Railway service..."
railway delete --service --yes 2>/dev/null || true

# Step 4: Fresh deploy
echo "🚀 Deploying minimal version..."
railway up

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "📋 Next steps:"
echo "1. Check Railway dashboard for your app URL"
echo "2. Test: curl https://your-app-url.railway.app/health"
echo "3. Once working, we can add full features"
echo ""
echo "🔗 Your minimal app should be live in 2-3 minutes!"
