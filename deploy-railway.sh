#!/bin/bash

# Railway Deployment Script
# Optimized deployment for Railway platform

echo "🚀 Deploying Interview Preparation Platform to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "📝 Please login to Railway:"
    railway login
fi

# Set environment variables
echo "⚙️ Setting up environment variables..."
railway variables APP_NAME="Interview Preparation Platform"
railway variables APP_VERSION="2.0.0"
railway variables APP_ENV=production
railway variables DEBUG=false

# Database configuration
railway variables DATABASE_ECHO=false
railway variables DATABASE_POOL_SIZE=5
railway variables DATABASE_MAX_OVERFLOW=10
railway variables DATABASE_POOL_TIMEOUT=10
railway variables DATABASE_POOL_RECYCLE=1800
railway variables DATABASE_CONNECT_TIMEOUT=5

# FastAPI configuration
railway variables HOST=0.0.0.0
railway variables PORT=8000

# Security
railway variables JWT_ALGORITHM=HS256
railway variables JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate limiting
railway variables RATE_LIMIT_REQUESTS=100
railway variables RATE_LIMIT_WINDOW=3600

# Monitoring
railway variables LOG_LEVEL=INFO
railway variables ENABLE_METRICS=true
railway variables ENABLE_TRACING=false

# Feature flags
railway variables ENABLE_OAUTH_LOGIN=true
railway variables ENABLE_RESUME_UPLOAD=true
railway variables ENABLE_AI_ROADMAPS=true
railway variables ENABLE_ASSESSMENTS=true
railway variables ENABLE_SIMULATION_MODE=true
railway variables ENABLE_LEADERBOARDS=true
railway variables ENABLE_INTERVIEWER_PROFILES=true
railway variables ENABLE_ANALYTICS=true

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 30

# Check deployment status
echo "🔍 Checking deployment status..."
railway status

# Get the deployment URL
DEPLOYMENT_URL=$(railway domain --raw 2>/dev/null)
if [ ! -z "$DEPLOYMENT_URL" ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Application URL: https://$DEPLOYMENT_URL"
    echo "📚 API Documentation: https://$DEPLOYMENT_URL/docs"
    echo "🏥 Health Check: https://$DEPLOYMENT_URL/health"
    echo "🔧 Ready Check: https://$DEPLOYMENT_URL/ready"
else
    echo "❌ Deployment failed or URL not available"
    echo "🔍 Check Railway dashboard for details"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Set up SECRET_KEY and JWT_SECRET_KEY in Railway dashboard"
echo "2. Configure AI service credentials (OLLAMA_BASE_URL, etc.)"
echo "3. Test the deployment at the provided URLs"
echo "4. Monitor logs with: railway logs"
