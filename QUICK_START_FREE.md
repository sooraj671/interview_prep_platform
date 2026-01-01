# 🆓 Quick Start - Free Cloud Deployment

Run your Interview Preparation Platform for FREE using cloud services!

## 🚀 **Option 1: Railway (Recommended - $5/month free credit)**

### Step 1: Sign Up & Install

```bash
# 1. Create Railway account at https://railway.app/
# 2. Install Railway CLI
npm install -g @railway/cli

# 3. Login
railway login
```

### Step 2: Prepare Your Code

```bash
cd interview_prep_platform

# Create railway.toml
cat > railway.toml << 'EOF'
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[services]]
name = "api"
sourceDir = "."

[services.variables]
PORT = "8000"
EOF
```

### Step 3: Get Free API Keys

```bash
# 1. Get Groq API Key (Free)
# Go to https://groq.com/ → Sign up → Get API key

# 2. Get Hugging Face API Key (Free)
# Go to https://huggingface.co/ → Sign up → Get API key
```

### Step 4: Deploy

```bash
# Initialize Railway project
railway init

# Deploy
railway up
```

### Step 5: Set Environment Variables

In Railway dashboard, set these variables:

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/interview_prep
SECRET_KEY=your-secure-random-key-here
DEBUG=false

# Free AI Services
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
OLLAMA_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🌐 **Option 2: Render (Free Tier)**

### Step 1: Create render.yaml

```yaml
services:
  - type: web
    name: interview-prep-api
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt && pip install groq"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: interview-prep-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: GROQ_API_KEY
        sync: false
      - key: HUGGINGFACE_API_KEY
        sync: false
      - key: OLLAMA_BASE_URL
        value: https://api.groq.com/openai/v1

databases:
  - name: interview-prep-db
    plan: free
```

### Step 2: Deploy

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. Connect GitHub to Render at https://render.com/
# 3. Deploy automatically starts
```

## ⚡ **Option 3: Vercel + Supabase (Free)**

### Step 1: Deploy API to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Step 2: Set up Supabase (Free PostgreSQL)

1. Go to https://supabase.com/
2. Create new project
3. Get connection string
4. Set as DATABASE_URL in Vercel

### Step 3: Create vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

## 🔑 **Free API Keys Setup**

### Groq (Free - 30 requests/minute)

```bash
# Sign up: https://groq.com/
# Get API key from dashboard
# Free tier includes:
# - Llama3 70B
# - Mixtral 8x7B
# - Gemma 7B
```

### Hugging Face (Free - 30,000 requests/month)

```bash
# Sign up: https://huggingface.co/
# Get API key from settings
# Free tier includes all sentence transformers
```

### OpenRouter (Free - $5/month credit)

```bash
# Sign up: https://openrouter.ai/
# Get API key from dashboard
# Access to 100+ models
```

## 🛠 **Minimal Resource Version**

If you have very limited resources, use this lightweight version:

### Update requirements.txt

```txt
# Core only
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Free AI APIs only
httpx==0.25.2
groq==0.4.1

# Data
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# Utils
python-dotenv==1.0.0
```

### Update app/main.py for Free Services

```python
# Replace AI service initialization
from app.ai.free_llm_client import get_free_llm_client
from app.ai.free_embedding_client import get_free_embedding_client

# In startup event
llm_client = get_free_llm_client()
embedding_client = get_free_embedding_client()
```

## 📊 **Cost Comparison**

| Platform       | Free Tier       | Cost After Free  | Best For        |
| -------------- | --------------- | ---------------- | --------------- |
| Railway        | $5/month credit | $0.25/1000 hours | Full-featured   |
| Render         | 750 hours/month | $7/month         | Beginners       |
| Vercel         | 100GB bandwidth | $20/month        | Static/API only |
| PythonAnywhere | Web app only    | $5/month         | Learning        |

**Total for first 1000 users: $0-5/month**

## 🔧 **Environment Setup**

### .env for Free Deployment

```bash
# Core
DATABASE_URL=your_free_database_url
SECRET_KEY=your_secure_secret_key
DEBUG=false

# Free AI Services
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
OLLAMA_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional OAuth (Free tier limits)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

## ✅ **Testing Your Deployment**

### Health Check

```bash
curl https://your-app.railway.app/health
```

### API Documentation

```bash
# Visit: https://your-app.railway.app/docs
```

### Test Registration

```bash
curl -X POST "https://your-app.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "auth_provider": "email"
  }'
```

## 🚨 **Troubleshooting**

### Common Issues:

1. **Database Connection**: Ensure DATABASE_URL is correct
2. **API Keys**: Verify free API keys are valid
3. **Memory Limits**: Use minimal version for low resources
4. **CORS**: Set ALLOWED_ORIGINS correctly

### Logs:

```bash
# Railway
railway logs

# Render
# Check Render dashboard logs

# Vercel
vercel logs
```

## 🎯 **Next Steps**

1. **Choose Platform**: Railway recommended for best experience
2. **Get API Keys**: Groq + Hugging Face (both free)
3. **Deploy**: Follow platform-specific instructions
4. **Test**: Verify health endpoint and API docs
5. **Customize**: Add your OAuth providers
6. **Monitor**: Check usage and upgrade when needed

## 📈 **Scaling Path**

When you're ready to scale beyond free tier:

1. **Railway**: Upgrade to Pro ($20/month)
2. **Render**: Upgrade to Standard ($7/month)
3. **Database**: Move to managed PostgreSQL
4. **AI**: Upgrade to paid API tiers
5. **Storage**: Add AWS S3 for file uploads

Your MVP is ready to launch for FREE! 🚀
