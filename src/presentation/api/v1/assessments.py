"""
Assessments API endpoints
Assessment creation, management, and evaluation
"""
from fastapi import APIRouter, HTTPException, status, Query, Path, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
import psycopg2

router = APIRouter(prefix="/assessments", tags=["Assessments"])

# Pydantic models for request/response
class AssessmentCreate(BaseModel):
    """Assessment creation request model"""
    title: str
    assessment_type: str
    skill_ids: List[str] = []
    difficulty: str = "intermediate"
    duration_minutes: int = 60
    user_id: Optional[str] = None
    roadmap_id: Optional[str] = None
    adaptive_difficulty: bool = True
    allow_hints: bool = True
    allow_review: bool = True
    randomize_questions: bool = True
    passing_score: int = 70
    max_attempts: int = 3
    time_limit_per_question: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Python Programming Assessment",
                "assessment_type": "technical",
                "skill_ids": ["skill-123", "skill-456"],
                "difficulty": "intermediate",
                "duration_minutes": 60,
                "user_id": "user-uuid",
                "roadmap_id": "roadmap-uuid",
                "adaptive_difficulty": True,
                "allow_hints": True,
                "allow_review": True,
                "randomize_questions": True,
                "passing_score": 70,
                "max_attempts": 3,
                "time_limit_per_question": 30
            }
        }

class AssessmentUpdate(BaseModel):
    """Assessment update request model"""
    title: Optional[str] = None
    assessment_type: Optional[str] = None
    skill_ids: Optional[List[str]] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = None
    adaptive_difficulty: Optional[bool] = None
    allow_hints: Optional[bool] = None
    allow_review: Optional[bool] = None
    randomize_questions: Optional[bool] = None
    passing_score: Optional[int] = None
    max_attempts: Optional[int] = None
    time_limit_per_question: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Python Assessment",
                "difficulty": "advanced",
                "passing_score": 80
            }
        }

class AssessmentResponse(BaseModel):
    """Assessment response model"""
    id: str
    title: str
    assessment_type: str
    skill_ids: List[str]
    difficulty: str
    duration_minutes: int
    user_id: Optional[str]
    roadmap_id: Optional[str]
    status: str
    adaptive_difficulty: bool
    allow_hints: bool
    allow_review: bool
    randomize_questions: bool
    passing_score: int
    max_attempts: int
    time_limit_per_question: Optional[int]
    started_at: Optional[str]
    completed_at: Optional[str]
    expires_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Python Programming Assessment",
                "assessment_type": "technical",
                "skill_ids": ["skill-123", "skill-456"],
                "difficulty": "intermediate",
                "duration_minutes": 60,
                "user_id": "user-456",
                "roadmap_id": "roadmap-789",
                "status": "created",
                "adaptive_difficulty": True,
                "allow_hints": True,
                "allow_review": True,
                "randomize_questions": True,
                "passing_score": 70,
                "max_attempts": 3,
                "time_limit_per_question": 30,
                "started_at": None,
                "completed_at": None,
                "expires_at": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class AssessmentStart(BaseModel):
    """Assessment start request model"""
    
    class Config:
        schema_extra = {
            "example": {}
        }

class AssessmentSubmit(BaseModel):
    """Assessment submission request model"""
    responses: List[Dict[str, Any]]
    
    class Config:
        schema_extra = {
            "example": {
                "responses": [
                    {
                        "question_id": "q1",
                        "answer": "Answer to question 1",
                        "time_taken": 120
                    },
                    {
                        "question_id": "q2",
                        "answer": "Answer to question 2",
                        "time_taken": 90
                    }
                ]
            }
        }

