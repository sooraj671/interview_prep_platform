#!/bin/bash

# Fixed Railway Setup Script for Interview Preparation Platform
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

# Add PostgreSQL service (updated command)
echo "🗄️ Adding PostgreSQL database..."
railway add

# Add Redis service (updated command)
echo "🔴 Adding Redis cache..."
railway add

# Set environment variables (updated command format)
echo "⚙️ Setting environment variables..."
railway variables import .env.railway

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
