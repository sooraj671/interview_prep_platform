from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from uuid import uuid4
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

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "candidate"

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool = True
    created_at: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserResponse

class SkillCreate(BaseModel):
    name: str
    description: str
    category: str
    difficulty_level: str

class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    difficulty_level: str
    created_at: str

class RoadmapCreate(BaseModel):
    title: str
    target_role: str
    current_skills: List[str]
    experience_level: str
    time_commitment: str

class RoadmapResponse(BaseModel):
    id: str
    title: str
    description: str
    target_role: str
    duration_weeks: int
    difficulty_level: str
    status: str
    progress_percentage: int
    created_at: str

class AssessmentCreate(BaseModel):
    title: str
    type: str
    skill_ids: List[str]
    difficulty: str
    duration_minutes: int

class AssessmentResponse(BaseModel):
    id: str
    title: str
    type: str
    status: str
    score: Optional[int] = None
    created_at: str

# In-memory storage (for demo purposes)
users_db = {}
skills_db = {}
roadmaps_db = {}
assessments_db = {}

# Sample data
skills_db = {
    "skill-1": {
        "id": "skill-1",
        "name": "Python",
        "description": "Programming language for web development, data science, and automation",
        "category": "Programming",
        "difficulty_level": "intermediate",
        "created_at": "2024-01-01T00:00:00Z"
    },
    "skill-2": {
        "id": "skill-2",
        "name": "JavaScript",
        "description": "Web programming language for frontend and backend development",
        "category": "Programming",
        "difficulty_level": "intermediate",
        "created_at": "2024-01-01T00:00:00Z"
    },
    "skill-3": {
        "id": "skill-3",
        "name": "SQL",
        "description": "Database query language",
        "category": "Database",
        "difficulty_level": "beginner",
        "created_at": "2024-01-01T00:00:00Z"
    }
}

# Root endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - Returns basic API information"""
    return {
        "message": "Interview Preparation Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint"""
    return {"pong": True, "timestamp": "2024-01-01"}

# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=UserResponse, tags=["Authentication"])
async def register(user_data: UserCreate):
    """Register a new user"""
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "role": user_data.role,
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }
    users_db[user_id] = user
    return user

@app.post("/api/v1/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(login_data: LoginRequest):
    """Login user and return tokens"""
    # Find user by email
    user = None
    for u in users_db.values():
        if u["email"] == login_data.email:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate mock tokens
    access_token = f"mock_access_token_{uuid4()}"
    refresh_token = f"mock_refresh_token_{uuid4()}"
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user": user
    }

@app.post("/api/v1/auth/refresh", tags=["Authentication"])
async def refresh_token():
    """Refresh access token"""
    return {
        "access_token": f"mock_access_token_{uuid4()}",
        "token_type": "bearer",
        "expires_in": 3600
    }

@app.post("/api/v1/auth/logout", tags=["Authentication"])
async def logout():
    """Logout user"""
    return {"message": "Successfully logged out"}

# User endpoints
@app.get("/api/v1/users/me", response_model=UserResponse, tags=["Users"])
async def get_current_user():
    """Get current user profile"""
    # Mock user data
    return {
        "id": "user-1",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "candidate",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }

@app.put("/api/v1/users/me", response_model=UserResponse, tags=["Users"])
async def update_current_user(user_data: dict):
    """Update current user profile"""
    # Mock updated user
    return {
        "id": "user-1",
        "email": "john.doe@example.com",
        "first_name": user_data.get("first_name", "John"),
        "last_name": user_data.get("last_name", "Doe"),
        "role": "candidate",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }

@app.post("/api/v1/users/me/change-password", tags=["Users"])
async def change_password(password_data: dict):
    """Change user password"""
    return {"message": "Password changed successfully"}

# Skills endpoints
@app.get("/api/v1/skills", response_model=List[SkillResponse], tags=["Skills"])
async def get_skills(skip: int = 0, limit: int = 100, category: str = None, search: str = None):
    """Get all skills with optional filtering"""
    skills = list(skills_db.values())
    
    # Apply filters
    if category:
        skills = [s for s in skills if s["category"] == category]
    if search:
        skills = [s for s in skills if search.lower() in s["name"].lower()]
    
    # Apply pagination
    return skills[skip:skip + limit]

@app.get("/api/v1/skills/{skill_id}", response_model=SkillResponse, tags=["Skills"])
async def get_skill(skill_id: str):
    """Get skill by ID"""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skills_db[skill_id]

