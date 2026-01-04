"""
Skills API endpoints
Skills management and assessment operations
"""
from fastapi import APIRouter, HTTPException, status, Query, Path, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
import psycopg2

router = APIRouter(prefix="/skills", tags=["Skills"])

# Pydantic models for request/response
class SkillCreate(BaseModel):
    """Skill creation request model"""
    name: str
    description: str = ""
    category: str
    difficulty: str = "intermediate"
    tags: List[str] = []
    prerequisites: List[str] = []
    related_skills: List[str] = []
    industry_relevance: Dict[str, Any] = {}
    average_salary_impact: Optional[float] = None
    learning_path: List[Dict[str, Any]] = []
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Python Programming",
                "description": "Learn Python programming fundamentals",
                "category": "programming",
                "difficulty": "intermediate",
                "tags": ["python", "programming", "backend"],
                "prerequisites": ["Basic computer skills"],
                "related_skills": ["JavaScript", "Django"],
                "industry_relevance": {"tech": 0.9, "finance": 0.7},
                "average_salary_impact": 15000.0,
                "learning_path": [
                    {"step": 1, "topic": "Variables", "duration": 2},
                    {"step": 2, "topic": "Control Flow", "duration": 3}
                ]
            }
        }

class SkillUpdate(BaseModel):
    """Skill update request model"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    related_skills: Optional[List[str]] = None
    industry_relevance: Optional[Dict[str, Any]] = None
    average_salary_impact: Optional[float] = None
    learning_path: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Python Programming Updated",
                "description": "Updated description",
                "difficulty": "advanced",
                "tags": ["python", "programming", "backend", "advanced"]
            }
        }

class SkillResponse(BaseModel):
    """Skill response model"""
    id: str
    name: str
    description: str
    category: str
    difficulty: str
    tags: List[str]
    prerequisites: List[str]
    related_skills: List[str]
    industry_relevance: Dict[str, Any]
    average_salary_impact: Optional[float]
    learning_path: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    is_active: bool
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Python Programming",
                "description": "Learn Python programming fundamentals",
                "category": "programming",
                "difficulty": "intermediate",
                "tags": ["python", "programming", "backend"],
                "prerequisites": ["Basic computer skills"],
                "related_skills": ["JavaScript", "Django"],
                "industry_relevance": {"tech": 0.9, "finance": 0.7},
                "average_salary_impact": 15000.0,
                "learning_path": [
                    {"step": 1, "topic": "Variables", "duration": 2},
                    {"step": 2, "topic": "Control Flow", "duration": 3}
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "is_active": True
            }
        }

class SkillTopicResponse(BaseModel):
    """Skill topic response model"""
    id: str
    name: str
    description: str
    difficulty: str
    estimated_hours: int
    prerequisites: List[str]
    learning_objectives: List[str]
    created_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "name": "Variables and Data Types",
                "description": "Understanding Python variables and data types",
                "difficulty": "beginner",
                "estimated_hours": 2,
                "prerequisites": [],
                "learning_objectives": [
                    "Understand variables",
                    "Learn data types"
                ],
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class SkillResourceResponse(BaseModel):
    """Skill resource response model"""
    id: str
    type: str
    title: str
    url: str
    description: str
    difficulty: str
    rating: float
    duration_hours: int
    cost: str
    provider: str
    created_at: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "type": "course",
                "title": "Python for Beginners",
                "url": "https://example.com/python-course",
                "description": "Comprehensive Python course",
                "difficulty": "beginner",
                "rating": 4.5,
                "duration_hours": 20,
                "cost": "Free",
                "provider": "Online Academy",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    related_skills: Optional[List[str]] = None
    industry_relevance: Optional[Dict[str, Any]] = None
    average_salary_impact: Optional[float] = None
    learning_path: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

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
    summary="Get All Skills",
    description="Retrieve all available skills with optional filtering and pagination",
    responses={
        200: {
            "description": "Skills retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Skills retrieved successfully",
                        "skills": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "name": "Python Programming",
                                "description": "Learn Python programming fundamentals",
                                "category": "programming",
                                "difficulty": "intermediate",
                                "tags": ["python", "programming", "backend"],
                                "prerequisites": ["Basic computer skills"],
                                "related_skills": ["JavaScript", "Django"],
                                "industry_relevance": {"tech": 0.9, "finance": 0.7},
                                "average_salary_impact": 15000.0,
                                "learning_path": [
                                    {"step": 1, "topic": "Variables", "duration": 2},
                                    {"step": 2, "topic": "Control Flow", "duration": 3}
                                ],
                                "created_at": "2024-01-01T00:00:00Z",
                                "updated_at": "2024-01-01T00:00:00Z",
                                "is_active": True
                            }
                        ],
                        "total": 1,
                        "skip": 0,
                        "limit": 50,
                        "filters": {
                            "category": None,
                            "difficulty": None
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve skills: Database error"}
                }
            }
        }
    }
)
async def get_skills(
    skip: int = Query(0, ge=0, description="Number of skills to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of skills to return (1-100)"),
    category: Optional[str] = Query(None, description="Filter skills by category"),
    difficulty: Optional[str] = Query(None, description="Filter skills by difficulty level")
):
    """
    Get all skills with optional filtering and pagination
    
    **Query Parameters:**
    - **skip**: Number of skills to skip for pagination (default: 0)
    - **limit**: Maximum number of skills to return (1-100, default: 50)
    - **category**: Filter by skill category (e.g., "programming", "database", "cloud")
    - **difficulty**: Filter by difficulty level ("beginner", "intermediate", "advanced", "expert")
    
    Returns a paginated list of skills with filtering options
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT s.id, s.name, s.description, s.category, s.difficulty,
                   s.tags, s.prerequisites, s.related_skills, s.industry_relevance,
                   s.average_salary_impact, s.learning_path, s.created_at, s.updated_at
            FROM skills s
            WHERE 1=1
        """
        params = []
        
        if category:
            query += " AND s.category = %s"
            params.append(category)
            
        if difficulty:
            query += " AND s.difficulty = %s"
            params.append(difficulty)
        
        query += " ORDER BY s.name LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        skills_data = cursor.fetchall()
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM skills s WHERE 1=1"
        count_params = []
        
        if category:
            count_query += " AND s.category = %s"
            count_params.append(category)
            
        if difficulty:
            count_query += " AND s.difficulty_level = %s"
            count_params.append(difficulty)
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        # Format the response
        skills = []
        for row in skills_data:
            skill = {
                "id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "category": row[3],
                "difficulty": row[4],
                "tags": row[5] if row[5] else [],
                "prerequisites": row[6] if row[6] else [],
                "related_skills": row[7] if row[7] else [],
                "industry_relevance": row[8] if row[8] else {},
                "average_salary_impact": row[9],
                "learning_path": row[10] if row[10] else [],
                "created_at": row[11].isoformat() if row[11] else None,
                "updated_at": row[12].isoformat() if row[12] else None
            }
            skills.append(skill)
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Skills retrieved successfully",
            "skills": skills,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "filters": {
                "category": category,
                "difficulty": difficulty
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve skills: {str(e)}"
        )

@router.get(
    "/{skill_id}",
    response_model=Dict[str, Any],
    summary="Get Skill by ID",
    description="Retrieve detailed information about a specific skill",
    responses={
        200: {
            "description": "Skill retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Skill retrieved successfully",
                        "skill": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Python Programming",
                            "description": "Learn Python programming fundamentals",
                            "category": "programming",
                            "difficulty": "intermediate",
                            "tags": ["python", "programming"],
                            "prerequisites": ["Basic computer skills"],
                            "related_skills": ["JavaScript", "Django"],
                            "industry_relevance": {"tech": 0.9, "finance": 0.7},
                            "average_salary_impact": 15000.0,
                            "learning_path": [{"step": 1, "topic": "Variables", "duration": 2}],
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                            "is_active": True
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
                    "example": {"detail": "Failed to retrieve skill: Database error"}
                }
            }
        }
    }
)
async def get_skill(
    skill_id: str = Path(..., description="UUID of the skill to retrieve")
):
    """
    Get skill by ID
    
    **Path Parameters:**
    - **skill_id**: Unique identifier of the skill (UUID)
    
    Returns detailed information about the specified skill including topics and resources
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query specific skill
        cursor.execute("""
            SELECT s.id, s.name, s.description, s.category, s.difficulty_level,
                   s.tags, s.prerequisites, s.related_skills, s.industry_relevance,
                   s.average_salary_impact, s.learning_path, s.created_at, s.updated_at, s.is_active
            FROM skills s
            WHERE s.id = %s
        """, (str(skill_id),))
        
        skill_data = cursor.fetchone()
        
        if not skill_data:
            raise HTTPException(
                status_code=404,
                detail="Skill not found"
            )
        
        skill = {
            "id": str(skill_data[0]),
            "name": skill_data[1],
            "description": skill_data[2],
            "category": skill_data[3],
            "difficulty": skill_data[4],
            "tags": skill_data[5] if skill_data[5] else [],
            "prerequisites": skill_data[6] if skill_data[6] else [],
            "related_skills": skill_data[7] if skill_data[7] else [],
            "industry_relevance": skill_data[8] if skill_data[8] else {},
            "average_salary_impact": skill_data[9],
            "learning_path": skill_data[10] if skill_data[10] else [],
            "created_at": skill_data[11].isoformat() if skill_data[11] else None,
            "updated_at": skill_data[12].isoformat() if skill_data[12] else None,
            "is_active": skill_data[13]
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Skill retrieved successfully",
            "skill": skill
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve skill: {str(e)}"
        )

