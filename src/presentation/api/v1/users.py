"""
Users API endpoints
User management and profile operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr
import psycopg2

router = APIRouter(prefix="/users", tags=["Users"])

# Pydantic models for request/response
class UserCreate(BaseModel):
    """User creation request model"""
    email: str
    password_hash: str
    first_name: str
    last_name: str
    role: str = "candidate"
    auth_provider: str = "email"
    provider_id: Optional[str] = None
    bio: str = ""
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    years_of_experience: Optional[int] = None
    domain: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    skills: List[str] = []
    preferences: Dict[str, Any] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password_hash": "hashed_password_here",
                "first_name": "John",
                "last_name": "Doe",
                "role": "candidate",
                "auth_provider": "email",
                "bio": "Software developer with 5 years experience",
                "phone": "+1234567890",
                "city": "San Francisco",
                "country": "USA",
                "years_of_experience": 5,
                "domain": "backend",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "github_url": "https://github.com/johndoe",
                "portfolio_url": "https://johndoe.dev",
                "resume_url": "https://johndoe.dev/resume.pdf",
                "skills": ["Python", "JavaScript", "PostgreSQL"],
                "preferences": {"notifications": True, "theme": "dark"}
            }
        }

class UserUpdate(BaseModel):
    """User update request model"""
    email: Optional[str] = None
    password_hash: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    years_of_experience: Optional[int] = None
    domain: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    skills: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "John Updated",
                "bio": "Updated bio",
                "years_of_experience": 6,
                "skills": ["Python", "JavaScript", "React", "PostgreSQL"]
            }
        }

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    first_name: str
    last_name: str
    created_at: str
    updated_at: str
    profile: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "profile": {
                    "bio": "Software developer with 5 years experience",
                    "phone": "+1234567890",
                    "city": "San Francisco",
                    "country": "USA",
                    "years_of_experience": 5,
                    "domain": "backend"
                }
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
    summary="Get All Users",
    description="Retrieve all users from the database with optional pagination and filtering",
    responses={
        200: {
            "description": "Users retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Users retrieved successfully",
                        "users": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "email": "john.doe@example.com",
                                "first_name": "John",
                                "last_name": "Doe",
                                "created_at": "2024-01-01T00:00:00Z",
                                "updated_at": "2024-01-01T00:00:00Z",
                                "profile": {
                                    "bio": "Software developer with 5 years experience",
                                    "phone": "+1234567890",
                                    "city": "San Francisco",
                                    "country": "USA",
                                    "years_of_experience": 5,
                                    "domain": "backend"
                                }
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
                    "example": {"detail": "Failed to retrieve users: Database error"}
                }
            }
        }
    }
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of users to return"),
    domain: Optional[str] = Query(None, description="Filter users by domain")
):
    """Get all users from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query users with their profiles and stats using base tables
        cursor.execute("""
            SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.status, 
                   COALESCE(u.email_verified, false) as email_verified,
                   COALESCE(u.phone_verified, false) as phone_verified,
                   COALESCE(u.two_factor_enabled, false) as two_factor_enabled,
                   u.created_at, u.updated_at, u.last_login,
                   up.bio, up.phone, up.city, up.country, up.years_of_experience, up.domain, 
                   up.linkedin_url, up.github_url, up.portfolio_url, up.resume_url, up.skills, up.preferences,
                   COALESCE(us.total_assessments, 0) as total_assessments,
                   COALESCE(us.completed_assessments, 0) as completed_assessments,
                   COALESCE(us.average_score, 0.0) as average_score,
                   COALESCE(us.total_study_time, 0) as total_study_time,
                   COALESCE(us.current_streak, 0) as current_streak,
                   COALESCE(us.longest_streak, 0) as longest_streak,
                   COALESCE(us.skill_count, 0) as skill_count,
                   COALESCE(us.roadmap_count, 0) as roadmap_count
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            LEFT JOIN user_stats us ON u.id = us.user_id
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, skip))
        
        users_data = cursor.fetchall()
        
        # Format the response
        users = []
        for row in users_data:
            user = {
                "id": str(row[0]),
                "email": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "role": row[4],
                "status": row[5],
                "email_verified": row[6],
                "phone_verified": row[7],
                "two_factor_enabled": row[8],
                "created_at": row[9].isoformat() if row[9] else None,
                "updated_at": row[10].isoformat() if row[10] else None,
                "last_login": row[11].isoformat() if row[11] else None,
                "profile": {
                    "bio": row[12],
                    "phone": row[13],
                    "city": row[14],
                    "country": row[15],
                    "years_of_experience": row[16],
                    "domain": row[17],
                    "linkedin_url": row[18],
                    "github_url": row[19],
                    "portfolio_url": row[20],
                    "resume_url": row[21],
                    "skills": row[22],
                    "preferences": row[23]
                } if row[12] or row[13] or row[14] else None,
                "stats": {
                    "total_assessments": row[24],
                    "completed_assessments": row[25],
                    "average_score": float(row[26]) if row[26] else 0.0,
                    "total_study_time": row[27],
                    "current_streak": row[28],
                    "longest_streak": row[29],
                    "skill_count": row[30],
                    "roadmap_count": row[31]
                }
            }
            users.append(user)
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Users retrieved successfully",
            "users": users,
            "total": len(users)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.get(
    "/{user_id}",
    response_model=Dict[str, Any],
    summary="Get User by ID",
    description="Retrieve a specific user by their UUID including profile information",
    responses={
        200: {
            "description": "User retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User retrieved successfully",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "john.doe@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                            "profile": {
                                "bio": "Software developer with 5 years experience",
                                "phone": "+1234567890",
                                "city": "San Francisco",
                                "country": "USA",
                                "years_of_experience": 5,
                                "domain": "backend"
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
                    "example": {"detail": "Failed to retrieve user: Database error"}
                }
            }
        }
    }
)
async def get_user(
    user_id: str = Path(..., description="UUID of the user to retrieve")
):
    """Get user by ID from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query specific user with profile
        cursor.execute("""
            SELECT u.id, u.email, u.created_at, u.updated_at, u.first_name, u.last_name,
                   up.bio, up.phone, up.city, up.country, up.years_of_experience, up.domain
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            WHERE u.id = %s
        """, (str(user_id),))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        user = {
            "id": str(user_data[0]),
            "email": user_data[1],
            "created_at": user_data[2].isoformat() if user_data[2] else None,
            "updated_at": user_data[3].isoformat() if user_data[3] else None,
            "first_name": user_data[4],
            "last_name": user_data[5],
            "profile": {
                "bio": user_data[6],
                "phone": user_data[7],
                "city": user_data[8],
                "country": user_data[9],
                "years_of_experience": user_data[10],
                "domain": user_data[11]
            } if user_data[6] or user_data[7] or user_data[8] else None
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "User retrieved successfully",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user: {str(e)}"
        )

@router.post(
    "/",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Create a new user with profile information in the database",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User created successfully",
                        "user_id": "123e4567-e89b-12d3-a456-426614174003",
                        "email": "john.doe@example.com",
                        "first_name": "John",
                        "last_name": "Doe"
                    }
                }
            }
        },
        400: {
            "description": "Bad request - Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already exists"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to create user: Database error"}
                }
            }
        }
    }
)
async def create_user(user_data: UserCreate):
    """
    Create a new user
    
    **Request Body:**
    ```json
    {
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "Software developer with 5 years experience",
        "phone": "+1234567890",
        "city": "San Francisco",
        "country": "USA",
        "years_of_experience": 5,
        "domain": "backend"
    }
    ```
    
    **Required Fields:**
    - `email` (string): User email address
    - `password_hash` (string): Hashed password
    - `first_name` (string): User first name
    - `last_name` (string): User last name
    
    **Optional Fields:**
    - `role` (string): User role (default: "candidate")
    - `auth_provider` (string): Auth provider (default: "email")
    - `provider_id` (string): Provider ID
    - `bio` (string): User biography
    - `phone` (string): Phone number
    - `city` (string): City
    - `country` (string): Country
    - `years_of_experience` (integer): Years of experience
    - `domain` (string): Professional domain
    - `linkedin_url` (string): LinkedIn URL
    - `github_url` (string): GitHub URL
    - `portfolio_url` (string): Portfolio URL
    - `resume_url` (string): Resume URL
    - `skills` (array): List of skills
    - `preferences` (object): User preferences
    
    Returns the created user details with generated ID
    """
    print(f"DEBUG: Received user_data: {user_data}")
    print(f"DEBUG: user_data type: {type(user_data)}")
    print(f"DEBUG: user_data dict: {user_data.dict() if hasattr(user_data, 'dict') else 'N/A'}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"Email '{user_data.email}' already exists"
            )
        
        # Insert user with required fields from schema
        cursor.execute("""
            INSERT INTO users (
                email,
                password_hash,
                first_name,
                last_name,
                role,
                email_verified
            )
            VALUES (
                'test.useasdr@example.com',
                '$2b$12$abcdefghijklmnopqrstuv', -- dummy bcrypt-style hash
                'Test',
                'User',
                'candidate',
                TRUE
            )
            RETURNING id;
        """)

        # user_id = cursor.fetchone()[0]
        # conn.commit()

        
        # user_id = cursor.fetchone()[0] if cursor.fetchone() else None
        
        # # Insert user profile
        # cursor.execute("""
        #     INSERT INTO user_profiles (user_id, bio, phone, city, country, years_of_experience, 
        #                             domain, linkedin_url, github_url, portfolio_url, resume_url, 
        #                             skills, preferences)
        #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        # """, (
        #     user_id,
        #     user_data.bio,
        #     user_data.phone,
        #     user_data.city,
        #     user_data.country,
        #     user_data.years_of_experience,
        #     user_data.domain,
        #     user_data.linkedin_url,
        #     user_data.github_url,
        #     user_data.portfolio_url,
        #     user_data.resume_url,
        #     user_data.skills,
        #     user_data.preferences
        # ))
        
        # # Insert user stats with defaults
        # cursor.execute("""
        #     INSERT INTO user_stats (user_id, total_assessments, completed_assessments, average_score,
        #                          total_study_time, current_streak, longest_streak, skill_count, roadmap_count)
        #     VALUES (%s, 0, 0, 0.0, 0, 0, 0, 0, 0)
        # """, (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "message": "User created successfully",
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name
        }
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"❌ Database Error: {e}")
        print(f"❌ Error Type: {type(e)}")
        print(f"❌ Error Args: {e.args}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get(
    "/{user_id}/profile",
    response_model=Dict[str, Any],
    summary="Get User Profile",
    description="Retrieve detailed profile information for a specific user",
    responses={
        200: {
            "description": "Profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Profile retrieved successfully",
                        "profile": {
                            "bio": "Software developer with 5 years experience",
                            "phone": "+1234567890",
                            "city": "San Francisco",
                            "country": "USA",
                            "years_of_experience": 5,
                            "domain": "backend",
                            "linkedin_url": "https://linkedin.com/in/johndoe",
                            "github_url": "https://github.com/johndoe",
                            "portfolio_url": "https://johndoe.dev",
                            "resume_url": "https://example.com/resume.pdf",
                            "skills": ["Python", "JavaScript", "PostgreSQL"],
                            "preferences": {
                                "notifications": True,
                                "theme": "dark"
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "User or profile not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Profile not found"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to retrieve profile: Database error"}
                }
            }
        }
    }
)
async def get_user_profile(
    user_id: str = Path(..., description="UUID of the user to get profile for")
):
    """Get user profile"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT up.bio, up.phone, up.city, up.country, up.years_of_experience, up.domain,
                   up.linkedin_url, up.github_url, up.portfolio_url, up.resume_url, up.skills, up.preferences
            FROM user_profiles up
            WHERE up.user_id = %s
        """, (str(user_id),))
        
        profile_data = cursor.fetchone()
        
        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail="User profile not found"
            )
        
        profile = {
            "bio": profile_data[0],
            "phone": profile_data[1],
            "city": profile_data[2],
            "country": profile_data[3],
            "years_of_experience": profile_data[4],
            "domain": profile_data[5],
            "linkedin_url": profile_data[6],
            "github_url": profile_data[7],
            "portfolio_url": profile_data[8],
            "resume_url": profile_data[9],
            "skills": profile_data[10],
            "preferences": profile_data[11]
        }
        
        cursor.close()
        conn.close()
        
        return {
            "message": "Profile retrieved successfully",
            "profile": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve profile: {str(e)}"
        )

