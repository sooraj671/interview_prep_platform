"""
Interview Preparation Platform - Debug Version
With comprehensive logging to identify bottlenecks
"""

import os
import sys
import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test database connection
def test_database_connection():
    """Test database connection and log results"""
    logger.info("Testing database connection...")
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            logger.info(f"Database URL found: {database_url.split('@')[0]}@***")
            
            # Try to import database modules
            try:
                from infrastructure.database.database import DatabaseConfig
                logger.info("Database config created successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to import database modules: {e}")
                return False
        else:
            logger.warning("No DATABASE_URL found in environment")
            return False
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

# Create FastAPI app
logger.info("Creating FastAPI application...")
app = FastAPI(
    title="Interview Preparation Platform",
    description="AI-powered interview preparation platform with debugging",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
logger.info("Adding CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with detailed logging"""
    logger.info("🚀 Starting Interview Preparation Platform...")
    start_time = time.time()
    
    # Test database connection
    db_ok = test_database_connection()
    logger.info(f"Database test result: {db_ok}")
    
    # Log environment variables
    logger.info("Environment variables:")
    for key in ["DATABASE_URL", "APP_ENV", "PORT", "DEBUG"]:
        value = os.getenv(key)
        logger.info(f"  {key}: {'***' if 'PASSWORD' in key or 'SECRET' in key else value}")
    
    logger.info(f"✅ Application started successfully in {time.time() - start_time:.2f}s")
    yield
    
    logger.info("🛑 Shutting down Interview Preparation Platform...")
    logger.info("✅ Application shutdown complete")

app.router.lifespan_context = lifespan

# Basic endpoints with logging
@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint called")
    start_time = time.time()
    
    response = {
        "message": "Interview Preparation Platform API",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }
    
    elapsed = time.time() - start_time
    logger.info(f"Root endpoint response in {elapsed:.3f}s")
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed logging"""
    logger.info("Health check endpoint called")
    start_time = time.time()
    
    # Test database connection
    db_status = "configured" if os.getenv("DATABASE_URL") else "not_configured"
    db_ok = test_database_connection()
    
    response = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "database": db_status,
        "database_test": db_ok
    }
    
    elapsed = time.time() - start_time
    logger.info(f"Health check response in {elapsed:.3f}s")
    return response

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    logger.info("Readiness check endpoint called")
    start_time = time.time()
    
    response = {
        "status": "ready",
        "database": "configured" if os.getenv("DATABASE_URL") else "not_configured",
        "environment": os.getenv("APP_ENV", "development"),
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    elapsed = time.time() - start_time
    logger.info(f"Readiness check response in {elapsed:.3f}s")
    return response

# Mock users endpoints with logging
@app.get("/users")
async def get_users():
    """Get users endpoint"""
    logger.info("Users GET endpoint called")
    start_time = time.time()
    
    if os.getenv("DATABASE_URL"):
        response = {"users": [], "total": 0, "message": "Database configured - no users yet"}
    else:
        response = {"users": [], "total": 0, "message": "Database not configured"}
    
    elapsed = time.time() - start_time
    logger.info(f"Users GET response in {elapsed:.3f}s")
    return response

@app.post("/users")
async def create_user():
    """Create user endpoint"""
    logger.info("Users POST endpoint called")
    start_time = time.time()
    
    if os.getenv("DATABASE_URL"):
        response = {"message": "User creation endpoint ready", "status": "pending_database"}
    else:
        response = {"message": "User creation not available - database not configured", "status": "error"}
    
    elapsed = time.time() - start_time
    logger.info(f"Users POST response in {elapsed:.3f}s")
    return response

# Mock roadmaps endpoints with logging
@app.get("/roadmaps")
async def get_roadmaps():
    """Get roadmaps endpoint"""
    logger.info("Roadmaps GET endpoint called")
    start_time = time.time()
    
    if os.getenv("DATABASE_URL"):
        response = {"roadmaps": [], "total": 0, "message": "Database configured - no roadmaps yet"}
    else:
        response = {"roadmaps": [], "total": 0, "message": "Database not configured"}
    
    elapsed = time.time() - start_time
    logger.info(f"Roadmaps GET response in {elapsed:.3f}s")
    return response

@app.post("/roadmaps")
async def create_roadmap():
    """Create roadmap endpoint"""
    logger.info("Roadmaps POST endpoint called")
    start_time = time.time()
    
    if os.getenv("DATABASE_URL"):
        response = {"message": "Roadmap creation endpoint ready", "status": "pending_database"}
    else:
        response = {"message": "Roadmap creation not available - database not configured", "status": "error"}
    
    elapsed = time.time() - start_time
    logger.info(f"Roadmaps POST response in {elapsed:.3f}s")
    return response

if __name__ == "__main__":
    logger.info("Starting application...")
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Port: {port}")
    
    import uvicorn
    logger.info("Starting uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