@router.post(
    "/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create Skill",
    description="Create a new skill with detailed information and learning path",
    responses={
        201: {
            "description": "Skill created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Skill created successfully",
                        "skill_id": "123e4567-e89b-12d3-a456-426614174003",
                        "name": "Python Programming",
                        "category": "programming"
                    }
                }
            }
        },
        400: {
            "description": "Bad request - Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Skill name already exists"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to create skill: Database error"}
                }
            }
        }
    }
)
async def create_skill(skill_data: SkillCreate):
    """
    Create a new skill
    
    **Request Body:**
    ```json
    {
        "name": "Python Programming",
        "description": "Learn Python programming fundamentals",
        "category": "programming",
        "difficulty": "intermediate",
        "tags": ["python", "programming", "backend"],
        "prerequisites": ["Basic computer skills"],
        "related_skills": ["JavaScript", "Django"],
        "industry_relevance": {"tech": 0.9, "finance": 0.7},
        "average_salary_impact": 15000.0,
        "learning_path": [
            {"step": 1, "topic": "Variables", "duration": 2},
            {"step": 2, "topic": "Control Flow", "duration": 3}
        ]
    }
    ```
    
    **Required Fields:**
    - `name` (string): Skill name
    - `category` (string): Skill category from predefined values
    
    **Optional Fields:**
    - `description` (string): Detailed description
    - `difficulty` (string): "beginner" | "intermediate" | "advanced" | "expert"
    - `tags` (array): List of tags
    - `prerequisites` (array): List of prerequisite skills
    - `related_skills` (array): List of related skills
    - `industry_relevance` (object): Industry relevance scores
    - `average_salary_impact` (number): Salary impact in USD
    - `learning_path` (array): Structured learning path
    
    Returns the created skill details with generated ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert skill
        cursor.execute("""
            INSERT INTO skills (name, description, category, difficulty, tags, 
                               prerequisites, related_skills, industry_relevance, 
                               average_salary_impact, learning_path, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (
            skill_data.name,
            skill_data.description,
            skill_data.category,
            skill_data.difficulty,
            skill_data.tags,
            skill_data.prerequisites,
            skill_data.related_skills,
            skill_data.industry_relevance,
            skill_data.average_salary_impact,
            skill_data.learning_path
        ))
        
        skill_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Skill created successfully",
            "skill_id": str(skill_id),
            "name": skill_data.name,
            "category": skill_data.category
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create skill: {str(e)}"
        )

