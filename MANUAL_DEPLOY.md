# 🚀 Manual Railway Deployment Guide

## ⚠️ **Issues You're Facing:**

1. **Free tier resource limit exceeded** - Railway has limits on free tier
2. **CLI commands changed** - `railway variables set` doesn't work anymore
3. **Interactive prompts failing** - Script can't handle interactive CLI

## 🎯 **SOLUTION: Manual Deployment**

### **Step 1: Use Existing Project**

You already have a project: `awake-analysis`

```bash
cd /Users/soorajkumar/CascadeProjects/interview_prep_platform
```

### **Step 2: Deploy Your App**

```bash
railway up
```

When it asks "Select a service", choose your main app (NOT Postgres or Redis)

### **Step 3: Set Environment Variables Manually**

Go to Railway Dashboard → Variables → Add these:

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

### **Step 4: Add Database (If Needed)**

If you don't have PostgreSQL:

1. Railway Dashboard → New Service → Database → PostgreSQL
2. Wait for it to be ready
3. Go to Variables → Add: `DATABASE_URL=${RAILWAY_POSTGRES_URL}`

### **Step 5: Test Your App**

Wait 2-3 minutes, then visit:

- Your app URL: `https://awake-analysis.railway.app`
- Health check: `https://awake-analysis.railway.app/health`
- API docs: `https://awake-analysis.railway.app/docs`

---

## 🔧 **If You Want a New Project**

### **Option 1: Delete and Recreate**

```bash
# Delete current project
railway projects delete awake-analysis

# Create new one
railway init
```

### **Option 2: Use Different Workspace**

```bash
# Switch to different workspace
railway link

# Then deploy
railway up
```

---

## 📱 **Quick Commands**

### **Check Deployment Status**

```bash
railway status
```

### **View Logs**

```bash
railway logs
```

### **Get Your App URL**

```bash
railway domain
```

### **Run Commands**

```bash
# Test database connection
railway run 'python -c "print(\"Hello World\")"'
```

---

## 🎯 **What to Do Right Now**

### **1. Deploy Your App**

```bash
railway up
```

Select your main app (not Postgres/Redis)

### **2. Add Environment Variables**

Go to Railway Dashboard → Variables → Add the variables listed above

### **3. Test Your App**

Visit: `https://awake-analysis.railway.app/health`

### **4. If It Works**

Visit: `https://awake-analysis.railway.app/docs`

---

## 🚨 **Troubleshooting**

### **If Deployment Fails**

```bash
# Check logs
railway logs

# Redeploy
railway up
```

### **If App Crashes**

1. Check environment variables
2. Check logs in Railway Dashboard
3. Make sure all required variables are set

### **If You Need Database**

1. Railway Dashboard → New Service → Database → PostgreSQL
2. Add `DATABASE_URL=${RAILWAY_POSTGRES_URL}` to Variables

---

## 🎉 **Expected Result**

Your app should be running at:

- **Main App**: `https://awake-analysis.railway.app`
- **API Docs**: `https://awake-analysis.railway.app/docs`
- **Health**: `https://awake-analysis.railway.app/health`

**Just follow the manual steps above! 🚀**