class AssessmentResults(BaseModel):
    """Assessment results response model"""
    total_questions: int
    answered_questions: int
    average_score: float
    best_score: float
    worst_score: float
    passed: bool
    
    class Config:
        schema_extra = {
            "example": {
                "total_questions": 10,
                "answered_questions": 10,
                "average_score": 85.5,
                "best_score": 90,
                "worst_score": 75,
                "passed": True
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
    summary="Get All Assessments",
    description="Retrieve all assessments with optional filtering and pagination",
    responses={
        200: {
            "description": "Assessments retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Assessments retrieved successfully",
                        "assessments": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "title": "Python Programming Assessment",
                                "assessment_type": "technical",
                                "skill_ids": ["skill-123", "skill-456"],
                                "difficulty": "intermediate",
                                "duration_minutes": 60,
                                "user_id": "user-456",
                                "roadmap_id": "roadmap-789",
                                "status": "created",
                                "adaptive_difficulty": True,
                                "allow_hints": True,
                                "allow_review": True,
                                "randomize_questions": True,
                                "passing_score": 70,
                                "max_attempts": 3,
                                "time_limit_per_question": 30,
                                "started_at": None,
                                "completed_at": None,
                                "expires_at": None,
                                "created_at": "2024-01-01T00:00:00Z",
                                "updated_at": "2024-01-01T00:00:00Z"
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
                    "example": {"detail": "Failed to retrieve assessments: Database error"}
                }
            }
        }
    }
)
async def get_assessments(
    skip: int = Query(0, ge=0, description="Number of assessments to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of assessments to return (1-100)"),
    user_id: Optional[str] = Query(None, description="Filter assessments by user ID"),
    status: Optional[str] = Query(None, description="Filter assessments by status")
):
    """Get all assessments with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT a.id, a.title, a.assessment_type, a.skill_ids, a.difficulty,
                   a.duration_minutes, a.user_id, a.roadmap_id, a.status,
                   a.adaptive_difficulty, a.allow_hints, a.allow_review, a.randomize_questions,
                   a.passing_score, a.max_attempts, a.time_limit_per_question,
                   a.started_at, a.completed_at, a.expires_at, a.created_at, a.updated_at
            FROM assessments a
            WHERE 1=1
        """
        params = []
        
        if user_id:
            query += " AND a.user_id = %s"
            params.append(user_id)
            
        if status:
            query += " AND a.status = %s"
            params.append(status)
        
        query += " ORDER BY a.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        assessments_data = cursor.fetchall()
        
        # Format the response
        assessments = []
        for row in assessments_data:
            assessment = {
                "id": str(row[0]),
                "title": row[1],
                "assessment_type": row[2],
                "skill_ids": row[3] if row[3] else [],
                "difficulty": row[4],
                "duration_minutes": row[5],
                "user_id": str(row[6]) if row[6] else None,
                "roadmap_id": str(row[7]) if row[7] else None,
                "status": row[8],
                "adaptive_difficulty": row[9],
                "allow_hints": row[10],
                "allow_review": row[11],
                "randomize_questions": row[12],
                "passing_score": row[13],
                "max_attempts": row[14],
                "time_limit_per_question": row[15],
                "started_at": row[16].isoformat() if row[16] else None,
                "completed_at": row[17].isoformat() if row[17] else None,
                "expires_at": row[18].isoformat() if row[18] else None,
                "created_at": row[19].isoformat() if row[19] else None,
                "updated_at": row[20].isoformat() if row[20] else None
            }
            assessments.append(assessment)
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Assessments retrieved successfully",
            "assessments": assessments,
            "total": len(assessments)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve assessments: {str(e)}"
        )

