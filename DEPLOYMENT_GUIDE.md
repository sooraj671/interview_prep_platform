# Interview Preparation Platform - Deployment Guide

## Overview

This guide covers deploying the Interview Preparation Platform with PostgreSQL database and Inference.net AI integration.

## Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis (optional, for caching)
- Docker and Docker Compose (recommended)

## Environment Configuration

Create a `.env` file in the project root:

```bash
# Application Settings
APP_NAME=Interview Preparation Platform
APP_VERSION=1.0.0
APP_ENV=production
DEBUG=false

# Database Settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=interview_prep
DB_USER=postgres
DB_PASSWORD=your_password_here

# AI Settings (Inference.net)
INFERENCE_API_KEY=inference-7879a8ca800d4e39a0395f057f407f90
INFERENCE_BASE_URL=https://api.inference.net/v1
INFERENCE_MODEL=google/gemma-3-27b-instruct/bf-16
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
AI_REQUEST_TIMEOUT=60
AI_MAX_RETRIES=3

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

# Feature Flags
ENABLE_OAUTH_LOGIN=true
ENABLE_RESUME_UPLOAD=true
ENABLE_AI_ROADMAPS=true
ENABLE_ASSESSMENTS=true
ENABLE_SIMULATION_MODE=true
ENABLE_LEADERBOARDS=true
ENABLE_INTERVIEWER_PROFILES=true
ENABLE_ANALYTICS=true

# Monitoring
LOG_LEVEL=info
ENABLE_METRICS=true
ENABLE_TRACING=false
```

## Database Setup

### 1. Create PostgreSQL Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE interview_prep;

-- Create user (optional)
CREATE USER interview_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE interview_prep TO interview_user;
```

### 2. Run Database Schema

```bash
# Apply the schema
psql -U postgres -d interview_prep -f database_schema.sql
```

### 3. Verify Schema

```sql
-- Check tables
\dt

-- Check users table structure
\d users
```

## Installation

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Application

```bash
# Development mode
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker Deployment

### 1. Docker Compose

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=interview_prep
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=interview_prep
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database_schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 2. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## Cloud Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Railway will automatically detect and deploy the FastAPI application

### Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables
4. Deploy

### AWS/Google Cloud

Use the provided Docker configuration for deployment to cloud platforms.

## Monitoring and Logging

### Health Checks

- `GET /health` - Basic health check
- `GET /ready` - Readiness check (includes database)

### Metrics

The application exposes metrics at `/metrics` when `ENABLE_METRICS=true`.

### Logging

Structured logging is enabled. Logs include:

- Request ID
- User ID (when authenticated)
- Timestamp
- Log level
- Message

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **Database**: Use strong passwords and SSL connections
3. **API Keys**: Rotate Inference.net API keys regularly
4. **JWT**: Use strong secret keys and appropriate expiration times
5. **CORS**: Configure allowed origins properly
6. **HTTPS**: Always use HTTPS in production

## Performance Optimization

1. **Database**: Use connection pooling (configured in settings)
2. **Caching**: Enable Redis for session storage and caching
3. **CDN**: Use CDN for static assets
4. **Load Balancing**: Use multiple workers behind a load balancer

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U postgres -h localhost -p 5432 -d interview_prep

# Check logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### AI Service Issues

```bash
# Test Inference.net API
curl -X POST https://api.inference.net/v1/chat/completions \
  -H "Authorization: Bearer inference-7879a8ca800d4e39a0395f057f407f90" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemma-3-27b-instruct/bf-16",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

### Application Logs

```bash
# View application logs
docker-compose logs -f app

# Or if running directly
tail -f logs/app.log
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
pg_dump -U postgres -h localhost interview_prep > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql -U postgres -h localhost interview_prep < backup_20231201_120000.sql
```

### Automated Backups

Set up automated backups using cron or cloud provider tools.

## Scaling

### Horizontal Scaling

- Use multiple application instances behind a load balancer
- Ensure all instances connect to the same database and Redis

### Database Scaling

- Read replicas for read-heavy workloads
- Connection pooling
- Database optimization based on query patterns

## Maintenance

### Regular Tasks

1. Update dependencies
2. Monitor database performance
3. Check AI API usage and costs
4. Review and rotate secrets
5. Update SSL certificates

### Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Migrate database (if schema changes)
# Run migration scripts as needed

# Restart application
docker-compose restart app
```

## Support

For issues and support:

1. Check application logs
2. Verify environment configuration
3. Test database connectivity
4. Validate AI API access
5. Review this troubleshooting guide