@app.post("/api/v1/skills", response_model=SkillResponse, tags=["Skills"])
async def create_skill(skill_data: SkillCreate):
    """Create a new skill"""
    skill_id = str(uuid4())
    skill = {
        "id": skill_id,
        "name": skill_data.name,
        "description": skill_data.description,
        "category": skill_data.category,
        "difficulty_level": skill_data.difficulty_level,
        "created_at": "2024-01-01T00:00:00Z"
    }
    skills_db[skill_id] = skill
    return skill

@app.put("/api/v1/skills/{skill_id}", response_model=SkillResponse, tags=["Skills"])
async def update_skill(skill_id: str, skill_data: dict):
    """Update skill"""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill = skills_db[skill_id]
    for key, value in skill_data.items():
        if key in skill:
            skill[key] = value
    
    return skill

@app.delete("/api/v1/skills/{skill_id}", tags=["Skills"])
async def delete_skill(skill_id: str):
    """Delete skill"""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    del skills_db[skill_id]
    return {"message": "Skill deleted successfully"}

@app.get("/api/v1/skills/domains", tags=["Skills"])
async def get_domains():
    """Get skill domains"""
    return [
        {"id": "domain-1", "name": "Software Development", "description": "Programming and software engineering"},
        {"id": "domain-2", "name": "Data Science", "description": "Data analysis and machine learning"},
        {"id": "domain-3", "name": "Soft Skills", "description": "Communication and interpersonal skills"}
    ]

# Roadmaps endpoints
@app.get("/api/v1/roadmaps", response_model=List[RoadmapResponse], tags=["Roadmaps"])
async def get_my_roadmaps():
    """Get user's roadmaps"""
    return [
        {
            "id": "roadmap-1",
            "title": "Full Stack Developer Roadmap",
            "description": "Complete roadmap to become a full stack developer",
            "target_role": "Full Stack Developer",
            "duration_weeks": 12,
            "difficulty_level": "intermediate",
            "status": "in_progress",
            "progress_percentage": 35,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]

@app.post("/api/v1/roadmaps", response_model=RoadmapResponse, tags=["Roadmaps"])
async def create_roadmap(roadmap_data: RoadmapCreate):
    """Create a new roadmap"""
    roadmap_id = str(uuid4())
    roadmap = {
        "id": roadmap_id,
        "title": roadmap_data.title,
        "description": f"Personalized learning path for becoming a {roadmap_data.target_role}",
        "target_role": roadmap_data.target_role,
        "duration_weeks": 16,
        "difficulty_level": roadmap_data.experience_level,
        "status": "not_started",
        "progress_percentage": 0,
        "created_at": "2024-01-01T00:00:00Z"
    }
    roadmaps_db[roadmap_id] = roadmap
    return roadmap

@app.get("/api/v1/roadmaps/{roadmap_id}", response_model=RoadmapResponse, tags=["Roadmaps"])
async def get_roadmap(roadmap_id: str):
    """Get roadmap by ID"""
    if roadmap_id not in roadmaps_db:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return roadmaps_db[roadmap_id]

# Assessments endpoints
@app.get("/api/v1/assessments", response_model=List[AssessmentResponse], tags=["Assessments"])
async def get_my_assessments(skip: int = 0, limit: int = 10):
    """Get user's assessments"""
    return [
        {
            "id": "assessment-1",
            "title": "Python Fundamentals Assessment",
            "type": "technical",
            "status": "completed",
            "score": 85,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": "assessment-2",
            "title": "JavaScript Assessment",
            "type": "technical",
            "status": "in_progress",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ][skip:skip + limit]

@app.post("/api/v1/assessments", response_model=AssessmentResponse, tags=["Assessments"])
async def create_assessment(assessment_data: AssessmentCreate):
    """Create a new assessment"""
    assessment_id = str(uuid4())
    assessment = {
        "id": assessment_id,
        "title": assessment_data.title,
        "type": assessment_data.type,
        "status": "created",
        "created_at": "2024-01-01T00:00:00Z"
    }
    assessments_db[assessment_id] = assessment
    return assessment

@app.get("/api/v1/assessments/{assessment_id}", response_model=AssessmentResponse, tags=["Assessments"])
async def get_assessment(assessment_id: str):
    """Get assessment by ID"""
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessments_db[assessment_id]

@app.post("/api/v1/assessments/{assessment_id}/start", tags=["Assessments"])
async def start_assessment(assessment_id: str):
    """Start an assessment"""
    return {"message": "Assessment started", "assessment_id": assessment_id}

@app.post("/api/v1/assessments/{assessment_id}/submit", tags=["Assessments"])
async def submit_assessment(assessment_id: str, answers: List[dict]):
    """Submit assessment answers"""
    return {
        "score": 85,
        "total_questions": len(answers),
        "correct_answers": int(len(answers) * 0.85),
        "feedback": "Good performance!"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
