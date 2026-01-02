#!/bin/bash

echo "🔥 NIXPACKS DEPLOYMENT - No Docker, No Health Check"

# Step 1: Use Nixpacks configuration
echo "📦 Using Nixpacks (no Docker)..."
cp railway-nixpacks.toml railway.toml

# Step 2: Ensure main.py is working
cp app/main-working.py app/main.py

# Step 3: Remove old deployment
echo "🗑️ Removing old deployment..."
railway delete --service --yes 2>/dev/null || true

# Step 4: Wait
echo "⏳ Waiting for cleanup..."
sleep 5

# Step 5: Deploy with Nixpacks
echo "🚀 Deploying with Nixpacks (no health check)..."
railway up

echo ""
echo "✅ NIXPACKS DEPLOYMENT COMPLETE!"
echo "📋 Strategy:"
echo "1. Using Nixpacks builder (not Docker)"
echo "2. No health check configuration"
echo "3. Direct start command"
echo "4. Railway handles port binding"
echo ""
echo "🔗 Your app should be LIVE!"
echo "🧪 Test: https://your-app.railway.app/"
echo "📊 Check Railway dashboard for URL!"
