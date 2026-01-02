from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, users, profiles, skills, roadmaps, assessments
import os

app = FastAPI(
    title="Interview Preparation Platform",
    description="AI-powered interview preparation platform with personalized learning roadmaps, assessments, and interview simulations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS for API documentation access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["Skills"])
app.include_router(roadmaps.router, prefix="/api/v1/roadmaps", tags=["Roadmaps"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    
    Returns basic API information
    """
    return {
        "message": "Interview Preparation Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint
    
    Returns API health status
    """
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
