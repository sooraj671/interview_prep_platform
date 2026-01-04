"""
Roadmaps API endpoints
Learning path generation and management
"""
from fastapi import APIRouter, HTTPException, status, Query, Path, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
import psycopg2

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])

# Pydantic models for request/response
class RoadmapCreate(BaseModel):
    """Roadmap creation request model"""
    title: str
    description: str = ""
    target_role: str
    duration_weeks: int = 12
    difficulty: str = "intermediate"
    user_id: str
    ai_generated: bool = False
    generation_prompt: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Python Backend Developer Roadmap",
                "description": "Comprehensive roadmap to become a Python backend developer",
                "target_role": "Backend Developer",
                "duration_weeks": 12,
                "difficulty": "intermediate",
                "user_id": "user-uuid",
                "ai_generated": False,
                "generation_prompt": "Create a roadmap for Python backend development"
            }
        }

class RoadmapUpdate(BaseModel):
    """Roadmap update request model"""
    title: Optional[str] = None
    description: Optional[str] = None
    target_role: Optional[str] = None
    duration_weeks: Optional[int] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Python Backend Developer Roadmap",
                "duration_weeks": 16,
                "difficulty": "advanced"
            }
        }

class RoadmapResponse(BaseModel):
    """Roadmap response model"""
    id: str
    title: str
    description: str
    target_role: str
    duration_weeks: int
    difficulty: str
    status: str
    progress_percentage: int
    total_topics: int
    completed_topics: int
    ai_generated: bool
    user_id: str
    created_at: str
    updated_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Python Backend Developer Roadmap",
                "description": "Comprehensive roadmap to become a Python backend developer",
                "target_role": "Backend Developer",
                "duration_weeks": 12,
                "difficulty": "intermediate",
                "status": "in_progress",
                "progress_percentage": 65,
                "total_topics": 20,
                "completed_topics": 13,
                "ai_generated": False,
                "user_id": "user-456",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "started_at": "2024-01-01T00:00:00Z",
                "completed_at": None
            }
        }

class RoadmapGenerate(BaseModel):
    """Roadmap generation request model"""
    target_role: str
    experience_level: str = "intermediate"
    focus_areas: List[str] = []
    duration_weeks: int = 12
    learning_style: str = "balanced"
    time_per_week: int = 20
    
    class Config:
        schema_extra = {
            "example": {
                "target_role": "Full Stack Developer",
                "experience_level": "intermediate",
                "focus_areas": ["React", "Node.js", "MongoDB"],
                "duration_weeks": 16,
                "learning_style": "project-based",
                "time_per_week": 20
            }
        }

class RoadmapTopicResponse(BaseModel):
    """Roadmap topic response model"""
    id: str
    title: str
    description: str
    difficulty: str
    estimated_hours: int
    status: str
    progress_percentage: int
    created_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "title": "Python Fundamentals",
                "description": "Learn Python basics",
                "difficulty": "beginner",
                "estimated_hours": 20,
                "status": "completed",
                "progress_percentage": 100,
                "created_at": "2024-01-01T00:00:00Z"
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
    summary="Get All Roadmaps",
    description="Retrieve all roadmaps with optional filtering and pagination",
    responses={
        200: {
            "description": "Roadmaps retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Roadmaps retrieved successfully",
                        "roadmaps": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "title": "Python Backend Developer Roadmap",
                                "description": "Comprehensive roadmap to become a Python backend developer",
                                "target_role": "Backend Developer",
                                "duration_weeks": 12,
                                "difficulty": "intermediate",
                                "status": "in_progress",
                                "progress_percentage": 65,
                                "total_topics": 20,
                                "completed_topics": 13,
                                "ai_generated": False,
                                "user_id": "user-456",
                                "created_at": "2024-01-01T00:00:00Z",
                                "updated_at": "2024-01-01T00:00:00Z",
                                "started_at": "2024-01-01T00:00:00Z",
                                "completed_at": None
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
                    "example": {"detail": "Failed to retrieve roadmaps: Database error"}
                }
            }
        }
    }
)
async def get_roadmaps(
    skip: int = Query(0, ge=0, description="Number of roadmaps to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of roadmaps to return (1-100)"),
    user_id: Optional[str] = Query(None, description="Filter roadmaps by user ID"),
    status: Optional[str] = Query(None, description="Filter roadmaps by status")
):
    """Get all roadmaps with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT r.id, r.title, r.description, r.target_role, r.duration_weeks,
                   r.difficulty, r.status, r.progress_percentage, r.total_topics,
                   r.completed_topics, r.ai_generated, r.user_id, r.created_at,
                   r.updated_at, r.started_at, r.completed_at
            FROM roadmaps r
            WHERE 1=1
        """
        params = []
        
        if user_id:
            query += " AND r.user_id = %s"
            params.append(user_id)
            
        if status:
            query += " AND r.status = %s"
            params.append(status)
        
        query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        roadmaps_data = cursor.fetchall()
        
        # Format the response
        roadmaps = []
        for row in roadmaps_data:
            roadmap = {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2],
                "target_role": row[3],
                "duration_weeks": row[4],
                "difficulty": row[5],
                "status": row[6],
                "progress_percentage": row[7],
                "total_topics": row[8],
                "completed_topics": row[9],
                "ai_generated": row[10],
                "user_id": str(row[11]),
                "created_at": row[12].isoformat() if row[12] else None,
                "updated_at": row[13].isoformat() if row[13] else None,
                "started_at": row[14].isoformat() if row[14] else None,
                "completed_at": row[15].isoformat() if row[15] else None
            }
            roadmaps.append(roadmap)
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Roadmaps retrieved successfully",
            "roadmaps": roadmaps,
            "total": len(roadmaps)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve roadmaps: {str(e)}"
        )

