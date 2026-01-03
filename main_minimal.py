"""
Minimal FastAPI Application for Railway Deployment
This version works without the complex imports
"""
import os
from fastapi import FastAPI

# Create minimal FastAPI app
app = FastAPI(
    title="Interview Preparation Platform",
    description="AI-powered interview preparation platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Interview Preparation Platform API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/docs")
async def docs():
    """API docs redirect"""
    return {
        "message": "API documentation available at /docs",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
