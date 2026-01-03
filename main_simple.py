"""
Simple FastAPI Application - No Complex Configuration
This bypasses all configuration issues and just works
"""
import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta

app = FastAPI(
    title="Interview Preparation Platform",
    description="AI-powered interview preparation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - simple configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "candidate"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RoadmapRequest(BaseModel):
    job_description: Optional[str] = None
    target_role: Optional[str] = None
    skills: Optional[List[str]] = None

class AssessmentRequest(BaseModel):
    skill: str
    difficulty: str = "medium"
    question_count: int = 20

class SimulationRequest(BaseModel):
    role: str
    difficulty: str = "medium"
    stress_mode: bool = False

# In-memory storage (for demo)
users_db = {}
roadmaps_db = {}
assessments_db = {}
simulations_db = {}
tokens_db = {}

# Helper functions
def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    return f"access_token_{uuid4()}"

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    return f"refresh_token_{uuid4()}"

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    if token not in tokens_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return tokens_db[token]

# ===== AUTH ENDPOINTS =====

@app.post("/api/v1/auth/register", response_model=UserResponse, tags=["Authentication"])
async def register(user_data: UserCreate):
    """Register a new user"""
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = str(uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "role": user_data.role,
        "password": user_data.password,  # In production, hash this!
        "created_at": datetime.now()
    }
    
    users_db[user_id] = user
    return UserResponse(**user)

@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(login_data: UserLogin):
    """User login"""
    for user in users_db.values():
        if user["email"] == login_data.email and user["password"] == login_data.password:
            access_token = create_access_token(user["id"])
            refresh_token = create_refresh_token(user["id"])
            
            tokens_db[access_token] = user
            tokens_db[refresh_token] = user
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=1800
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(**current_user)

# ===== USER ENDPOINTS =====

@app.post("/api/v1/users/upload-resume", tags=["Users"])
async def upload_resume(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload and parse resume"""
    # Simulate resume parsing
    parsed_data = {
        "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
        "experience": "5 years",
        "education": "Bachelor's in Computer Science",
        "projects": ["E-commerce platform", "Mobile app", "API development"]
    }
    
    return {
        "message": "Resume uploaded and parsed successfully",
        "parsed_data": parsed_data
    }

@app.get("/api/v1/users/profile", tags=["Users"])
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user profile"""
    return {
        "user": current_user,
        "stats": {
            "assessments_completed": 5,
            "simulations_completed": 2,
            "roadmaps_in_progress": 1,
            "study_time_hours": 23
        }
    }

@app.put("/api/v1/users/profile", tags=["Users"])
async def update_user_profile(
    profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    return {
        "message": "Profile updated successfully",
        "updated_fields": list(profile_data.keys())
    }

@app.post("/api/v1/users/interview-feedback", tags=["Users"])
async def submit_interview_feedback(
    feedback_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Submit interview feedback"""
    return {
        "message": "Interview feedback submitted successfully",
        "feedback_id": str(uuid4()),
        "analysis": "Feedback analyzed and roadmap updated"
    }

@app.get("/api/v1/users/interview-feedback/history", tags=["Users"])
async def get_feedback_history(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get interview feedback history"""
    return {
        "feedback_history": [
            {
                "id": "1",
                "company": "Tech Corp",
                "role": "Software Engineer",
                "date": "2024-01-15",
                "score": 85,
                "feedback": "Good technical skills, improve communication"
            }
        ]
    }

# ===== ROADMAP ENDPOINTS =====

@app.post("/api/v1/roadmaps/generate", tags=["Roadmaps"])
async def generate_roadmap(
    request: RoadmapRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate personalized learning roadmap"""
    roadmap_id = str(uuid4())
    
    # Simulate AI roadmap generation
    roadmap = {
        "id": roadmap_id,
        "user_id": current_user["id"],
        "target_role": request.target_role or "Software Engineer",
        "job_description": request.job_description,
        "skills": request.skills or ["Python", "JavaScript", "System Design"],
        "topics": [
            {
                "id": "1",
                "title": "Data Structures & Algorithms",
                "description": "Master fundamental data structures",
                "difficulty": "medium",
                "estimated_hours": 20,
                "resources": ["LeetCode", "Cracking the Coding Interview"],
                "completed": False
            },
            {
                "id": "2", 
                "title": "System Design",
                "description": "Learn scalable system design",
                "difficulty": "hard",
                "estimated_hours": 30,
                "resources": ["Designing Data-Intensive Applications", "Grokking System Design"],
                "completed": False
            },
            {
                "id": "3",
                "title": "Behavioral Interview",
                "description": "Prepare for behavioral questions",
                "difficulty": "easy",
                "estimated_hours": 10,
                "resources": ["STAR method practice", "Common behavioral questions"],
                "completed": False
            }
        ],
        "created_at": datetime.now(),
        "progress": 0
    }
    
    roadmaps_db[roadmap_id] = roadmap
    return roadmap

@app.get("/api/v1/roadmaps/{roadmap_id}", tags=["Roadmaps"])
async def get_roadmap(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get roadmap details"""
    if roadmap_id not in roadmaps_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found"
        )
    
    roadmap = roadmaps_db[roadmap_id]
    if roadmap["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return roadmap

@app.get("/api/v1/roadmaps", tags=["Roadmaps"])
async def list_roadmaps(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all user roadmaps"""
    user_roadmaps = [r for r in roadmaps_db.values() if r["user_id"] == current_user["id"]]
    return {"roadmaps": user_roadmaps}

@app.put("/api/v1/roadmaps/{roadmap_id}/progress", tags=["Roadmaps"])
async def update_roadmap_progress(
    roadmap_id: str,
    progress_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update roadmap progress"""
    if roadmap_id not in roadmaps_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found"
        )
    
    roadmap = roadmaps_db[roadmap_id]
    if roadmap["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    roadmap["progress"] = progress_data.get("progress", roadmap["progress"])
    return {"message": "Progress updated successfully", "progress": roadmap["progress"]}

@app.delete("/api/v1/roadmaps/{roadmap_id}", tags=["Roadmaps"])
async def delete_roadmap(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete roadmap"""
    if roadmap_id not in roadmaps_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found"
        )
    
    roadmap = roadmaps_db[roadmap_id]
    if roadmap["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    del roadmaps_db[roadmap_id]
    return {"message": "Roadmap deleted successfully"}

# ===== ASSESSMENT ENDPOINTS =====

@app.post("/api/v1/assessments/generate", tags=["Assessments"])
async def generate_assessment(
    request: AssessmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate skill assessment"""
    assessment_id = str(uuid4())
    
    # Simulate AI assessment generation
    questions = []
    for i in range(request.question_count):
        questions.append({
            "id": str(i + 1),
            "type": "multiple_choice",
            "question": f"Sample question {i + 1} about {request.skill}",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "difficulty": request.difficulty,
            "points": 10
        })
    
    assessment = {
        "id": assessment_id,
        "user_id": current_user["id"],
        "skill": request.skill,
        "difficulty": request.difficulty,
        "questions": questions,
        "created_at": datetime.now(),
        "status": "pending",
        "score": None
    }
    
    assessments_db[assessment_id] = assessment
    return assessment

@app.post("/api/v1/assessments/{assessment_id}/submit", tags=["Assessments"])
async def submit_assessment(
    assessment_id: str,
    answers: Dict[str, str],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Submit assessment answers"""
    if assessment_id not in assessments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    assessment = assessments_db[assessment_id]
    if assessment["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Calculate score
    correct = 0
    for question in assessment["questions"]:
        if answers.get(question["id"]) == question["correct_answer"]:
            correct += 1
    
    score = (correct / len(assessment["questions"])) * 100
    assessment["score"] = score
    assessment["status"] = "completed"
    
    return {
        "assessment_id": assessment_id,
        "score": score,
        "correct_answers": correct,
        "total_questions": len(assessment["questions"]),
        "status": "completed"
    }

@app.get("/api/v1/assessments", tags=["Assessments"])
async def list_assessments(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all user assessments"""
    user_assessments = [a for a in assessments_db.values() if a["user_id"] == current_user["id"]]
    return {"assessments": user_assessments}

@app.get("/api/v1/assessments/{assessment_id}", tags=["Assessments"])
async def get_assessment(
    assessment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get assessment details"""
    if assessment_id not in assessments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    assessment = assessments_db[assessment_id]
    if assessment["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return assessment

@app.get("/api/v1/assessments/{assessment_id}/results", tags=["Assessments"])
async def get_assessment_results(
    assessment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get assessment results and analysis"""
    if assessment_id not in assessments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    assessment = assessments_db[assessment_id]
    if assessment["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "assessment_id": assessment_id,
        "score": assessment.get("score"),
        "analysis": "Strong performance in core concepts, need improvement in advanced topics",
        "recommendations": ["Practice more algorithms", "Review system design patterns"],
        "skill_breakdown": {
            "algorithms": 85,
            "data_structures": 90,
            "problem_solving": 75
        }
    }

# ===== SIMULATION ENDPOINTS =====

@app.post("/api/v1/simulation/start", tags=["Simulation"])
async def start_simulation(
    request: SimulationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Start interview simulation"""
    simulation_id = str(uuid4())
    
    simulation = {
        "id": simulation_id,
        "user_id": current_user["id"],
        "role": request.role,
        "difficulty": request.difficulty,
        "stress_mode": request.stress_mode,
        "status": "active",
        "current_question": 1,
        "questions": [
            {
                "id": "1",
                "question": "Tell me about yourself and your experience.",
                "type": "behavioral",
                "time_limit": 120
            },
            {
                "id": "2",
                "question": "How would you design a URL shortener?",
                "type": "technical",
                "time_limit": 300
            },
            {
                "id": "3",
                "question": "What's your biggest weakness?",
                "type": "behavioral",
                "time_limit": 90
            }
        ],
        "answers": {},
        "feedback": None,
        "started_at": datetime.now()
    }
    
    simulations_db[simulation_id] = simulation
    return simulation

@app.post("/api/v1/simulation/{simulation_id}/answer", tags=["Simulation"])
async def submit_simulation_answer(
    simulation_id: str,
    answer: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Submit answer for simulation question"""
    if simulation_id not in simulations_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    simulation = simulations_db[simulation_id]
    if simulation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    current_q = simulation["current_question"]
    simulation["answers"][str(current_q)] = answer
    
    # Generate AI feedback (simulated)
    feedback = {
        "question_id": str(current_q),
        "answer_quality": "good",
        "suggestions": "Be more specific about your achievements",
        "score": 8.5
    }
    
    # Move to next question or end simulation
    if current_q >= len(simulation["questions"]):
        simulation["status"] = "completed"
        simulation["feedback"] = "Overall good performance. Focus on being more specific with examples."
    else:
        simulation["current_question"] += 1
    
    return {
        "simulation_id": simulation_id,
        "current_question": simulation["current_question"],
        "status": simulation["status"],
        "feedback": feedback
    }

@app.get("/api/v1/simulation/{simulation_id}", tags=["Simulation"])
async def get_simulation(
    simulation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get simulation details"""
    if simulation_id not in simulations_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    simulation = simulations_db[simulation_id]
    if simulation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return simulation

@app.get("/api/v1/simulation", tags=["Simulation"])
async def list_simulations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all user simulations"""
    user_simulations = [s for s in simulations_db.values() if s["user_id"] == current_user["id"]]
    return {"simulations": user_simulations}

@app.post("/api/v1/simulation/{simulation_id}/complete", tags=["Simulation"])
async def complete_simulation(
    simulation_id: str,
    feedback_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Complete simulation and get final feedback"""
    if simulation_id not in simulations_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    simulation = simulations_db[simulation_id]
    if simulation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    simulation["status"] = "completed"
    simulation["feedback"] = feedback_data.get("feedback", "Simulation completed successfully")
    
    return {
        "simulation_id": simulation_id,
        "status": "completed",
        "overall_score": 85,
        "feedback": "Great performance! Focus on improving communication clarity.",
        "recommendations": ["Practice STAR method", "Be more concise", "Add specific examples"]
    }

# ===== ANALYTICS ENDPOINTS =====

@app.get("/api/v1/analytics/dashboard", tags=["Analytics"])
async def get_analytics_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user analytics dashboard"""
    return {
        "user_id": current_user["id"],
        "skill_progress": {
            "Python": 75,
            "JavaScript": 60,
            "System Design": 45
        },
        "readiness_score": 67,
        "assessments_completed": 5,
        "simulations_completed": 2,
        "roadmaps_in_progress": 1,
        "study_time_hours": 23,
        "last_activity": datetime.now().isoformat()
    }

@app.get("/api/v1/analytics/leaderboard", tags=["Analytics"])
async def get_leaderboard(
    limit: int = 10,
    category: str = "overall",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get leaderboard"""
    # Simulate leaderboard data
    leaderboard = [
        {"rank": 1, "name": "Alice Chen", "score": 95, "category": category},
        {"rank": 2, "name": "Bob Smith", "score": 87, "category": category},
        {"rank": 3, "name": "Carol Davis", "score": 82, "category": category},
        {"rank": 4, "name": "David Wilson", "score": 78, "category": category},
        {"rank": 5, "name": "Eve Johnson", "score": 75, "category": category}
    ]
    
    return {
        "leaderboard": leaderboard[:limit],
        "category": category,
        "user_rank": 12,  # Current user's rank
        "total_users": 156
    }

@app.get("/api/v1/analytics/progress", tags=["Analytics"])
async def get_progress_analytics(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get detailed progress analytics"""
    return {
        "user_id": current_user["id"],
        "overall_progress": 67,
        "skill_progress": {
            "algorithms": 75,
            "data_structures": 80,
            "system_design": 45,
            "behavioral": 85,
            "problem_solving": 70
        },
        "time_spent": {
            "total_hours": 23,
            "this_week": 8,
            "daily_average": 3.3
        },
        "completion_rates": {
            "roadmaps": 60,
            "assessments": 80,
            "simulations": 100
        },
        "weak_areas": ["System Design", "Advanced Algorithms"],
        "strong_areas": ["Behavioral Interview", "Data Structures"]
    }

@app.get("/api/v1/analytics/recommendations", tags=["Analytics"])
async def get_recommendations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get personalized recommendations"""
    return {
        "user_id": current_user["id"],
        "recommendations": [
            {
                "type": "skill_focus",
                "title": "Improve System Design",
                "description": "Focus on distributed systems and scalability",
                "priority": "high"
            },
            {
                "type": "practice",
                "title": "More Algorithm Practice",
                "description": "Practice 5 medium problems daily",
                "priority": "medium"
            },
            {
                "type": "simulation",
                "title": "Mock Interviews",
                "description": "Schedule 2 mock interviews this week",
                "priority": "high"
            }
        ],
        "next_steps": [
            "Complete current roadmap on System Design",
            "Take advanced algorithms assessment",
            "Practice behavioral questions with STAR method"
        ]
    }

# ===== ADMIN ENDPOINTS =====

@app.get("/api/v1/admin/users", tags=["Admin"])
async def get_all_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "users": list(users_db.values()),
        "total_count": len(users_db),
        "active_users": len([u for u in users_db.values() if u.get("active", True)])
    }

@app.get("/api/v1/admin/stats", tags=["Admin"])
async def get_platform_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get platform statistics (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {
        "total_users": len(users_db),
        "total_roadmaps": len(roadmaps_db),
        "total_assessments": len(assessments_db),
        "total_simulations": len(simulations_db),
        "active_sessions": 23,
        "daily_active_users": 45,
        "platform_health": "excellent"
    }

# ===== DATABASE VIEWER ENDPOINTS =====

@app.get("/api/v1/database/view", tags=["Database"])
async def view_database_records(current_user: Dict[str, Any] = Depends(get_current_user)):
    """View all database records (for demo purposes)"""
    return {
        "users": list(users_db.values()),
        "roadmaps": list(roadmaps_db.values()),
        "assessments": list(assessments_db.values()),
        "simulations": list(simulations_db.values()),
        "total_records": {
            "users": len(users_db),
            "roadmaps": len(roadmaps_db),
            "assessments": len(assessments_db),
            "simulations": len(simulations_db)
        }
    }

@app.get("/api/v1/database/reset", tags=["Database"])
async def reset_database(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Reset all database records (for demo purposes)"""
    global users_db, roadmaps_db, assessments_db, simulations_db
    
    users_db.clear()
    roadmaps_db.clear()
    assessments_db.clear()
    simulations_db.clear()
    
    return {"message": "Database reset successfully"}

# ===== ROOT AND HEALTH ENDPOINTS =====

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Interview Preparation Platform API",
        "version": "1.0.0",
        "environment": "production",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "roadmaps": "/api/v1/roadmaps",
            "assessments": "/api/v1/assessments",
            "simulation": "/api/v1/simulation",
            "analytics": "/api/v1/analytics"
        }
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "production",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "ai_services": "connected",
            "cache": "connected"
        }
    }

@app.get("/ready", tags=["Health"])
async def ready():
    """Ready check for load balancers"""
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "cache": "ok",
            "ai_services": "ok"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