@router.get(
    "/{roadmap_id}",
    response_model=Dict[str, Any],
    summary="Get Roadmap by ID",
    description="Retrieve a specific roadmap by its UUID including all details and progress",
    responses={
        200: {
            "description": "Roadmap retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Roadmap retrieved successfully",
                        "roadmap": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "title": "Python Backend Developer Roadmap",
                            "description": "Comprehensive roadmap to become a Python backend developer",
                            "target_role": "Backend Developer",
                            "duration_weeks": 12,
                            "difficulty": "intermediate",
                            "status": "in_progress",
                            "progress_percentage": 65,
                            "total_topics": 20,
                            "completed_topics": 13,
                            "ai_generated": False,
                            "user_id": "user-456",
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                            "started_at": "2024-01-01T00:00:00Z",
                            "completed_at": None
                        }
                    }
                }
            }
        },
        404: {
            "description": "Roadmap not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Roadmap not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve roadmap: Database error"}
                }
            }
        }
    }
)
async def get_roadmap(
    roadmap_id: str = Path(..., description="UUID of the roadmap to retrieve")
):
    """Get roadmap by ID from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.id, r.title, r.description, r.target_role, r.duration_weeks,
                   r.difficulty, r.status, r.progress_percentage, r.total_topics,
                   r.completed_topics, r.ai_generated, r.user_id, r.created_at,
                   r.updated_at, r.started_at, r.completed_at
            FROM roadmaps r
            WHERE r.id = %s
        """, (str(roadmap_id),))
        
        roadmap_data = cursor.fetchone()
        
        if not roadmap_data:
            raise HTTPException(
                status_code=404,
                detail="Roadmap not found"
            )
        
        roadmap = {
            "id": str(roadmap_data[0]),
            "title": roadmap_data[1],
            "description": roadmap_data[2],
            "target_role": roadmap_data[3],
            "duration_weeks": roadmap_data[4],
            "difficulty": roadmap_data[5],
            "status": roadmap_data[6],
            "progress_percentage": roadmap_data[7],
            "total_topics": roadmap_data[8],
            "completed_topics": roadmap_data[9],
            "ai_generated": roadmap_data[10],
            "user_id": str(roadmap_data[11]),
            "created_at": roadmap_data[12].isoformat() if roadmap_data[12] else None,
            "updated_at": roadmap_data[13].isoformat() if roadmap_data[13] else None,
            "started_at": roadmap_data[14].isoformat() if roadmap_data[14] else None,
            "completed_at": roadmap_data[15].isoformat() if roadmap_data[15] else None
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Roadmap retrieved successfully",
            "roadmap": roadmap
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve roadmap: {str(e)}"
        )

