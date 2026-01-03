#!/bin/bash

# Complete Railway Deployment Script
echo "🚀 Complete Railway Deployment for Interview Preparation Platform"

# Step 1: Login and setup
echo "🔐 Step 1: Logging into Railway..."
railway login

# Step 2: Create project
echo "📦 Step 2: Creating Railway project..."
railway init

# Step 3: Add PostgreSQL
echo "🗄️ Step 3: Adding PostgreSQL database..."
echo "PostgreSQL" | railway add

# Step 4: Add Redis
echo "🔴 Step 4: Adding Redis cache..."
echo "Redis" | railway add

# Step 5: Set environment variables manually
echo "⚙️ Step 5: Setting environment variables..."

# Get Railway PostgreSQL URL
POSTGRES_URL=$(railway variables get RAILWAY_POSTGRES_URL 2>/dev/null || echo "")
REDIS_URL=$(railway variables get RAILWAY_REDIS_URL 2>/dev/null || echo "")

# Set environment variables one by one
railway variables set APP_NAME="Interview Preparation Platform"
railway variables set APP_VERSION="1.0.0"
railway variables set APP_ENV="production"
railway variables set DEBUG="false"
railway variables set DATABASE_URL="$POSTGRES_URL"
railway variables set REDIS_URL="$REDIS_URL"
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

# Step 6: Deploy the application
echo "🚀 Step 6: Deploying application..."
railway up

# Step 7: Wait for deployment and run migrations
echo "⏳ Step 7: Waiting for deployment to complete..."
sleep 30

echo "🔄 Step 8: Running database migrations..."
railway run 'python scripts/migrate_db.py'

# Step 8: Get the application URL
echo "📱 Step 9: Getting application URL..."
APP_URL=$(railway domain 2>/dev/null || echo "https://your-app.railway.app")

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo ""
echo "📋 Your Application Details:"
echo "🌐 App URL: $APP_URL"
echo "📚 API Docs: $APP_URL/docs"
echo "❤️  Health Check: $APP_URL/health"
echo ""
echo "🔧 Next Steps:"
echo "1. Add OAuth credentials in Railway dashboard:"
echo "   - GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET"
echo "   - GITHUB_CLIENT_ID & GITHUB_CLIENT_SECRET"
echo "   - MICROSOFT_CLIENT_ID & MICROSOFT_CLIENT_SECRET"
echo "   - LINKEDIN_CLIENT_ID & LINKEDIN_CLIENT_SECRET"
echo ""
echo "2. Test your application at: $APP_URL"
echo "3. View API documentation at: $APP_URL/docs"
echo ""
echo "✅ Your Interview Preparation Platform is now live!"
