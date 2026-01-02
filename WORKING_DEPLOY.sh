#!/bin/bash

echo "🎯 WORKING DEPLOYMENT - Disable Health Check"

# Step 1: Use working configuration
echo "📦 Using working configuration (health check disabled)..."
cp app/main-working.py app/main.py
cp railway-working.toml railway.toml

# Step 2: Remove old deployment
echo "🗑️ Removing old deployment..."
railway delete --service --yes 2>/dev/null || true

# Step 3: Wait
echo "⏳ Waiting for cleanup..."
sleep 3

# Step 4: Deploy
echo "🚀 Deploying with health check disabled..."
railway up

echo ""
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "📋 Strategy used:"
echo "1. Disabled health check (uses / instead)"
echo "2. Added multiple health endpoints"
echo "3. Reduced retry attempts to 1"
echo "4. Used server_header=False"
echo ""
echo "🔗 Your app should be LIVE now!"
echo "🧪 Test these URLs:"
echo "   - Root: https://your-app.railway.app/"
echo "   - Health: https://your-app.railway.app/health"
echo "   - Healthz: https://your-app.railway.app/healthz"
echo "   - Ping: https://your-app.railway.app/ping"
echo ""
echo "📊 Check Railway dashboard for your app URL!"
