# Railway Environment Variables

## Required Environment Variables

### Database Configuration

```
DB_HOST=${{POSTGRES_HOST}}
DB_PORT=${{POSTGRES_PORT}}
DB_NAME=${{POSTGRES_DATABASE}}
DB_USER=${{POSTGRES_USER}}
DB_PASSWORD=${{POSTGRES_PASSWORD}}
DATABASE_URL=postgresql://${{POSTGRES_USER}}:${{POSTGRES_PASSWORD}}@${{POSTGRES_HOST}}:${{POSTGRES_PORT}}/${{POSTGRES_DATABASE}}
```

### AI Configuration

```
INFERENCE_API_KEY=inference-7879a8ca800d4e39a0395f057f407f90
INFERENCE_BASE_URL=https://api.inference.net/v1
INFERENCE_MODEL=google/gemma-3-27b-instruct/bf-16
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
AI_REQUEST_TIMEOUT=60
AI_MAX_RETRIES=3
```

### Application Configuration

```
APP_NAME=Interview Preparation Platform
APP_VERSION=1.0.0
APP_ENV=production
DEBUG=false
PORT=8000
PYTHON_VERSION=3.11
```

### Authentication

```
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### CORS Configuration

```
ALLOWED_ORIGINS=*
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*
```

### Feature Flags

```
ENABLE_OAUTH_LOGIN=true
ENABLE_RESUME_UPLOAD=true
ENABLE_AI_ROADMAPS=true
ENABLE_ASSESSMENTS=true
ENABLE_SIMULATION_MODE=true
ENABLE_LEADERBOARDS=true
ENABLE_INTERVIEWER_PROFILES=true
ENABLE_ANALYTICS=true
```

### Monitoring

```
LOG_LEVEL=info
ENABLE_METRICS=true
ENABLE_TRACING=false
```

## How to Add These in Railway

1. Go to your Railway project dashboard
2. Select your service
3. Go to "Variables" tab
4. Add each variable above
5. Redeploy the service

## Important Notes

- Change `JWT_SECRET_KEY` to a secure random string in production
- Set `ALLOWED_ORIGINS` to your actual domain in production
- Database variables will be automatically populated by Railway when you add PostgreSQL service
- PORT is automatically set by Railway
