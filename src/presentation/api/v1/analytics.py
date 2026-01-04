"""
Analytics API endpoints
User performance metrics and insights
"""
from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
import psycopg2

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Pydantic models for request/response
class AnalyticsOverview(BaseModel):
    """Analytics overview response model"""
    total_users: int
    total_analytics_records: int
    users_with_progress: int
    users_with_assessments: int
    
    class Config:
        schema_extra = {
            "example": {
                "total_users": 1000,
                "total_analytics_records": 500,
                "users_with_progress": 750,
                "users_with_assessments": 600
            }
        }

class UserAnalytics(BaseModel):
    """User analytics response model"""
    user_id: str
    skill_progress: Dict[str, Dict[str, Any]]
    readiness_trends: Dict[str, float]
    assessment_history: List[Dict[str, Any]]
    study_time: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "skill_progress": {
                    "python": {"level": 7, "confidence": "high"},
                    "javascript": {"level": 5, "confidence": "medium"}
                },
                "readiness_trends": {
                    "overall": 0.75,
                    "technical": 0.80,
                    "behavioral": 0.70
                },
                "assessment_history": [
                    {
                        "assessment_id": "assessment-123",
                        "score": 85,
                        "date": "2024-01-01T00:00:00Z"
                    }
                ],
                "study_time": {
                    "total_minutes": 1200,
                    "daily_average": 60
                }
            }
        }

class LeaderboardEntry(BaseModel):
    """Leaderboard entry response model"""
    rank: int
    user_id: str
    score: float
    name: str
    
    class Config:
        schema_extra = {
            "example": {
                "rank": 1,
                "user_id": "user-123",
                "score": 95,
                "name": "John Doe"
            }
        }

class LeaderboardResponse(BaseModel):
    """Leaderboard response model"""
    leaderboard_type: str
    category: Optional[str]
    entries: List[LeaderboardEntry]
    total_participants: int
    last_updated: str
    
    class Config:
        schema_extra = {
            "example": {
                "leaderboard_type": "skill_mastery",
                "category": "Python",
                "entries": [
                    {"rank": 1, "user_id": "user-123", "score": 95, "name": "John Doe"},
                    {"rank": 2, "user_id": "user-456", "score": 87, "name": "Jane Smith"}
                ],
                "total_participants": 100,
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }

class SkillAnalytics(BaseModel):
    """Skill analytics response model"""
    skill_id: str
    total_users: int
    average_level: float
    confident_users: int
    
    class Config:
        schema_extra = {
            "example": {
                "skill_id": "skill-123",
                "total_users": 500,
                "average_level": 6.5,
                "confident_users": 300
            }
        }

class AssessmentAnalytics(BaseModel):
    """Assessment analytics response model"""
    assessment_id: str
    total_attempts: int
    average_score: float
    best_score: float
    worst_score: float
    
    class Config:
        schema_extra = {
            "example": {
                "assessment_id": "assessment-123",
                "total_attempts": 100,
                "average_score": 78.5,
                "best_score": 95,
                "worst_score": 45
            }
        }

def get_db_connection():
    """Get database connection with hardcoded credentials"""
    return psycopg2.connect(
        host="aws-1-ap-southeast-1.pooler.supabase.com",
        port="5432",
        database="postgres",
        user="postgres.dfymgksznlpyfuueqomg",
        password="QpshyJLctAZsLFYl",
        connect_timeout=15
    )

@router.get(
    "/",
    response_model=Dict[str, Any],
    summary="Get Analytics Overview",
    description="Get analytics overview and summary statistics for the platform",
    responses={
        200: {
            "description": "Analytics overview retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Analytics overview retrieved successfully",
                        "analytics": {
                            "total_users": 1000,
                            "total_analytics_records": 500,
                            "users_with_progress": 750,
                            "users_with_assessments": 600
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve analytics: Database error"}
                }
            }
        }
    }
)
async def get_analytics():
    """Get analytics overview"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get overview statistics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT a.user_id) as total_users,
                COUNT(*) as total_analytics_records,
                COUNT(CASE WHEN a.skill_progress IS NOT NULL THEN 1 END) as users_with_progress,
                COUNT(CASE WHEN a.assessment_history IS NOT NULL THEN 1 END) as users_with_assessments
            FROM analytics a
        """)
        
        overview_data = cursor.fetchone()
        
        analytics = {
            "total_users": overview_data[0] if overview_data[0] else 0,
            "total_analytics_records": overview_data[1] if overview_data[1] else 0,
            "users_with_progress": overview_data[2] if overview_data[2] else 0,
            "users_with_assessments": overview_data[3] if overview_data[3] else 0
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Analytics overview retrieved successfully",
            "analytics": analytics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )

