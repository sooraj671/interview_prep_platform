"""
Interview Preparation Platform - ORM Version
Main application using SQLAlchemy ORM repositories
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import ORM session manager
from infrastructure.database.orm_session import orm_session_manager
from infrastructure.database.orm_dependencies import (
    get_user_repository, get_skill_repository, get_roadmap_repository,
    get_assessment_repository, get_analytics_repository
)

# Import API routers
from presentation.api.v1.users_orm_robust import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Interview Preparation Platform with ORM...")
    
    # Initialize database tables if needed
    try:
        await orm_session_manager.create_tables()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database tables: {e}")
    
    logger.info("✅ Application started successfully")
    yield
    
    logger.info("🛑 Shutting down Interview Preparation Platform...")
    await orm_session_manager.close()
    logger.info("✅ Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Interview Preparation Platform - ORM",
    description="AI-powered interview preparation platform with SQLAlchemy ORM",
    version="2.0.0",
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

app.router.lifespan_context = lifespan

# Include API routers
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])

# Basic endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Interview Preparation Platform API - ORM Version",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "database": "SQLAlchemy ORM with PostgreSQL"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "database": "SQLAlchemy ORM",
        "orm": "enabled"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "database": "SQLAlchemy ORM configured",
        "environment": os.getenv("APP_ENV", "development"),
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Repository test endpoints
@app.get("/test/repositories")
async def test_repositories(
    user_repo=Depends(get_user_repository),
    skill_repo=Depends(get_skill_repository),
    roadmap_repo=Depends(get_roadmap_repository),
    assessment_repo=Depends(get_assessment_repository),
    analytics_repo=Depends(get_analytics_repository)
):
    """Test repository dependencies"""
    return {
        "message": "All ORM repositories initialized successfully",
        "repositories": {
            "user": type(user_repo).__name__,
            "skill": type(skill_repo).__name__,
            "roadmap": type(roadmap_repo).__name__,
            "assessment": type(assessment_repo).__name__,
            "analytics": type(analytics_repo).__name__
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting ORM application on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
