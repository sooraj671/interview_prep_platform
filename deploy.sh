#!/bin/bash

echo "🚀 Deploying Interview Prep Platform to Railway..."

# Step 1: Use lightweight configurations
echo "📦 Setting up lightweight configuration..."
cp requirements-free.txt requirements.txt
cp Dockerfile-free Dockerfile
cp railway-free.toml railway.toml

# Step 2: Clean up any cached builds
echo "🧹 Cleaning up..."
railway delete --service --yes 2>/dev/null || true

# Step 3: Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "📊 Check your Railway dashboard for the deployment URL"