@router.get(
    "/users/{user_id}",
    response_model=Dict[str, Any],
    summary="Get User Analytics",
    description="Retrieve detailed analytics and progress information for a specific user",
    responses={
        200: {
            "description": "User analytics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User analytics retrieved successfully",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "analytics": {
                            "skill_progress": {
                                "python": {"level": 7, "confidence": "high"},
                                "javascript": {"level": 5, "confidence": "medium"}
                            },
                            "readiness_trends": {
                                "overall": 0.75,
                                "technical": 0.80,
                                "behavioral": 0.70
                            },
                            "assessment_history": [
                                {
                                    "assessment_id": "assessment-123",
                                    "score": 85,
                                    "date": "2024-01-01T00:00:00Z"
                                }
                            ],
                            "study_time": {
                                "total_minutes": 1200,
                                "daily_average": 60
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve user analytics: Database error"}
                }
            }
        }
    }
)
async def get_user_analytics(
    user_id: str = Path(..., description="UUID of the user to get analytics for")
):
    """Get analytics for specific user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.skill_progress, a.readiness_trends, a.assessment_history,
                   a.topic_coverage, a.study_time, a.leaderboards, a.summary
            FROM analytics a
            WHERE a.user_id = %s
        """, (str(user_id),))
        
        analytics_data = cursor.fetchone()
        
        if not analytics_data:
            raise HTTPException(
                status_code=404,
                detail="User analytics not found"
            )
        
        analytics = {
            "skill_progress": analytics_data[0] if analytics_data[0] else {},
            "readiness_trends": analytics_data[1] if analytics_data[1] else {},
            "assessment_history": analytics_data[2] if analytics_data[2] else {},
            "topic_coverage": analytics_data[3] if analytics_data[3] else {},
            "study_time": analytics_data[4] if analytics_data[4] else {},
            "leaderboards": analytics_data[5] if analytics_data[5] else {},
            "summary": analytics_data[6] if analytics_data[6] else {}
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "User analytics retrieved successfully",
            "user_id": str(user_id),
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user analytics: {str(e)}"
        )

@router.get(
    "/leaderboards",
    response_model=Dict[str, Any],
    summary="Get Leaderboards",
    description="Retrieve various leaderboards showing top performers across different categories",
    responses={
        200: {
            "description": "Leaderboards retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Leaderboards retrieved successfully",
                        "leaderboards": [
                            {
                                "leaderboard_type": "skill_mastery",
                                "category": "Python",
                                "entries": [
                                    {"rank": 1, "user_id": "user-123", "score": 95, "name": "John Doe"},
                                    {"rank": 2, "user_id": "user-456", "score": 87, "name": "Jane Smith"}
                                ],
                                "total_participants": 100,
                                "last_updated": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "total": 1
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve leaderboards: Database error"}
                }
            }
        }
    }
)
async def get_leaderboards(
    type: Optional[str] = Query(None, description="Filter leaderboard by type"),
    category: Optional[str] = Query(None, description="Filter leaderboard by category"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of entries to return")
):
    """Get leaderboards"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.leaderboard_type, l.category, l.entries, l.total_participants, l.last_updated
            FROM leaderboards l
            ORDER BY l.last_updated DESC
        """)
        
        leaderboards_data = cursor.fetchall()
        
        leaderboards = []
        for row in leaderboards_data:
            leaderboard = {
                "leaderboard_type": row[0],
                "category": row[1],
                "entries": row[2] if row[2] else [],
                "total_participants": row[3],
                "last_updated": row[4].isoformat() if row[4] else None
            }
            leaderboards.append(leaderboard)
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Leaderboards retrieved successfully",
            "leaderboards": leaderboards,
            "total": len(leaderboards)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve leaderboards: {str(e)}"
        )

