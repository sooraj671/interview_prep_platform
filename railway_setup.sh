#!/bin/bash

# Railway Setup Script for Interview Preparation Platform
echo "🚀 Setting up Interview Preparation Platform on Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project or link existing
echo "📦 Setting up Railway project..."
railway init

# Add PostgreSQL service
echo "🗄️ Adding PostgreSQL database..."
railway add postgresql

# Add Redis service (free tier)
echo "🔴 Adding Redis cache..."
railway add redis

# Set environment variables from .env.railway
echo "⚙️ Setting environment variables..."
railway variables set APP_NAME="Interview Preparation Platform"
railway variables set APP_VERSION="1.0.0"
railway variables set APP_ENV="production"
railway variables set DEBUG="false"
railway variables set DATABASE_URL="${RAILWAY_POSTGRES_URL}"
railway variables set REDIS_URL="${RAILWAY_REDIS_URL}"
railway variables set JWT_SECRET_KEY="your_super_secret_jwt_key_change_this_in_production"
railway variables set JWT_ALGORITHM="HS256"
railway variables set JWT_ACCESS_TOKEN_EXPIRE_MINUTES="30"
railway variables set JWT_REFRESH_TOKEN_EXPIRE_DAYS="7"
railway variables set OLLAMA_BASE_URL="http://localhost:11434"
railway variables set OLLAMA_MODEL="llama2"
railway variables set ALLOWED_ORIGINS="*"
railway variables set ENABLE_OAUTH_LOGIN="true"
railway variables set ENABLE_RESUME_UPLOAD="true"
railway variables set ENABLE_AI_ROADMAPS="true"
railway variables set ENABLE_ASSESSMENTS="true"
railway variables set ENABLE_SIMULATION_MODE="true"
railway variables set ENABLE_LEADERBOARDS="true"
railway variables set ENABLE_INTERVIEWER_PROFILES="true"
railway variables set ENABLE_ANALYTICS="true"
railway variables set LOG_LEVEL="info"

echo "🎯 Railway setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add your OAuth credentials in Railway dashboard:"
echo "   - GOOGLE_CLIENT_ID"
echo "   - GOOGLE_CLIENT_SECRET"
echo "   - GITHUB_CLIENT_ID"
echo "   - GITHUB_CLIENT_SECRET"
echo "   - MICROSOFT_CLIENT_ID"
echo "   - MICROSOFT_CLIENT_SECRET"
echo "   - LINKEDIN_CLIENT_ID"
echo "   - LINKEDIN_CLIENT_SECRET"
echo ""
echo "2. Deploy your application:"
echo "   railway up"
echo ""
echo "3. Run database migrations:"
echo "   railway run 'python scripts/migrate_db.py'"
echo ""
echo "4. Your app will be available at:"
echo "   https://your-app-name.railway.app"
echo ""
echo "5. API documentation will be at:"
echo "   https://your-app-name.railway.app/docs"
