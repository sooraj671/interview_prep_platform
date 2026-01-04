#!/bin/bash

# Final Fixed Deployment Script
# Deploy working version with all fixes applied

echo "🚀 FINAL FIXED DEPLOYMENT"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "📝 Please login to Railway:"
    railway login
fi

# Deploy fixed version
echo "🚀 Deploying fixed version to Railway..."
railway up

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 25

# Get the deployment URL
DEPLOYMENT_URL=$(railway domain --raw 2>/dev/null)
if [ ! -z "$DEPLOYMENT_URL" ]; then
    echo "✅ Fixed deployment successful!"
    echo "🌐 Application URL: https://$DEPLOYMENT_URL"
    echo "📚 API Documentation: https://$DEPLOYMENT_URL/docs"
    echo "🏥 Health Check: https://$DEPLOYMENT_URL/health"
    echo "🔧 Ready Check: https://$DEPLOYMENT_URL/ready"
    
    echo ""
    echo "🧪 Testing all endpoints..."
    
    # Test health endpoint
    echo "Testing health endpoint..."
    if curl -m 5 "https://$DEPLOYMENT_URL/health" > /dev/null 2>&1; then
        echo "✅ Health check working"
    else
        echo "❌ Health check failed - checking logs..."
        railway logs --tail 20
    fi
    
    # Test root endpoint
    echo "Testing root endpoint..."
    if curl -m 5 "https://$DEPLOYMENT_URL/" > /dev/null 2>&1; then
        echo "✅ Root endpoint working"
    else
        echo "❌ Root endpoint failed"
    fi
    
    # Test users endpoint
    echo "Testing users endpoint..."
    if curl -m 5 "https://$DEPLOYMENT_URL/users" > /dev/null 2>&1; then
        echo "✅ Users endpoint working"
    else
        echo "❌ Users endpoint failed"
    fi
    
    echo ""
    echo "🎉 DEPLOYMENT COMPLETE!"
    echo "📊 Summary:"
    echo "   - API: https://$DEPLOYMENT_URL"
    echo "   - Docs: https://$DEPLOYMENT_URL/docs"
    echo "   - Health: https://$DEPLOYMENT_URL/health"
    echo "   - Users: https://$DEPLOYMENT_URL/users"
    echo ""
    echo "🔍 If still having issues:"
    echo "   1. Check logs: railway logs --tail 50"
    echo "   2. Check environment variables in Railway dashboard"
    echo "   3. All endpoints should respond in < 5 seconds"
    
else
    echo "❌ Deployment failed or URL not available"
    echo "🔍 Check Railway dashboard for details"
fi
