"""
Users ORM API - Updated Version
FastAPI router for user management using new SQLAlchemy ORM models
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr
from pydantic.email_validator import validate_email
from datetime import datetime

# Import new database configuration and models
from infrastructure.database.orm_dependencies import get_db_session
from infrastructure.database.models.user import User, UserProfile, UserStats

# Pydantic models
class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    role: str = "candidate"
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

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    status: str
    email_verified: bool
    phone_verified: bool
    two_factor_enabled: bool
    created_at: str
    updated_at: str
    last_login: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = None

class UsersListResponse(BaseModel):
    """Users list response model"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

def user_to_response(user) -> UserResponse:
    """Convert user entity to response model - simplified version"""
    try:
        # Get profile data safely
        profile_data = None
        if hasattr(user, 'profile') and user.profile:
            profile_data = {
                "bio": getattr(user.profile, 'bio', ''),
                "phone": getattr(user.profile, 'phone', None),
                "city": getattr(user.profile, 'city', None),
                "country": getattr(user.profile, 'country', None),
                "years_of_experience": getattr(user.profile, 'years_of_experience', None),
                "domain": getattr(user.profile, 'domain', None),
                "linkedin_url": getattr(user.profile, 'linkedin_url', None),
                "github_url": getattr(user.profile, 'github_url', None),
                "portfolio_url": getattr(user.profile, 'portfolio_url', None),
                "resume_url": getattr(user.profile, 'resume_url', None),
                "skills": getattr(user.profile, 'skills', []),
                "preferences": getattr(user.profile, 'preferences', {})
            }
        
        # Get stats data safely
        stats_data = None
        if hasattr(user, 'stats') and user.stats:
            stats_data = {
                "total_assessments": getattr(user.stats, 'total_assessments', 0),
                "completed_assessments": getattr(user.stats, 'completed_assessments', 0),
                "average_score": float(getattr(user.stats, 'average_score', 0.0)),
                "total_study_time": getattr(user.stats, 'total_study_time', 0),
                "current_streak": getattr(user.stats, 'current_streak', 0),
                "longest_streak": getattr(user.stats, 'longest_streak', 0),
                "skill_count": getattr(user.stats, 'skill_count', 0),
                "roadmap_count": getattr(user.stats, 'roadmap_count', 0),
                "last_active": getattr(user.stats, 'last_active', None)
            }
            if stats_data["last_active"]:
                stats_data["last_active"] = stats_data["last_active"].isoformat()
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            status=user.status,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at.isoformat() if user.created_at else "",
            updated_at=user.updated_at.isoformat() if user.updated_at else "",
            last_login=user.last_login.isoformat() if user.last_login else None,
            profile=profile_data,
            stats=stats_data
        )
    except Exception as e:
        # Fallback response if conversion fails
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            status=user.status,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at.isoformat() if user.created_at else "",
            updated_at=user.updated_at.isoformat() if user.updated_at else "",
            last_login=user.last_login.isoformat() if user.last_login else None,
            profile=None,
            stats=None
        )

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "module": "users_orm_simple"}

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Create a new user using SQLAlchemy ORM - with error handling
    """
    try:
        # Check if user already exists
        existing_stmt = select(User).where(User.email == user_data.email)
        existing_result = await session.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=user_data.password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            auth_provider="email",
            provider_id=None,
            status="pending_verification",
            email_verified=False,
            phone_verified=False,
            two_factor_enabled=False
        )
        
        session.add(user)
        await session.flush()  # Get the ID
        
        # Create profile
        profile = UserProfile(
            user_id=user.id,
            bio=user_data.bio,
            phone=user_data.phone,
            city=user_data.city,
            country=user_data.country,
            years_of_experience=user_data.years_of_experience,
            domain=user_data.domain,
            linkedin_url=user_data.linkedin_url,
            github_url=user_data.github_url,
            portfolio_url=user_data.portfolio_url,
            resume_url=user_data.resume_url,
            skills=user_data.skills or [],
            preferences=user_data.preferences or {}
        )
        
        session.add(profile)
        
        # Create stats
        stats = UserStats(
            user_id=user.id,
            total_assessments=0,
            completed_assessments=0,
            average_score=0.0,
            total_study_time=0,
            current_streak=0,
            longest_streak=0,
            skill_count=len(user_data.skills) if user_data.skills else 0,
            roadmap_count=0
        )
        
        session.add(stats)
        await session.commit()
        
        return user_to_response(user)
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

@router.get("/", response_model=UsersListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name and email"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get all users with pagination and filters - simplified version
    """
    try:
        # Simple query without eager loading to avoid issues
        stmt = select(User).offset(skip).limit(limit)
        
        # Apply filters
        filters = []
        if role:
            filters.append(User.role == role)
        if status:
            filters.append(User.status == status)
        if search:
            filters.append(
                or_(
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        # Order by created_at
        stmt = stmt.order_by(User.created_at.desc())
        
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        # Simple count query
        count_stmt = select(User)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        
        count_result = await session.execute(count_stmt)
        total = len(count_result.scalars().all())
        
        return UsersListResponse(
            users=[user_to_response(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID = Path(..., description="User ID"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get user by ID using SQLAlchemy ORM
    """
    try:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        return user_to_response(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

@router.get("/count", response_model=Dict[str, int])
async def count_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name and email"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Count users with filters
    """
    try:
        stmt = select(User)
        
        # Apply filters
        filters = []
        if role:
            filters.append(User.role == role)
        if status:
            filters.append(User.status == status)
        if search:
            filters.append(
                or_(
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        result = await session.execute(stmt)
        count = len(result.scalars().all())
        
        return {"count": count}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
