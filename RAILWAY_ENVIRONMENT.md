# 🚀 Railway Environment Variables - Copy Paste Ready

## 📋 **ALL ENVIRONMENT VARIABLES FOR RAILWAY DASHBOARD**

### **🔧 Application Settings**

```
APP_NAME=Interview Preparation Platform
APP_VERSION=1.0.0
APP_ENV=production
DEBUG=false
PORT=8000
```

### **🔐 Authentication & Security**

```
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production_make_it_long_and_random
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### **🤖 AI/LLM Configuration (Ollama)**

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=30
OLLAMA_MAX_RETRIES=3
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
```

### **🗄️ Database Configuration**

```
DATABASE_URL=${RAILWAY_POSTGRES_URL}
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_ECHO=false
```

### **🔴 Cache Configuration**

```
REDIS_URL=${RAILWAY_REDIS_URL}
CACHE_DEFAULT_TTL=3600
```

### **🌐 CORS & Network**

```
ALLOWED_ORIGINS=*
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*
```

### **🔑 OAuth Providers (Get these from provider dashboards)**

```
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here

MICROSOFT_CLIENT_ID=your_microsoft_client_id_here
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret_here

LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
```

### **🚀 Feature Flags**

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

### **📊 Monitoring & Logging**

```
LOG_LEVEL=info
ENABLE_METRICS=true
ENABLE_TRACING=false
```

---

## 🎯 **QUICK COPY PASTE BLOCK**

### **Copy this entire block and paste into Railway Dashboard Variables:**

```
APP_NAME=Interview Preparation Platform
APP_VERSION=1.0.0
APP_ENV=production
DEBUG=false
PORT=8000
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production_make_it_long_and_random
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=30
OLLAMA_MAX_RETRIES=3
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
DATABASE_URL=${RAILWAY_POSTGRES_URL}
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_ECHO=false
REDIS_URL=${RAILWAY_REDIS_URL}
CACHE_DEFAULT_TTL=3600
ALLOWED_ORIGINS=*
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*
ENABLE_OAUTH_LOGIN=true
ENABLE_RESUME_UPLOAD=true
ENABLE_AI_ROADMAPS=true
ENABLE_ASSESSMENTS=true
ENABLE_SIMULATION_MODE=true
ENABLE_LEADERBOARDS=true
ENABLE_INTERVIEWER_PROFILES=true
ENABLE_ANALYTICS=true
LOG_LEVEL=info
ENABLE_METRICS=true
ENABLE_TRACING=false
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
MICROSOFT_CLIENT_ID=your_microsoft_client_id_here
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret_here
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
```

---

## 🔧 **Ollama Configuration**

### **For Local Ollama:**

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### **For Remote Ollama (if you host it elsewhere):**

```
OLLAMA_BASE_URL=https://your-ollama-server.com
OLLAMA_MODEL=llama2
```

### **Available Ollama Models:**

- `llama2` (default)
- `codellama` (for coding questions)
- `mistral` (faster responses)
- `vicuna` (good for interviews)

---

## 🗄️ **Database Setup**

### **Railway PostgreSQL:**

- Automatically available as `${RAILWAY_POSTGRES_URL}`
- No additional setup needed
- Connection string will be auto-populated

### **Manual PostgreSQL (if needed):**

```
DATABASE_URL=postgresql://username:password@host:port/database
```

---

## 🔴 **Redis Cache**

### **Railway Redis:**

- Automatically available as `${RAILWAY_REDIS_URL}`
- No additional setup needed
- Connection string will be auto-populated

### **Manual Redis (if needed):**

```
REDIS_URL=redis://username:password@host:port
```

---

## 🎉 **After Setting Variables:**

1. **Deploy your app**: `railway up`
2. **Set port to**: `8000`
3. **Test endpoints**: `https://your-app.railway.app/health`
4. **View API docs**: `https://your-app.railway.app/docs`

---

## 🚨 **Important Notes:**

### **Security:**

- Change `JWT_SECRET_KEY` to something random and long
- Get real OAuth client IDs and secrets from provider dashboards
- Don't expose sensitive values in logs

### **Ollama:**

- Make sure your Ollama server is accessible from Railway
- For local development, use `http://localhost:11434`
- For production, consider hosting Ollama on a cloud server

### **Database:**

- Railway PostgreSQL is automatically configured
- `${RAILWAY_POSTGRES_URL}` will be auto-populated
- No manual database setup needed for basic functionality

**Copy the environment variables block above and paste into Railway Dashboard! 🚀**
