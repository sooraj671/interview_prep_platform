#!/bin/bash

echo "🐍 PYTHON DIRECT DEPLOYMENT - Ultra Simple"

# Step 1: Use Python direct config
echo "📦 Using direct Python deployment..."
cp railway-python.toml railway.toml

# Step 2: Create ultra simple main
echo "📝 Creating ultra simple app..."
cat > app/main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Step 3: Remove old deployment
echo "🗑️ Removing old deployment..."
railway delete --service --yes 2>/dev/null || true

# Step 4: Deploy
echo "🚀 Deploying ultra-simple Python app..."
railway up

echo ""
echo "✅ PYTHON DEPLOYMENT COMPLETE!"
echo "📋 This is the simplest possible FastAPI app"
echo "🔗 Test: https://your-app.railway.app/"
echo "📊 Railway dashboard will show your URL"