@router.put(
    "/{skill_id}",
    response_model=Dict[str, Any],
    summary="Update Skill",
    description="Update skill information and learning path details",
    responses={
        200: {
            "description": "Skill updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Skill updated successfully",
                        "skill_id": "123e4567-e89b-12d3-a456-426614174000",
                        "updated_fields": ["name", "description", "difficulty"]
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
        400: {
            "description": "Bad request - Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid difficulty level"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to update skill: Database error"}
                }
            }
        }
    }
)
async def update_skill(
    skill_id: str = Path(..., description="UUID of the skill to update"),
    skill_data: SkillUpdate = Body(...)
):
    """
    Update an existing skill
    
    **Path Parameters:**
    - **skill_id**: Unique identifier of the skill to update (UUID)
    
    **Request Body:**
    - Partial skill data to update (all fields optional)
    
    Returns the updated skill details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        params = []
        
        if skill_data.name is not None:
            update_fields.append("name = %s")
            params.append(skill_data.name)
        if skill_data.description is not None:
            update_fields.append("description = %s")
            params.append(skill_data.description)
        if skill_data.category is not None:
            update_fields.append("category = %s")
            params.append(skill_data.category)
        if skill_data.difficulty is not None:
            update_fields.append("difficulty_level = %s")
            params.append(skill_data.difficulty)
        if skill_data.tags is not None:
            update_fields.append("tags = %s")
            params.append(skill_data.tags)
        if skill_data.prerequisites is not None:
            update_fields.append("prerequisites = %s")
            params.append(skill_data.prerequisites)
        if skill_data.related_skills is not None:
            update_fields.append("related_skills = %s")
            params.append(skill_data.related_skills)
        if skill_data.industry_relevance is not None:
            update_fields.append("industry_relevance = %s")
            params.append(skill_data.industry_relevance)
        if skill_data.average_salary_impact is not None:
            update_fields.append("average_salary_impact = %s")
            params.append(skill_data.average_salary_impact)
        if skill_data.learning_path is not None:
            update_fields.append("learning_path = %s")
            params.append(skill_data.learning_path)
        if skill_data.is_active is not None:
            update_fields.append("is_active = %s")
            params.append(skill_data.is_active)
        
        if not update_fields:
            raise HTTPException(
                status_code=400,
                detail="No fields to update provided"
            )
        
        update_fields.append("updated_at = NOW()")
        params.append(str(skill_id))
        
        query = f"UPDATE skills SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, params)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Skill updated successfully",
            "skill_id": str(skill_id),
            "updated_fields": list(skill_data.dict(exclude_unset=True).keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update skill: {str(e)}"
        )

@router.delete(
    "/{skill_id}",
    response_model=Dict[str, Any],
    summary="Delete Skill",
    description="Delete a skill and its associated topics and resources",
    responses={
        200: {
            "description": "Skill deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Skill deleted successfully",
                        "skill_id": "123e4567-e89b-12d3-a456-426614174000"
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
                    "example": {"detail": "Failed to delete skill: Database error"}
                }
            }
        }
    }
)
async def delete_skill(
    skill_id: str = Path(..., description="UUID of the skill to delete")
):
    """
    Delete a skill
    
    **Path Parameters:**
    - **skill_id**: Unique identifier of the skill to delete (UUID)
    
    Performs a soft delete by setting is_active to false
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE skills SET is_active = false, updated_at = NOW()
            WHERE id = %s
        """, (str(skill_id),))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Skill not found"
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "Skill deleted successfully",
            "skill_id": str(skill_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete skill: {str(e)}"
        )

@router.get(
    "/{skill_id}/topics",
    response_model=Dict[str, Any],
    summary="Get Skill Topics",
    description="Retrieve all topics associated with a specific skill",
    responses={
        200: {
            "description": "Skill topics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Skill topics retrieved successfully",
                        "skill_id": "123e4567-e89b-12d3-a456-426614174000",
                        "topics": [
                            {
                                "id": "456e7890-e89b-12d3-a456-426614174001",
                                "name": "Variables and Data Types",
                                "description": "Understanding Python variables and data types",
                                "difficulty": "beginner",
                                "estimated_hours": 2,
                                "prerequisites": [],
                                "learning_objectives": [
                                    "Understand variables",
                                    "Learn data types"
                                ],
                                "created_at": "2024-01-01T00:00:00Z"
                            }
                        ],
                        "total": 1
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
                    "example": {"detail": "Failed to retrieve skill topics: Database error"}
                }
            }
        }
    }
)
async def get_skill_topics(
    skill_id: str = Path(..., description="UUID of the skill to get topics for")
):
    """
    Get topics for a specific skill
    
    **Path Parameters:**
    - **skill_id**: Unique identifier of the skill (UUID)
    
    Returns all available topics for the specified skill
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT st.id, st.name, st.description, st.difficulty, st.estimated_hours,
                   st.prerequisites, st.learning_objectives, st.created_at
            FROM skill_topics st
            WHERE st.skill_id = %s
            ORDER BY st.created_at
        """, (str(skill_id),))
        
        topics_data = cursor.fetchall()
        
        topics = []
        for row in topics_data:
            topic = {
                "id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "difficulty": row[3],
                "estimated_hours": row[4],
                "prerequisites": row[5] if row[5] else [],
                "learning_objectives": row[6] if row[6] else [],
                "created_at": row[7].isoformat() if row[7] else None
            }
            topics.append(topic)
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Skill topics retrieved successfully",
            "skill_id": str(skill_id),
            "topics": topics,
            "total": len(topics)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve skill topics: {str(e)}"
        )

@router.get(
    "/{skill_id}/resources",
    response_model=Dict[str, Any],
    summary="Get Skill Resources",
    description="Retrieve all learning resources associated with a specific skill",
    responses={
        200: {
            "description": "Skill resources retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Skill resources retrieved successfully",
                        "skill_id": "123e4567-e89b-12d3-a456-426614174000",
                        "resources": [
                            {
                                "id": "456e7890-e89b-12d3-a456-426614174001",
                                "type": "course",
                                "title": "Python for Beginners",
                                "url": "https://example.com/python-course",
                                "description": "Comprehensive Python course",
                                "difficulty": "beginner",
                                "rating": 4.5,
                                "duration_hours": 20,
                                "cost": "Free",
                                "provider": "Online Academy"
                            }
                        ],
                        "total": 1
                    }
                }
            }
        }
    }
)
async def get_skill_resources(skill_id: UUID):
    """
    Get learning resources for a specific skill
    
    **Path Parameters:**
    - **skill_id**: Unique identifier of the skill (UUID)
    
    Returns all available learning resources for the specified skill
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sr.id, sr.type, sr.title, sr.url, sr.description, sr.difficulty,
                   sr.rating, sr.duration_hours, sr.cost, sr.provider, sr.created_at
            FROM skill_resources sr
            WHERE sr.skill_id = %s
            ORDER BY sr.rating DESC
        """, (str(skill_id),))
        
        resources_data = cursor.fetchall()
        
        resources = []
        for row in resources_data:
            resource = {
                "id": str(row[0]),
                "type": row[1],
                "title": row[2],
                "url": row[3],
                "description": row[4],
                "difficulty": row[5],
                "rating": row[6],
                "duration_hours": row[7],
                "cost": row[8],
                "provider": row[9],
                "created_at": row[10].isoformat() if row[10] else None
            }
            resources.append(resource)
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Skill resources retrieved successfully",
            "skill_id": str(skill_id),
            "resources": resources,
            "total": len(resources)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve skill resources: {str(e)}"
        )
