"""
Main Application - SQLAlchemy ORM Version
FastAPI application with SQLAlchemy ORM and Clean Architecture
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

# Global variables
sqlalchemy_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Interview Preparation Platform with SQLAlchemy ORM...")
    
    try:
        # Load configuration
        from config.settings import get_settings
        settings = get_settings()
        print("✅ Configuration loaded")
        
        # Initialize SQLAlchemy
        from infrastructure.database.sqlalchemy_connection import get_sqlalchemy_manager
        global sqlalchemy_manager
        sqlalchemy_manager = await get_sqlalchemy_manager(settings)
        print("✅ SQLAlchemy initialized")
        
        # Test database connection
        from infrastructure.database.sqlalchemy_connection import get_db_session
        async with get_db_session() as session:
            result = await session.execute("SELECT 1")
            print("✅ Database connection verified")
        
        print("✅ Application startup complete")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🔄 Shutting down application...")
    try:
        if sqlalchemy_manager:
            await sqlalchemy_manager.close()
        print("✅ Application shutdown complete")
    except Exception as e:
        print(f"❌ Shutdown error: {e}")

# Create FastAPI app
app = FastAPI(
    title="Interview Preparation Platform - ORM Version",
    description="AI-powered interview preparation platform with SQLAlchemy ORM",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if app.debug else "Something went wrong"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        from infrastructure.database.sqlalchemy_connection import get_db_session
        async with get_db_session() as session:
            result = await session.execute("SELECT 1")
            
        return {
            "status": "healthy",
            "database": "connected",
            "orm": "sqlalchemy",
            "version": "2.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Interview Preparation Platform - ORM Version",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include API routers
try:
    from presentation.api.v1.users_orm import router as users_router
    app.include_router(users_router)
    print("✅ Users API loaded (ORM version)")
except ImportError as e:
    print(f"❌ Failed to load Users API: {e}")

# Load additional routers if they exist
additional_routers = [
    ("auth", "Authentication API"),
    ("skills", "Skills API"),
    ("assessments", "Assessments API"),
    ("roadmaps", "Roadmaps API"),
    ("analytics", "Analytics API"),
    ("ai_test", "AI Test API")
]

for router_name, description in additional_routers:
    try:
        router_module = __import__(f"presentation.api.v1.{router_name}", fromlist=["router"])
        if hasattr(router_module, "router"):
            app.include_router(router_module.router)
            print(f"✅ {description} loaded")
    except ImportError:
        print(f"⚠️ {description} not available")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_orm:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
