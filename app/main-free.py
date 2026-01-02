import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config import settings
from app.core.exceptions import AppException
from app.api.v1 import auth, users, profiles, skills, roadmaps, assessments
from app.ai.free_llm_client import get_free_llm_client
from app.ai.free_embedding_client import get_free_embedding_client

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global variables for AI clients
llm_client = None
embedding_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global llm_client, embedding_client
    
    # Startup
    logger.info("Starting Interview Preparation Platform")
    
    try:
        # Initialize free AI clients
        llm_client = get_free_llm_client()
        embedding_client = get_free_embedding_client()
        
        # Warm up AI services
        await llm_client.warm_up()
        await embedding_client.warm_up()
        
        logger.info("AI services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI services: {e}")
        # Continue without AI services for basic functionality
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    if llm_client:
        await llm_client.close()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered interview preparation platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    logger.error(f"Application error: {exc.message}", extra={"error_code": exc.error_code})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "error_code": exc.error_code}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["profiles"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["skills"])
app.include_router(roadmaps.router, prefix="/api/v1/roadmaps", tags=["roadmaps"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["assessments"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": "1.0.0"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Interview Preparation Platform API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
