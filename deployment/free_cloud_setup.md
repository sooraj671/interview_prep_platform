# Free Cloud Deployment Guide

## Option 1: Railway (Recommended - $5/month free credit)

### Setup Steps:

1. **Install Railway CLI**

```bash
npm install -g @railway/cli
```

2. **Login and Initialize**

```bash
railway login
cd interview_prep_platform
railway init
```

3. **Create Railway Configuration**

```bash
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
```

4. **Deploy**

```bash
railway up
```

5. **Set Environment Variables in Railway Dashboard**

- `DATABASE_URL`: Provided by Railway PostgreSQL
- `SECRET_KEY`: Generate a secure random key
- `DEBUG`: false
- `OLLAMA_BASE_URL`: https://api.ollama.ai (free API)

### Free AI Services Integration:

Replace Ollama with free APIs:

1. **Groq API (Free tier)**

```python
# Update app/ai/llm_client.py
class FreeLLMClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"

    async def generate_text(self, prompt: str, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 1000)
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/chat/completions",
                                    headers=headers, json=payload)
            return response.json()["choices"][0]["message"]["content"]
```

2. **Hugging Face Inference API (Free)**

```python
# Free embeddings
class FreeEmbeddingClient:
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.base_url = "https://api-inference.huggingface.co"

    async def generate_embedding(self, text: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {"inputs": text}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/sentence-transformers/all-MiniLM-L6-v2",
                headers=headers, json=payload
            )
            return response.json()[0]
```

## Option 2: Render (Free Tier)

### Create render.yaml:

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

## Option 3: Vercel + Supabase (Free)

### 1. Deploy API to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### 2. Set up Supabase (Free PostgreSQL)

- Go to https://supabase.com
- Create new project
- Get connection string
- Set as DATABASE_URL in Vercel

### 3. Create vercel.json

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

## Option 4: PythonAnywhere (Free)

### Steps:

1. **Sign up** at https://www.pythonanywhere.com/
2. **Create Web App** → Flask → Custom
3. **Upload code** via Git or drag-and-drop
4. **Install dependencies** in virtual environment
5. **Configure WSGI** for FastAPI

## Free AI Services Configuration

### Get Free API Keys:

1. **Groq** (https://groq.com/)

   - Free tier: 30 requests/minute
   - Models: Llama3 70B, Mixtral 8x7B

2. **Hugging Face** (https://huggingface.co/)

   - Free tier: 30,000 requests/month
   - Models: All sentence transformers

3. **OpenRouter** (https://openrouter.ai/)
   - Free tier: $5/month credit
   - Access to multiple models

### Update Configuration:

```bash
# .env file for free deployment
DATABASE_URL=your_free_database_url
SECRET_KEY=your_secure_secret_key
DEBUG=false

# Free AI Services
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
OLLAMA_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Minimal Resource Version

### Remove Heavy Dependencies:

Update requirements.txt to lightweight version:

```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# AI (Free APIs only)
httpx==0.25.2
groq==0.4.1

# Data
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# Utils
python-dotenv==1.0.0
```

### SQLite Version (No Database Cost):

```python
# Update app/database.py for SQLite
DATABASE_URL = "sqlite:///./interview_prep.db"

# Note: Remove pgvector features for SQLite
```

## Deployment Checklist:

- [ ] Choose hosting platform (Railway recommended)
- [ ] Get free API keys (Groq, Hugging Face)
- [ ] Set environment variables
- [ ] Test deployment
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring

## Cost Breakdown (Free Tier):

| Service      | Free Tier          | Cost After Free   |
| ------------ | ------------------ | ----------------- |
| Railway      | $5/month credit    | $0.25/1000 hours  |
| Render       | 750 hours/month    | $7/month          |
| Vercel       | 100GB bandwidth    | $20/month         |
| Groq         | 30 requests/min    | $0.25/1M tokens   |
| Hugging Face | 30K requests/month | $0.10/1K requests |

**Total for first 1000 users: $0-5/month**