@router.post(
    "/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create Roadmap",
    description="Create a new learning roadmap with specified parameters and goals",
    responses={
        201: {
            "description": "Roadmap created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Roadmap created successfully",
                        "roadmap_id": "123e4567-e89b-12d3-a456-426614174003",
                        "title": "Python Backend Developer Roadmap",
                        "target_role": "Backend Developer"
                    }
                }
            }
        },
        400: {
            "description": "Bad request - Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid user ID"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to create roadmap: Database error"}
                }
            }
        }
    }
)
async def create_roadmap(roadmap_data: RoadmapCreate):
    """
    Create a new roadmap
    
    **Request Body:**
    ```json
    {
        "title": "Python Backend Developer Roadmap",
        "description": "Comprehensive roadmap to become a Python backend developer",
        "target_role": "Backend Developer",
        "duration_weeks": 12,
        "difficulty": "intermediate",
        "user_id": "user-uuid",
        "ai_generated": false,
        "generation_prompt": "Create a roadmap for Python backend development"
    }
    ```
    
    **Required Fields:**
    - `title` (string): Roadmap title
    - `target_role` (string): Target role/position
    - `user_id` (string): User ID
    
    **Optional Fields:**
    - `description` (string): Roadmap description
    - `duration_weeks` (integer): Duration in weeks
    - `difficulty` (string): "beginner" | "intermediate" | "advanced" | "expert"
    - `ai_generated` (boolean): Whether AI generated
    - `generation_prompt` (string): AI generation prompt
    
    Returns the created roadmap details with generated ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO roadmaps (title, description, target_role, duration_weeks, difficulty,
                                status, progress_percentage, total_topics, completed_topics,
                                ai_generated, generation_prompt, user_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (
            roadmap_data.title,
            roadmap_data.description,
            roadmap_data.target_role,
            roadmap_data.duration_weeks,
            roadmap_data.difficulty,
            "not_started",
            0,
            0,
            0,
            roadmap_data.ai_generated,
            roadmap_data.generation_prompt,
            roadmap_data.user_id
        ))
        
        roadmap_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Roadmap created successfully",
            "roadmap_id": str(roadmap_id),
            "title": roadmap_data.title,
            "target_role": roadmap_data.target_role
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create roadmap: {str(e)}"
        )

@router.get(
    "/{roadmap_id}/topics",
    response_model=Dict[str, Any],
    summary="Get Roadmap Topics",
    description="Retrieve all topics associated with a specific roadmap",
    responses={
        200: {
            "description": "Roadmap topics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Roadmap topics retrieved successfully",
                        "roadmap_id": "123e4567-e89b-12d3-a456-426614174000",
                        "topics": [
                            {
                                "id": "456e7890-e89b-12d3-a456-426614174001",
                                "title": "Python Fundamentals",
                                "description": "Learn Python basics",
                                "difficulty": "beginner",
                                "estimated_hours": 20,
                                "status": "completed",
                                "progress_percentage": 100,
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "total": 1
                    }
                }
            }
        },
        404: {
            "description": "Roadmap not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Roadmap not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve roadmap topics: Database error"}
                }
            }
        }
    }
)
async def get_roadmap_topics(
    roadmap_id: str = Path(..., description="UUID of the roadmap to get topics for")
):
    """Get roadmap topics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rt.id, rt.title, rt.description, rt.difficulty, rt.estimated_hours,
                   rt.status, rt.progress_percentage, rt.created_at
            FROM roadmap_topics rt
            WHERE rt.roadmap_id = %s
            ORDER BY rt.created_at
        """, (str(roadmap_id),))
        
        topics_data = cursor.fetchall()
        
        topics = []
        for row in topics_data:
            topic = {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2],
                "difficulty": row[3],
                "estimated_hours": row[4],
                "status": row[5],
                "progress_percentage": row[6],
                "created_at": row[7].isoformat() if row[7] else None
            }
            topics.append(topic)
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Roadmap topics retrieved successfully",
            "roadmap_id": str(roadmap_id),
            "topics": topics,
            "total": len(topics)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve roadmap topics: {str(e)}"
        )

@router.post("/{roadmap_id}/topics")
async def create_roadmap_topic(roadmap_id: str):
    """Create topic for roadmap"""
    return {
        "message": f"Create topic for roadmap {roadmap_id}",
        "status": "created"
    }

@router.put(
    "/{roadmap_id}",
    response_model=Dict[str, Any],
    summary="Update Roadmap",
    description="Update roadmap information and progress tracking",
    responses={
        200: {
            "description": "Roadmap updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Roadmap updated successfully",
                        "roadmap_id": "123e4567-e89b-12d3-a456-426614174000",
                        "updated_fields": ["title", "duration_weeks", "status"]
                    }
                }
            }
        },
        404: {
            "description": "Roadmap not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Roadmap not found"}
                }
            }
        },
        400: {
            "description": "Bad request - Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid status value"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to update roadmap: Database error"}
                }
            }
        }
    }
)
async def update_roadmap(
    roadmap_id: str = Path(..., description="UUID of the roadmap to update"),
    roadmap_data: RoadmapUpdate = Body(...)
):
    """Update roadmap"""
    return {
        "message": f"Update roadmap {roadmap_id}",
        "status": "updated"
    }

@router.delete(
    "/{roadmap_id}",
    response_model=Dict[str, Any],
    summary="Delete Roadmap",
    description="Delete a roadmap and its associated topics and progress data",
    responses={
        200: {
            "description": "Roadmap deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Roadmap deleted successfully",
                        "roadmap_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        },
        404: {
            "description": "Roadmap not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Roadmap not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to delete roadmap: Database error"}
                }
            }
        }
    }
)
async def delete_roadmap(
    roadmap_id: str = Path(..., description="UUID of the roadmap to delete")
):
    """Delete roadmap"""
    return {
        "message": f"Delete roadmap {roadmap_id}",
        "status": "deleted"
    }
