"""
Robust Main Application with All APIs
Gracefully handles missing modules and loads available APIs
"""
import os
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Create FastAPI app
app = FastAPI(
    title="Interview Preparation Platform",
    description="AI-powered interview preparation platform with full API coverage",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for modules
modules_loaded = {}

# Try to load configuration
try:
    from config.settings import config_loader
    settings = config_loader.load_config()
    modules_loaded['config'] = True
except ImportError as e:
    print(f"Config loading failed: {e}")
    settings = None
    modules_loaded['config'] = False

# Try to load database
try:
    # Test if we can import and use the database connection
    from infrastructure.database.simple_connection import test_database_connection
    modules_loaded['database'] = True
    print("✅ Database module loaded (simple connection)")
except ImportError as e:
    print(f"Database loading failed: {e}")
    modules_loaded['database'] = False

# Try to load AI (simplified)
try:
    import httpx
    modules_loaded['ai'] = True
except ImportError as e:
    print(f"AI loading failed: {e}")
    modules_loaded['ai'] = False

# Try to load auth
try:
    from presentation.api import auth_router
    modules_loaded['auth'] = True
except ImportError as e:
    print(f"Auth loading failed: {e}")
    modules_loaded['auth'] = False

# Try to load users
try:
    from presentation.api import users_router
    modules_loaded['users'] = True
except ImportError as e:
    print(f"Users loading failed: {e}")
    modules_loaded['users'] = False

# Try to load skills
try:
    from presentation.api import skills_router
    modules_loaded['skills'] = True
except ImportError as e:
    print(f"Skills loading failed: {e}")
    modules_loaded['skills'] = False

# Try to load assessments
try:
    from presentation.api import assessments_router
    modules_loaded['assessments'] = True
except ImportError as e:
    print(f"Assessments loading failed: {e}")
    modules_loaded['assessments'] = False

# Try to load roadmaps
try:
    from presentation.api import roadmaps_router
    modules_loaded['roadmaps'] = True
except ImportError as e:
    print(f"Roadmaps loading failed: {e}")
    modules_loaded['roadmaps'] = False

# Try to load analytics
try:
    from presentation.api import analytics_router
    modules_loaded['analytics'] = True
except ImportError as e:
    print(f"Analytics loading failed: {e}")
    modules_loaded['analytics'] = False

# Try to load database test
try:
    from presentation.api import database_test_router
    modules_loaded['database_test'] = True
except ImportError as e:
    print(f"Database test loading failed: {e}")
    modules_loaded['database_test'] = False

# Try to load AI test
try:
    from presentation.api import ai_test_router
    modules_loaded['ai_test'] = True
except ImportError as e:
    print(f"AI test loading failed: {e}")
    modules_loaded['ai_test'] = False

# Include routers that loaded successfully
if modules_loaded.get('auth'):
    app.include_router(auth_router, tags=["Authentication"])
    print("✅ Auth API loaded")

if modules_loaded.get('users'):
    app.include_router(users_router, tags=["Users"])
    print("✅ Users API loaded")

if modules_loaded.get('skills'):
    app.include_router(skills_router, tags=["Skills"])
    print("✅ Skills API loaded")

if modules_loaded.get('assessments'):
    app.include_router(assessments_router, tags=["Assessments"])
    print("✅ Assessments API loaded")

if modules_loaded.get('roadmaps'):
    app.include_router(roadmaps_router, tags=["Roadmaps"])
    print("✅ Roadmaps API loaded")

if modules_loaded.get('analytics'):
    app.include_router(analytics_router, tags=["Analytics"])
    print("✅ Analytics API loaded")

if modules_loaded.get('database_test'):
    app.include_router(database_test_router, tags=["Database Testing"])
    print("✅ Database Test API loaded")

if modules_loaded.get('ai_test'):
    app.include_router(ai_test_router, tags=["AI Testing"])
    print("✅ AI Test API loaded")

# Basic endpoints
@app.get("/")
async def root():
    """Root endpoint with module status"""
    return {
        "message": "Interview Preparation Platform API",
        "status": "running",
        "version": "1.0.0",
        "modules_loaded": modules_loaded,
        "api_endpoints": {
            "auth": "/auth" if modules_loaded.get('auth') else None,
            "users": "/users" if modules_loaded.get('users') else None,
            "skills": "/skills" if modules_loaded.get('skills') else None,
            "assessments": "/assessments" if modules_loaded.get('assessments') else None,
            "roadmaps": "/roadmaps" if modules_loaded.get('roadmaps') else None,
            "analytics": "/analytics" if modules_loaded.get('analytics') else None,
            "database_test": "/database" if modules_loaded.get('database_test') else None,
            "ai_test": "/ai" if modules_loaded.get('ai_test') else None,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if modules_loaded.get('database') else "not available",
        "ai_service": "inference.net" if modules_loaded.get('ai') else "not available",
        "modules_loaded": sum(modules_loaded.values()),
        "total_modules": len(modules_loaded)
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "database": os.getenv("DB_NAME", "not configured"),
        "ai_service": "inference.net",
        "environment": os.getenv("APP_ENV", "development")
    }

# Module status endpoint
@app.get("/modules")
async def module_status():
    """Get status of all loaded modules"""
    return {
        "modules": modules_loaded,
        "loaded_count": sum(modules_loaded.values()),
        "total_count": len(modules_loaded)
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Interview Preparation Platform...")
    
    # Test database connection during startup
    print("🔍 [STARTUP] Testing database connection...")
    try:
        from infrastructure.database.simple_connection import test_database_connection
        db_result = test_database_connection()
        print(f"📊 [STARTUP] Database test result: {db_result.get('status')}")
        if db_result.get('status') == 'connected':
            print(f"✅ [STARTUP] Database connected successfully! Found {db_result.get('table_count', 0)} tables")
        else:
            print(f"❌ [STARTUP] Database connection failed: {db_result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ [STARTUP] Database test exception: {str(e)}")
    
    # Quick startup without blocking operations
    print(f"📊 Modules loaded: {sum(modules_loaded.values())}/{len(modules_loaded)}")
    print("✅ Application started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Interview Preparation Platform...")

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