@router.get(
    "/{assessment_id}",
    response_model=Dict[str, Any],
    summary="Get Assessment by ID",
    description="Retrieve a specific assessment by its UUID including all configuration details",
    responses={
        200: {
            "description": "Assessment retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Assessment retrieved successfully",
                        "assessment": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "Python Programming Assessment",
                            "assessment_type": "technical",
                            "skill_ids": ["skill-123", "skill-456"],
                            "difficulty": "intermediate",
                            "duration_minutes": 60,
                            "user_id": "user-456",
                            "roadmap_id": "roadmap-789",
                            "status": "created",
                            "adaptive_difficulty": True,
                            "allow_hints": True,
                            "allow_review": True,
                            "randomize_questions": True,
                            "passing_score": 70,
                            "max_attempts": 3,
                            "time_limit_per_question": 30,
                            "started_at": None,
                            "completed_at": None,
                            "expires_at": None,
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z"
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
                    "example": {"detail": "Failed to retrieve assessment: Database error"}
                }
            }
        }
    }
)
async def get_assessment(
    assessment_id: str = Path(..., description="UUID of the assessment to retrieve")
):
    """Get assessment by ID from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.title, a.assessment_type, a.skill_ids, a.difficulty,
                   a.duration_minutes, a.user_id, a.roadmap_id, a.status,
                   a.adaptive_difficulty, a.allow_hints, a.allow_review, a.randomize_questions,
                   a.passing_score, a.max_attempts, a.time_limit_per_question,
                   a.started_at, a.completed_at, a.expires_at, a.created_at, a.updated_at
            FROM assessments a
            WHERE a.id = %s
        """, (str(assessment_id),))
        
        assessment_data = cursor.fetchone()
        
        if not assessment_data:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )
        
        assessment = {
            "id": str(assessment_data[0]),
            "title": assessment_data[1],
            "assessment_type": assessment_data[2],
            "skill_ids": assessment_data[3] if assessment_data[3] else [],
            "difficulty": assessment_data[4],
            "duration_minutes": assessment_data[5],
            "user_id": str(assessment_data[6]) if assessment_data[6] else None,
            "roadmap_id": str(assessment_data[7]) if assessment_data[7] else None,
            "status": assessment_data[8],
            "adaptive_difficulty": assessment_data[9],
            "allow_hints": assessment_data[10],
            "allow_review": assessment_data[11],
            "randomize_questions": assessment_data[12],
            "passing_score": assessment_data[13],
            "max_attempts": assessment_data[14],
            "time_limit_per_question": assessment_data[15],
            "started_at": assessment_data[16].isoformat() if assessment_data[16] else None,
            "completed_at": assessment_data[17].isoformat() if assessment_data[17] else None,
            "expires_at": assessment_data[18].isoformat() if assessment_data[18] else None,
            "created_at": assessment_data[19].isoformat() if assessment_data[19] else None,
            "updated_at": assessment_data[20].isoformat() if assessment_data[20] else None
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Assessment retrieved successfully",
            "assessment": assessment
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve assessment: {str(e)}"
        )

@router.post(
    "/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create Assessment",
    description="Create a new assessment with specified configuration and settings",
    responses={
        201: {
            "description": "Assessment created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Assessment created successfully",
                        "assessment_id": "123e4567-e89b-12d3-a456-426614174003",
                        "title": "Python Programming Assessment",
                        "assessment_type": "technical"
                    }
                }
            }
        },
        400: {
            "description": "Bad request - Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid assessment type"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to create assessment: Database error"}
                }
            }
        }
    }
)
async def create_assessment(assessment_data: AssessmentCreate):
    """
    Create a new assessment
    
    **Request Body:**
    ```json
    {
        "title": "Python Programming Assessment",
        "assessment_type": "technical",
        "skill_ids": ["skill-123", "skill-456"],
        "difficulty": "intermediate",
        "duration_minutes": 60,
        "user_id": "user-uuid",
        "roadmap_id": "roadmap-uuid",
        "adaptive_difficulty": true,
        "allow_hints": true,
        "allow_review": true,
        "randomize_questions": true,
        "passing_score": 70,
        "max_attempts": 3,
        "time_limit_per_question": 30
    }
    ```
    
    **Required Fields:**
    - `title` (string): Assessment title
    - `assessment_type` (string): Assessment type from predefined values
    
    **Optional Fields:**
    - `skill_ids` (array): List of skill IDs
    - `difficulty` (string): "beginner" | "intermediate" | "advanced" | "expert"
    - `duration_minutes` (integer): Duration in minutes
    - `user_id` (string): User ID
    - `roadmap_id` (string): Roadmap ID
    - `adaptive_difficulty` (boolean): Enable adaptive difficulty
    - `allow_hints` (boolean): Allow hints during assessment
    - `allow_review` (boolean): Allow review after completion
    - `randomize_questions` (boolean): Randomize question order
    - `passing_score` (integer): Minimum passing score (0-100)
    - `max_attempts` (integer): Maximum allowed attempts
    - `time_limit_per_question` (integer): Time limit per question in seconds
    
    Returns the created assessment details with generated ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO assessments (title, assessment_type, skill_ids, difficulty, duration_minutes,
                                  user_id, roadmap_id, adaptive_difficulty, allow_hints, allow_review,
                                  randomize_questions, passing_score, max_attempts, time_limit_per_question,
                                  created_at, updated_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s)
            RETURNING id
        """, (
            assessment_data.title,
            assessment_data.assessment_type,
            assessment_data.skill_ids,
            assessment_data.difficulty,
            assessment_data.duration_minutes,
            assessment_data.user_id,
            assessment_data.roadmap_id,
            assessment_data.adaptive_difficulty,
            assessment_data.allow_hints,
            assessment_data.allow_review,
            assessment_data.randomize_questions,
            assessment_data.passing_score,
            assessment_data.max_attempts,
            assessment_data.time_limit_per_question,
            "created"
        ))
        
        assessment_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Assessment created successfully",
            "assessment_id": str(assessment_id),
            "title": assessment_data.title,
            "assessment_type": assessment_data.assessment_type
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create assessment: {str(e)}"
        )

