from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/ping", tags=["Health"])
async def ping():
    """
    Simple ping endpoint
    
    Returns pong for connectivity testing
    """
    return {"pong": True, "timestamp": "2024-01-01"}

# Sample API endpoints for demonstration
@app.get("/api/v1/users", tags=["Users"])
async def get_users():
    """
    Get all users
    
    Returns a list of users (sample endpoint)
    """
    return {
        "users": [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
    }

@app.get("/api/v1/skills", tags=["Skills"])
async def get_skills():
    """
    Get all skills
    
    Returns available skills for assessment (sample endpoint)
    """
    return {
        "skills": [
            {"id": 1, "name": "Python", "category": "Programming"},
            {"id": 2, "name": "JavaScript", "category": "Programming"},
            {"id": 3, "name": "SQL", "category": "Database"},
            {"id": 4, "name": "Communication", "category": "Soft Skills"}
        ]
    }

@app.get("/api/v1/roadmaps", tags=["Roadmaps"])
async def get_roadmaps():
    """
    Get learning roadmaps
    
    Returns available learning roadmaps (sample endpoint)
    """
    return {
        "roadmaps": [
            {"id": 1, "title": "Full Stack Developer", "duration": "12 weeks"},
            {"id": 2, "title": "Data Scientist", "duration": "16 weeks"},
            {"id": 3, "title": "DevOps Engineer", "duration": "10 weeks"}
        ]
    }

@app.get("/api/v1/assessments", tags=["Assessments"])
async def get_assessments():
    """
    Get assessments
    
    Returns available assessments (sample endpoint)
    """
    return {
        "assessments": [
            {"id": 1, "title": "Python Fundamentals", "type": "technical"},
            {"id": 2, "title": "Problem Solving", "type": "analytical"},
            {"id": 3, "title": "Communication Skills", "type": "behavioral"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
