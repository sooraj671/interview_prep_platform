"""
Interview Preparation Platform - Simple Working Version
Minimal FastAPI app for Railway deployment
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Create FastAPI app
app = FastAPI(
    title="Interview Preparation Platform",
    description="AI-powered interview preparation platform",
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simple lifespan manager"""
    print("🚀 Starting Interview Preparation Platform...")
    print("✅ Application started successfully")
    yield
    print("🛑 Shutting down Interview Preparation Platform...")
    print("✅ Application shutdown complete")

app.router.lifespan_context = lifespan

# Basic endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Interview Preparation Platform API",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "database": "not_configured"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "database": "not_configured",
        "environment": os.getenv("APP_ENV", "development"),
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Simple users endpoint (without database)
@app.get("/users")
async def get_users():
    """Get users endpoint (mock)"""
    return {
        "users": [],
        "total": 0,
        "message": "Database not configured - returning empty list"
    }

@app.post("/users")
async def create_user():
    """Create user endpoint (mock)"""
    return {
        "message": "User creation not available - database not configured",
        "status": "error"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
