# 🚀 Interview Preparation Platform - Setup Guide

## 📋 Table of Contents

1. [Ollama Integration](#ollama-integration)
2. [Database Setup](#database-setup)
3. [Railway Deployment Configuration](#railway-deployment-configuration)
4. [Project Documentation Generation](#project-documentation-generation)
5. [API Documentation Access](#api-documentation-access)

---

## 🔗 Ollama Integration

### Prerequisites

- Ollama installed and running locally
- At least one model pulled (e.g., `ollama pull llama2`)

### Configuration Steps

#### 1. Update Configuration Files

**Update `src/config/ai.yaml`:**

```yaml
ai:
  ollama:
    base_url: "http://localhost:11434"
    models:
      default: "llama2"
      roadmap: "llama2"
      assessment: "llama2"
      simulation: "llama2"
    timeout: 30
    max_retries: 3
    retry_delay: 1
```

#### 2. Environment Variables

**Add to `.env` file:**

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=30
OLLAMA_MAX_RETRIES=3
```

#### 3. Test Ollama Connection

**Create test script `test_ollama.py`:**

```python
import asyncio
import httpx

async def test_ollama():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print("✅ Ollama is running!")
                print(f"Available models: {response.json()}")
            else:
                print("❌ Ollama is not responding")
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
```

#### 4. Run Test

```bash
python test_ollama.py
```

#### 5. Integration with FastAPI

The LLM client is already configured in `src/infrastructure/ai/llm_client.py`. The application will automatically use Ollama when configured.

---

## 🗄️ Database Setup

### Prerequisites

- PostgreSQL installed locally or use cloud service
- Python virtual environment

### Configuration Steps

#### 1. Database Configuration

**Update `src/config/database.yaml`:**

```yaml
database:
  url: "postgresql://username:password@localhost:5432/interview_prep"
  echo: false
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 3600
```

#### 2. Environment Variables

**Add to `.env` file:**

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/interview_prep
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

#### 3. Install Database Dependencies

```bash
pip install psycopg2-binary sqlalchemy alembic
```

#### 4. Initialize Database with Alembic

**Step 1: Initialize Alembic (if not already done)**

```bash
cd /Users/soorajkumar/CascadeProjects/interview_prep_platform
alembic init alembic
```

**Step 2: Configure Alembic**

**Update `alembic.ini`:**

```ini
# sqlalchemy.url = postgresql://username:password@localhost:5432/interview_prep
sqlalchemy.url = ${DATABASE_URL}
```

**Update `alembic/env.py`:**

```python
from src.config.settings import config_loader
from src.domain.entities import user, skill, roadmap, assessment, analytics

# Add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata
```

#### 5. Create Database Migrations

**Create initial migration:**

```bash
alembic revision --autogenerate -m "Initial migration"
```

**Apply migrations:**

```bash
alembic upgrade head
```

#### 6. Create Database Schema

**Create `scripts/create_database.py`:**

```python
import asyncio
from sqlalchemy import create_engine
from src.config.settings import config_loader
from src.domain.entities import Base

async def create_database():
    settings = config_loader.load_config()
    engine = create_engine(settings.database.url)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_database())
```

**Run the script:**

```bash
python scripts/create_database.py
```

#### 7. Seed Initial Data

**Create `scripts/seed_data.py`:**

```python
import asyncio
from src.application.use_cases.auth.register_user import RegisterUserUseCase, RegisterUserRequest

async def seed_admin():
    # Create admin user
    admin_request = RegisterUserRequest(
        email="admin@example.com",
        password="admin123",
        first_name="Admin",
        last_name="User",
        role="admin"
    )

    use_case = RegisterUserUseCase()
    await use_case.execute(admin_request)
    print("✅ Admin user created!")

if __name__ == "__main__":
    asyncio.run(seed_admin())
```

---

## 🚂 Railway Deployment Configuration

### Prerequisites

- Railway account
- Railway CLI installed
- Project pushed to GitHub

### Configuration Steps

#### 1. Railway Environment Variables

**Set up environment variables in Railway dashboard:**

```bash
# Application
APP_NAME=Interview Preparation Platform
APP_VERSION=1.0.0
APP_ENV=production
DEBUG=false

# Database (use Railway's PostgreSQL)
DATABASE_URL=${RAILWAY_POSTGRES_URL}

# OAuth Providers
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# JWT
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI/LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Redis (if using Railway's Redis)
REDIS_URL=${RAILWAY_REDIS_URL}

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 2. Update Railway.toml

**Ensure your `railway.toml` is configured:**

```toml
[build]
builder = "NIXPACKS"

[deploy]
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[[services]]
name = "api"
sourceDir = "."

[services.variables]
PORT = "8000"
PYTHON_VERSION = "3.11"

# Start command for refactored architecture
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

#### 3. Database Setup on Railway

**Option 1: Use Railway's PostgreSQL**

1. Add PostgreSQL service in Railway
2. Railway will provide `RAILWAY_POSTGRES_URL`
3. Use this URL in your configuration

**Option 2: External Database**

1. Set `DATABASE_URL` to your external database
2. Ensure database is accessible from Railway

#### 4. Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy
railway up
```

#### 5. Run Database Migrations on Railway

**Create `scripts/railway_migrate.py`:**

```python
import asyncio
import os
from alembic.config import Config
from alembic import command

async def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("✅ Database migrations completed!")

if __name__ == "__main__":
    asyncio.run(run_migrations())
```

**Add to Railway deployment script or run manually:**

```bash
python scripts/railway_migrate.py
```

---

## 📚 Project Documentation Generation

### Automatic Documentation with FastAPI

FastAPI automatically generates OpenAPI/Swagger documentation.

#### 1. Enable Documentation in Production

**Update `main.py`:**

```python
from src.config.settings import config_loader

settings = config_loader.load_config()

app = FastAPI(
    title=settings.name,
    description="AI-powered interview preparation platform",
    version=settings.version,
    docs_url="/docs" if settings.environment.value != "production" else None,
    redoc_url="/redoc" if settings.environment.value != "production" else None,
    openapi_url="/openapi.json" if settings.environment.value != "production" else None,
)
```

#### 2. Generate Static Documentation

**Create `scripts/generate_docs.py`:**

```python
import json
from main import app

def generate_openapi_docs():
    # Generate OpenAPI schema
    openapi_schema = app.openapi()

    # Save to file
    with open("docs/openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)

    print("✅ OpenAPI documentation generated!")

if __name__ == "__main__":
    generate_openapi_docs()
```

#### 3. Create Comprehensive Documentation

**Create `docs/README.md`:**

```markdown
# Interview Preparation Platform API Documentation

## Overview

This document describes the REST API for the Interview Preparation Platform.

## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:
```

Authorization: Bearer <your_jwt_token>

````

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-app.railway.app`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user profile

### Users
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `POST /api/v1/users/upload-resume` - Upload and parse resume

### Roadmaps
- `POST /api/v1/roadmaps/generate` - Generate personalized roadmap
- `GET /api/v1/roadmaps/{id}` - Get roadmap details
- `PUT /api/v1/roadmaps/{id}/regenerate` - Regenerate roadmap

### Assessments
- `POST /api/v1/assessments/generate` - Generate assessment
- `POST /api/v1/assessments/{id}/start` - Start assessment
- `POST /api/v1/assessments/{id}/submit` - Submit answer

### Simulation
- `POST /api/v1/simulation/start` - Start interview simulation
- `POST /api/v1/simulation/{id}/answer` - Submit simulation answer

### Analytics
- `GET /api/v1/analytics/dashboard` - Get user analytics
- `GET /api/v1/analytics/leaderboard` - Get leaderboard
- `GET /api/v1/analytics/users/discover` - Discover users

## Error Handling
All errors follow this format:
```json
{
  "error": {
    "type": "error_type",
    "message": "Human-readable error message",
    "status_code": 400,
    "correlation_id": "uuid"
  }
}
````

## Rate Limiting

API requests are rate-limited to prevent abuse.

```

```

#### 4. Generate Sphinx Documentation (Optional)

**Install Sphinx:**

```bash
pip install sphinx sphinx-rtd-theme
```

**Create Sphinx configuration:**

```bash
cd docs
sphinx-quickstart
```

**Update `docs/conf.py`:**

```python
html_theme = "sphinx_rtd_theme"
```

**Generate documentation:**

```bash
cd docs
make html
```

---

## 📖 API Documentation Access

### 1. Interactive Swagger UI

**Development Environment:**

```
http://localhost:8000/docs
```

**Production Environment:**

```
https://your-app.railway.app/docs
```

### 2. ReDoc Documentation

**Development Environment:**

```
http://localhost:8000/redoc
```

**Production Environment:**

```
https://your-app.railway.app/redoc
```

### 3. OpenAPI JSON Schema

**Development Environment:**

```
http://localhost:8000/openapi.json
```

**Production Environment:**

```
https://your-app.railway.app/openapi.json
```

### 4. Available API Endpoints

Here's a comprehensive list of all APIs in your project:

#### Authentication APIs (`/api/v1/auth/`)

- `POST /register` - Register new user
- `POST /login` - User login with OAuth
- `POST /refresh` - Refresh JWT token
- `POST /logout` - User logout
- `GET /me` - Get current user profile
- `PUT /me` - Update current user profile
- `POST /me/change-password` - Change user password
- `GET /oauth/{provider}/login` - Get OAuth login URL
- `GET /oauth/{provider}/callback` - OAuth callback handler

#### User Management APIs (`/api/v1/users/`)

- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `POST /upload-resume` - Upload and parse resume
- `POST /interview-feedback` - Submit interview feedback
- `GET /interview-feedback/history` - Get feedback history

#### Roadmap APIs (`/api/v1/roadmaps/`)

- `POST /generate` - Generate personalized roadmap
- `GET /{id}` - Get roadmap details
- `PUT /{id}/regenerate` - Regenerate roadmap
- `POST /{id}/topics/{topic_id}/complete` - Mark topic as complete
- `GET /{id}/progress` - Get roadmap progress

#### Assessment APIs (`/api/v1/assessments/`)

- `POST /generate` - Generate assessment
- `GET /{id}` - Get assessment details
- `POST /{id}/start` - Start assessment
- `POST /{id}/answer` - Submit assessment answer
- `POST /{id}/complete` - Complete assessment
- `GET /{id}/results` - Get assessment results

#### Simulation APIs (`/api/v1/simulation/`)

- `POST /start` - Start interview simulation
- `POST /{id}/answer` - Submit simulation answer
- `POST /{id}/next-question` - Get next question
- `POST /{id}/complete` - Complete simulation
- `GET /{id}/feedback` - Get simulation feedback

#### Study Mode APIs (`/api/v1/study/`)

- `POST /session/start` - Start study session
- `POST /session/{id}/continue` - Continue study session
- `GET /session/{id}/exercises` - Get practice exercises

#### Analytics APIs (`/api/v1/analytics/`)

- `GET /dashboard` - Get user analytics dashboard
- `GET /skill-progress` - Get skill progress trends
- `GET /readiness-score` - Get readiness score
- `GET /assessment-history` - Get assessment history

#### Leaderboard APIs (`/api/v1/leaderboard/`)

- `GET /` - Get leaderboard
- `GET /filters` - Get available filters
- `GET /my-rank` - Get user's rank

#### User Discovery APIs (`/api/v1/discovery/`)

- `GET /users` - Discover users
- `GET /interviewers` - Discover interviewers
- `GET /filters` - Get discovery filters

#### Health & System APIs

- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /` - Root endpoint with API info

### 5. Testing API Endpoints

**Using curl:**

```bash
# Health check
curl http://localhost:8000/health

# Get API info
curl http://localhost:8000/

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","first_name":"Test","last_name":"User"}'
```

**Using Python requests:**

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Get API docs
response = requests.get("http://localhost:8000/openapi.json")
print(response.json())
```

---

## 🚀 Quick Start Checklist

### Local Development

1. [ ] Install Ollama and pull a model
2. [ ] Set up PostgreSQL database
3. [ ] Configure environment variables
4. [ ] Run database migrations
5. [ ] Start the FastAPI application
6. [ ] Access API documentation at `http://localhost:8000/docs`

### Railway Deployment

1. [ ] Push code to GitHub
2. [ ] Configure Railway environment variables
3. [ ] Add PostgreSQL service
4. [ ] Deploy to Railway
5. [ ] Run database migrations
6. [ ] Test API endpoints
7. [ ] Access API documentation at `https://your-app.railway.app/docs`

---

## 🔧 Troubleshooting

### Common Issues

#### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Check Ollama service status
curl http://localhost:11434/api/tags
```

#### Database Connection Issues

```bash
# Test database connection
psql $DATABASE_URL

# Check migration status
alembic current
alembic history
```

#### Railway Deployment Issues

```bash
# Check Railway logs
railway logs

# Check environment variables
railway variables
```

---

## 📞 Support

For additional help:

1. Check the API documentation at `/docs`
2. Review the error logs for detailed information
3. Ensure all environment variables are properly set
4. Verify database migrations are applied

---

**🎉 Your Interview Preparation Platform is now fully configured and ready to use!**
