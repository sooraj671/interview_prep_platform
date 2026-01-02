#!/bin/bash

echo "📚 DEPLOY FULL API with Documentation"

# Step 1: Use full API version
echo "📦 Deploying full API with documentation..."
cp app/main-full.py app/main.py
cp railway-nixpacks.toml railway.toml

# Step 2: Deploy
echo "🚀 Deploying full API..."
railway up

echo ""
echo "✅ FULL API DEPLOYED!"
echo "📚 Documentation available at:"
echo "   📖 Swagger UI: https://your-app.railway.app/docs"
echo "   📋 ReDoc: https://your-app.railway.app/redoc"
echo "   🔧 OpenAPI JSON: https://your-app.railway.app/openapi.json"
echo ""
echo "🧪 Test these sample endpoints:"
echo "   👥 Users: https://your-app.railway.app/api/v1/users"
echo "   💻 Skills: https://your-app.railway.app/api/v1/skills"
echo "   🗺️ Roadmaps: https://your-app.railway.app/api/v1/roadmaps"
echo "   📝 Assessments: https://your-app.railway.app/api/v1/assessments"
echo ""
echo "🎯 The /docs page will show interactive API documentation!"