@router.get(
    "/skills/{skill_id}",
    response_model=Dict[str, Any],
    summary="Get Skill Analytics",
    description="Retrieve analytics and performance data for a specific skill",
    responses={
        200: {
            "description": "Skill analytics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Skill analytics retrieved successfully",
                        "skill_analytics": {
                            "skill_id": "skill-123",
                            "total_users": 500,
                            "average_level": 6.5,
                            "confident_users": 300,
                            "completion_rate": 0.75,
                            "average_time_to_master": 120
                        }
                    }
                }
            }
        },
        404: {
            "description": "Skill not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Skill not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve skill analytics: Database error"}
                }
            }
        }
    }
)
async def get_skill_analytics(
    skill_id: str = Path(..., description="UUID of the skill to get analytics for")
):
    """Get analytics for specific skill"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get skill progress data
        cursor.execute("""
            SELECT COUNT(*) as total_users,
                   AVG(CAST(usp.current_level AS FLOAT)) as avg_level,
                   COUNT(CASE WHEN usp.confidence_level = 'high' THEN 1 END) as confident_users
            FROM user_skill_progress usp
            WHERE usp.skill_id = %s
        """, (skill_id,))
        
        skill_data = cursor.fetchone()
        
        skill_analytics = {
            "skill_id": skill_id,
            "total_users": skill_data[0] if skill_data[0] else 0,
            "average_level": float(skill_data[1]) if skill_data[1] else 0.0,
            "confident_users": skill_data[2] if skill_data[2] else 0
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Skill analytics retrieved successfully",
            "skill_analytics": skill_analytics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve skill analytics: {str(e)}"
        )

@router.get(
    "/assessments/{assessment_id}",
    response_model=Dict[str, Any],
    summary="Get Assessment Analytics",
    description="Retrieve performance analytics and statistics for a specific assessment",
    responses={
        200: {
            "description": "Assessment analytics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Assessment analytics retrieved successfully",
                        "assessment_analytics": {
                            "assessment_id": "assessment-123",
                            "total_attempts": 100,
                            "average_score": 78.5,
                            "best_score": 95,
                            "worst_score": 45,
                            "pass_rate": 0.65,
                            "average_completion_time": 2700,
                            "difficulty_rating": 3.5
                        }
                    }
                }
            }
        },
        404: {
            "description": "Assessment not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Assessment not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve assessment analytics: Database error"}
                }
            }
        }
    }
)
async def get_assessment_analytics(
    assessment_id: str = Path(..., description="UUID of the assessment to get analytics for")
):
    """Get analytics for specific assessment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total_attempts,
                   AVG(qe.score) as average_score,
                   MAX(qe.score) as best_score,
                   MIN(qe.score) as worst_score
            FROM question_evaluations qe
            WHERE qe.assessment_id = %s
        """, (assessment_id,))
        
        assessment_data = cursor.fetchone()
        
        assessment_analytics = {
            "assessment_id": assessment_id,
            "total_attempts": assessment_data[0] if assessment_data[0] else 0,
            "average_score": float(assessment_data[1]) if assessment_data[1] else 0.0,
            "best_score": assessment_data[2] if assessment_data[2] else 0,
            "worst_score": assessment_data[3] if assessment_data[3] else 0
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Assessment analytics retrieved successfully",
            "assessment_analytics": assessment_analytics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve assessment analytics: {str(e)}"
        )

@router.get("/roadmaps/{roadmap_id}")
async def get_roadmap_analytics(roadmap_id: str):
    """Get analytics for specific roadmap"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total_users,
                   AVG(r.progress_percentage) as avg_progress,
                   COUNT(CASE WHEN r.status = 'completed' THEN 1 END) as completed_users
            FROM roadmaps r
            WHERE r.id = %s
        """, (roadmap_id,))
        
        roadmap_data = cursor.fetchone()
        
        roadmap_analytics = {
            "roadmap_id": roadmap_id,
            "total_users": roadmap_data[0] if roadmap_data[0] else 0,
            "average_progress": float(roadmap_data[1]) if roadmap_data[1] else 0.0,
            "completed_users": roadmap_data[2] if roadmap_data[2] else 0
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Roadmap analytics retrieved successfully",
            "roadmap_analytics": roadmap_analytics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve roadmap analytics: {str(e)}"
        )
