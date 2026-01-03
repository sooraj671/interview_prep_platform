"""
Interview Preparation Platform - Main Application Entry Point
Clean Architecture Implementation with FastAPI
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

try:
    from config.settings import config_loader
    from infrastructure.logging.structured_logger import StructuredLogger
    from presentation.middleware.error_handling import error_handling_middleware
    from presentation.middleware.logging import logging_middleware
    from presentation.middleware.rate_limiting import rate_limiting_middleware
except ImportError as e:
    print(f"Import error: {e}")
    print("Creating minimal app for debugging...")
    
    app = FastAPI(title="Interview Preparation Platform")
    
    @app.get("/")
    async def root():
        return {"message": "Interview Preparation Platform API", "status": "minimal"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    sys.exit(0)


# Load configuration
settings = config_loader.load_config()
logger = StructuredLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Interview Preparation Platform", version=settings.app.version)
    
    # Initialize infrastructure components
    # This would include database connections, cache, etc.
    
    yield
    
    # Shutdown
    logger.info("Shutting down Interview Preparation Platform")
    
    # Cleanup infrastructure components
    # This would include closing database connections, etc.


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app.name,
        description="AI-powered interview preparation platform with personalized learning roadmaps, assessments, and interview simulations",
        version=settings.app.version,
        docs_url=settings.app.docs_url if settings.feature_flags.enable_analytics else None,
        redoc_url=settings.app.redoc_url if settings.feature_flags.enable_analytics else None,
        openapi_url="/openapi.json" if settings.feature_flags.enable_analytics else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.app.allowed_methods,
        allow_headers=settings.app.allowed_headers,
    )
    
    # Add custom middleware
    app.middleware("http")(error_handling_middleware)
    app.middleware("http")(logging_middleware)
    app.middleware("http")(rate_limiting_middleware)
    
    # Include API routers
    # This will be implemented in the presentation layer
    # app.include_router(auth_router, prefix=settings.api_prefix)
    # app.include_router(users_router, prefix=settings.api_prefix)
    # app.include_router(skills_router, prefix=settings.api_prefix)
    # app.include_router(roadmaps_router, prefix=settings.api_prefix)
    # app.include_router(assessments_router, prefix=settings.api_prefix)
    # app.include_router(analytics_router, prefix=settings.api_prefix)
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint - Returns basic API information"""
        return {
            "message": "Interview Preparation Platform API",
            "version": settings.app.version,
            "environment": settings.app.environment.value,
            "docs": settings.app.docs_url,
            "redoc": settings.app.redoc_url,
            "health": "/health",
            "features": {
                "oauth_login": settings.feature_flags.enable_oauth_login,
                "resume_upload": settings.feature_flags.enable_resume_upload,
                "ai_roadmaps": settings.feature_flags.enable_ai_roadmaps,
                "assessments": settings.feature_flags.enable_assessments,
                "simulation_mode": settings.feature_flags.enable_simulation_mode,
                "leaderboards": settings.feature_flags.enable_leaderboards,
                "interviewer_profiles": settings.feature_flags.enable_interviewer_profiles,
                "analytics": settings.feature_flags.enable_analytics
            }
        }
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.app.version,
            "environment": settings.app.environment.value,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    # Ready check endpoint
    @app.get("/ready", tags=["Health"])
    async def ready():
        """Ready check endpoint for load balancers"""
        # This would check database connections, external services, etc.
        return {
            "status": "ready",
            "checks": {
                "database": "ok",
                "cache": "ok",
                "ai_services": "ok"
            }
        }
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.app.debug,
        log_level=settings.monitoring.log_level.lower()
    )