@router.post(
    "/{assessment_id}/start",
    response_model=Dict[str, Any],
    summary="Start Assessment",
    description="Start an assessment and set its status to in_progress",
    responses={
        200: {
            "description": "Assessment started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Assessment started successfully",
                        "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
                        "started_at": "2024-01-01T10:00:00Z",
                        "expires_at": "2024-01-01T11:00:00Z",
                        "status": "in_progress"
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
        400: {
            "description": "Bad request - Assessment already started or expired",
            "content": {
                "application/json": {
                    "example": {"detail": "Assessment already started"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to start assessment: Database error"}
                }
            }
        }
    }
)
async def start_assessment(
    assessment_id: str = Path(..., description="UUID of the assessment to start")
):
    """Submit assessment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE assessments 
            SET status = 'in_progress', started_at = NOW(), expires_at = NOW() + INTERVAL '1 hour'
            WHERE id = %s AND status = 'created'
        """, (str(assessment_id),))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=400,
                detail="Assessment cannot be started"
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Assessment started successfully",
            "assessment_id": str(assessment_id),
            "started_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "status": "in_progress"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start assessment: {str(e)}"
        )

@router.post("/{assessment_id}/submit")
async def submit_assessment(assessment_id: UUID):
    """Submit assessment"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE assessments 
            SET status = 'completed', completed_at = NOW(), last_activity_at = NOW()
            WHERE id = %s AND status = 'in_progress'
        """, (str(assessment_id),))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=400,
                detail="Assessment cannot be submitted"
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Assessment submitted successfully",
            "assessment_id": str(assessment_id),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit assessment: {str(e)}"
        )

@router.get(
    "/{assessment_id}/results",
    response_model=Dict[str, Any],
    summary="Get Assessment Results",
    description="Retrieve detailed results and performance metrics for a completed assessment",
    responses={
        200: {
            "description": "Assessment results retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Assessment results retrieved successfully",
                        "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
                        "results": {
                            "total_questions": 10,
                            "answered_questions": 10,
                            "average_score": 85.5,
                            "best_score": 90,
                            "worst_score": 75,
                            "passed": True,
                            "time_taken": 2700,
                            "performance_breakdown": {
                                "technical": 88,
                                "practical": 83,
                                "theoretical": 85
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "Assessment not found or not completed",
            "content": {
                "application/json": {
                    "example": {"detail": "Assessment results not available"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve assessment results: Database error"}
                }
            }
        }
    }
)
async def get_assessment_results(
    assessment_id: str = Path(..., description="UUID of the assessment to get results for")
):
    """Get assessment results"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(aq.id), COUNT(ar.id), AVG(qe.score), MAX(qe.score), MIN(qe.score)
            FROM assessments a
            LEFT JOIN assessment_questions aq ON a.id = aq.assessment_id
            LEFT JOIN assessment_responses ar ON a.id = ar.assessment_id
            LEFT JOIN question_evaluations qe ON a.id = qe.assessment_id AND aq.id = qe.question_id
            WHERE a.id = %s
        """, (str(assessment_id),))
        
        results_data = cursor.fetchone()
        
        results = {
            "total_questions": results_data[0] if results_data[0] else 0,
            "answered_questions": results_data[1] if results_data[1] else 0,
            "average_score": float(results_data[2]) if results_data[2] else 0.0,
            "best_score": results_data[3] if results_data[3] else 0,
            "worst_score": results_data[4] if results_data[4] else 0,
            "passed": (results_data[2] or 0) >= 70
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Assessment results retrieved successfully",
            "assessment_id": str(assessment_id),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve assessment results: {str(e)}"
        )