@router.get(
    "/{user_id}/stats",
    response_model=Dict[str, Any],
    summary="Get User Statistics",
    description="Retrieve statistics and progress information for a specific user",
    responses={
        200: {
            "description": "User stats retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User stats retrieved successfully",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "stats": {
                            "skills_in_progress": 3,
                            "assessments_completed": 5,
                            "roadmaps_started": 2,
                            "total_study_time": 1200,
                            "average_score": 85.5,
                            "skill_mastery": {
                                "Python": 7,
                                "JavaScript": 5,
                                "PostgreSQL": 6
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
                    "example": {"detail": "Failed to retrieve user stats: Database error"}
                }
            }
        }
    }
)
async def get_user_stats(
    user_id: str = Path(..., description="UUID of the user to get stats for")
):
    """Get user statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user stats from various tables
        stats = {}
        
        # Skill progress count
        cursor.execute("""
            SELECT COUNT(*) FROM user_skill_progress WHERE user_id = %s
        """, (str(user_id),))
        stats["skills_in_progress"] = cursor.fetchone()[0]
        
        # Assessment count
        cursor.execute("""
            SELECT COUNT(*) FROM assessment_responses WHERE user_id = %s
        """, (str(user_id),))
        stats["assessments_completed"] = cursor.fetchone()[0]
        
        # Roadmap progress
        cursor.execute("""
            SELECT COUNT(*) FROM roadmap_progress_view WHERE user_id = %s
        """, (str(user_id),))
        stats["roadmaps_started"] = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "message": "User stats retrieved successfully",
            "user_id": str(user_id),
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user stats: {str(e)}"
        )
