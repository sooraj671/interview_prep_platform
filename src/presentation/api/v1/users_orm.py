"""
Users API Endpoints - SQLAlchemy ORM Version
User management and profile operations using SQLAlchemy ORM
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID

from infrastructure.database.sqlalchemy_connection import get_db_session
from infrastructure.repositories import get_repository_factory
from application.use_cases.user import (
    CreateUserUseCase,
    GetUserUseCase,
    GetUserByEmailUseCase,
    GetUsersUseCase,
    CountUsersUseCase
)
from shared.exceptions.domain_exceptions import (
    NotFoundException,
    DuplicateResourceException,
    ValidationException,
    DatabaseException
)

# Pydantic models for request/response
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/users", tags=["Users"])

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

# Exception handler
def handle_domain_exception(exc: Exception):
    """Convert domain exceptions to HTTP exceptions"""
    if isinstance(exc, NotFoundException):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    elif isinstance(exc, DuplicateResourceException):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )
    elif isinstance(exc, ValidationException):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        )
    elif isinstance(exc, DatabaseException):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

def user_to_response(user) -> UserResponse:
    """Convert user entity to response model"""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        status=user.status.value,
        email_verified=user.email_verified,
        phone_verified=user.phone_verified,
        two_factor_enabled=user.two_factor_enabled,
        created_at=user.created_at.isoformat() if user.created_at else "",
        updated_at=user.updated_at.isoformat() if user.updated_at else "",
        last_login=user.last_login.isoformat() if user.last_login else None,
        profile={
            "bio": user.profile.bio,
            "phone": user.profile.phone,
            "city": user.profile.city,
            "country": user.profile.country,
            "years_of_experience": user.profile.years_of_experience,
            "domain": user.profile.domain,
            "linkedin_url": user.profile.linkedin_url,
            "github_url": user.profile.github_url,
            "portfolio_url": user.profile.portfolio_url,
            "resume_url": user.profile.resume_url,
            "skills": user.profile.skills,
            "preferences": user.profile.preferences
        } if user.profile else None,
        stats={
            "total_assessments": user.stats.total_assessments,
            "completed_assessments": user.stats.completed_assessments,
            "average_score": user.stats.average_score,
            "total_study_time": user.stats.total_study_time,
            "current_streak": user.stats.current_streak,
            "longest_streak": user.stats.longest_streak,
            "skill_count": user.stats.skill_count,
            "roadmap_count": user.stats.roadmap_count,
            "last_active": user.stats.last_active.isoformat() if user.stats.last_active else None
        } if user.stats else None
    )

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Create a new user
    """
    try:
        # Get repository factory
        repo_factory = get_repository_factory(session)
        user_repo = repo_factory.user_repository()
        
        # Create use case
        create_user_use_case = CreateUserUseCase(user_repo)
        
        # Execute use case
        user = await create_user_use_case.execute(user_data.dict())
        
        return user_to_response(user)
        
    except Exception as e:
        handle_domain_exception(e)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID = Path(..., description="User ID"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get user by ID
    """
    try:
        # Get repository factory
        repo_factory = get_repository_factory(session)
        user_repo = repo_factory.user_repository()
        
        # Create use case
        get_user_use_case = GetUserUseCase(user_repo)
        
        # Execute use case
        user = await get_user_use_case.execute(user_id)
        
        return user_to_response(user)
        
    except Exception as e:
        handle_domain_exception(e)

@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str = Path(..., description="User email"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get user by email
    """
    try:
        # Get repository factory
        repo_factory = get_repository_factory(session)
        user_repo = repo_factory.user_repository()
        
        # Create use case
        get_user_by_email_use_case = GetUserByEmailUseCase(user_repo)
        
        # Execute use case
        user = await get_user_by_email_use_case.execute(email)
        
        return user_to_response(user)
        
    except Exception as e:
        handle_domain_exception(e)

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
    Get all users with pagination and filters
    """
    try:
        # Get repository factory
        repo_factory = get_repository_factory(session)
        user_repo = repo_factory.user_repository()
        
        # Create use cases
        get_users_use_case = GetUsersUseCase(user_repo)
        count_users_use_case = CountUsersUseCase(user_repo)
        
        # Execute use cases
        users = await get_users_use_case.execute(skip, limit, role, status, search)
        total = await count_users_use_case.execute(role, status, search)
        
        return UsersListResponse(
            users=[user_to_response(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        handle_domain_exception(e)

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
        # Get repository factory
        repo_factory = get_repository_factory(session)
        user_repo = repo_factory.user_repository()
        
        # Create use case
        count_users_use_case = CountUsersUseCase(user_repo)
        
        # Execute use case
        count = await count_users_use_case.execute(role, status, search)
        
        return {"count": count}
        
    except Exception as e:
        handle_domain_exception(e)
