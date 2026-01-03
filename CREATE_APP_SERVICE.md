# 🚀 Create Main Application Service

## 🎯 **The Problem**

You only have PostgreSQL and Redis services, but no main application service to deploy your code.

## 🔧 **Solution: Create Main Application Service**

### **Step 1: Add Empty Service**

```bash
railway add
```

When it asks "What do you need?", select:

- **Empty Service** (not GitHub Repo, Database, or Docker Image)

### **Step 2: Configure the Service**

Give it a name like:

- **api** or **app** or **interview-platform**

### **Step 3: Deploy Your Code**

Now when you run:

```bash
railway up
```

You should see:

```
? Select a service
> api              (your main app)
  Postgres
  Redis
```

Select your **main app service** (api/app), not Postgres or Redis.

---

## 🎯 **Complete Steps**

### **1. Create Main Service**

```bash
railway add
# Select "Empty Service"
# Name it "api" or "app"
```

### **2. Deploy Your Code**

```bash
railway up
# Select your main app service (not Postgres/Redis)
```

### **3. Add Environment Variables**

Go to Railway Dashboard → Your App Service → Variables → Add:

```
APP_NAME=Interview Preparation Platform
APP_VERSION=1.0.0
APP_ENV=production
DEBUG=false
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
ALLOWED_ORIGINS=*
ENABLE_OAUTH_LOGIN=true
ENABLE_RESUME_UPLOAD=true
ENABLE_AI_ROADMAPS=true
ENABLE_ASSESSMENTS=true
ENABLE_SIMULATION_MODE=true
ENABLE_LEADERBOARDS=true
ENABLE_INTERVIEWER_PROFILES=true
ENABLE_ANALYTICS=true
LOG_LEVEL=info
```

### **4. Add Database Connection**

Also add:

```
DATABASE_URL=${RAILWAY_POSTGRES_URL}
REDIS_URL=${RAILWAY_REDIS_URL}
```

### **5: Test Your App**

Wait 2-3 minutes, then visit:

- Your app URL: `https://your-service-name.railway.app`
- Health check: `https://your-service-name.railway.app/health`
- API docs: `https://your-service-name.railway.app/docs`

---

## 🔍 **What You Should See**

After creating the main service, `railway up` should show:

```
? Select a service
> api              (your main app - SELECT THIS)
  Postgres
  Redis
```

NOT just Postgres and Redis.

---

## 🚨 **If Still Issues**

### **Check Your Services**

```bash
railway status
```

### **View All Services**

```bash
railway services
```

### **Start Fresh**

```bash
# Create new project
railway init

# Add main service first
railway add
# Select "Empty Service"

# Then add database
railway add
# Select "Database" → "PostgreSQL"

# Then deploy
railway up
```

---

## 🎉 **Expected Result**

You should have 3 services:

1. **api/app** (your main application)
2. **Postgres** (database)
3. **Redis** (cache)

And your main app should be running at `https://your-service-name.railway.app`

**Create the main service first, then deploy! 🚀**
