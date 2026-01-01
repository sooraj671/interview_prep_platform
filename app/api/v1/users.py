from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse, UserUpdate, UserWithProfileResponse,
    UserProfileResponse, UserProfileUpdate,
    UserSkillResponse, UserSkillCreate, UserSkillUpdate,
    UserExperienceResponse, UserExperienceCreate, UserExperienceUpdate,
    UserEducationResponse, UserEducationCreate, UserEducationUpdate
)
from app.services.user_service import UserService
from app.dependencies import get_current_user, require_candidate_user
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()

@router.get("/me", response_model=UserWithProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's complete profile."""
    user_service = UserService(db)
    return user_service.get_user_with_profile(current_user.id)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update current user information."""
    user_service = UserService(db)
    return user_service.update_user(current_user.id, user_update)

# Profile endpoints
@router.get("/me/profile", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's profile."""
    user_service = UserService(db)
    profile = user_service.get_user_profile(current_user.id)
    if not profile:
        raise NotFoundError("Profile not found")
    return profile

@router.put("/me/profile", response_model=UserProfileResponse)
async def update_my_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update current user's profile."""
    user_service = UserService(db)
    return user_service.update_user_profile(current_user.id, profile_update)

# Skills endpoints
@router.get("/me/skills", response_model=List[UserSkillResponse])
async def get_my_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's skills."""
    user_service = UserService(db)
    return user_service.get_user_skills(current_user.id)

@router.post("/me/skills", response_model=UserSkillResponse)
async def add_my_skill(
    skill_create: UserSkillCreate,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Add a skill to current user's profile."""
    user_service = UserService(db)
    return user_service.add_user_skill(current_user.id, skill_create)

@router.put("/me/skills/{skill_id}", response_model=UserSkillResponse)
async def update_my_skill(
    skill_id: str,
    skill_update: UserSkillUpdate,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a skill in current user's profile."""
    user_service = UserService(db)
    return user_service.update_user_skill(current_user.id, skill_id, skill_update)

@router.delete("/me/skills/{skill_id}")
async def delete_my_skill(
    skill_id: str,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a skill from current user's profile."""
    user_service = UserService(db)
    user_service.delete_user_skill(current_user.id, skill_id)
    return {"message": "Skill deleted successfully"}

# Experience endpoints
@router.get("/me/experiences", response_model=List[UserExperienceResponse])
async def get_my_experiences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's work experiences."""
    user_service = UserService(db)
    return user_service.get_user_experiences(current_user.id)

@router.post("/me/experiences", response_model=UserExperienceResponse)
async def add_my_experience(
    experience_create: UserExperienceCreate,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Add work experience to current user's profile."""
    user_service = UserService(db)
    return user_service.add_user_experience(current_user.id, experience_create)

@router.put("/me/experiences/{experience_id}", response_model=UserExperienceResponse)
async def update_my_experience(
    experience_id: str,
    experience_update: UserExperienceUpdate,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update work experience in current user's profile."""
    user_service = UserService(db)
    return user_service.update_user_experience(current_user.id, experience_id, experience_update)

@router.delete("/me/experiences/{experience_id}")
async def delete_my_experience(
    experience_id: str,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete work experience from current user's profile."""
    user_service = UserService(db)
    user_service.delete_user_experience(current_user.id, experience_id)
    return {"message": "Experience deleted successfully"}

# Education endpoints
@router.get("/me/education", response_model=List[UserEducationResponse])
async def get_my_education(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's education."""
    user_service = UserService(db)
    return user_service.get_user_education(current_user.id)

@router.post("/me/education", response_model=UserEducationResponse)
async def add_my_education(
    education_create: UserEducationCreate,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Add education to current user's profile."""
    user_service = UserService(db)
    return user_service.add_user_education(current_user.id, education_create)

@router.put("/me/education/{education_id}", response_model=UserEducationResponse)
async def update_my_education(
    education_id: str,
    education_update: UserEducationUpdate,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update education in current user's profile."""
    user_service = UserService(db)
    return user_service.update_user_education(current_user.id, education_id, education_update)

@router.delete("/me/education/{education_id}")
async def delete_my_education(
    education_id: str,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete education from current user's profile."""
    user_service = UserService(db)
    user_service.delete_user_education(current_user.id, education_id)
    return {"message": "Education deleted successfully"}
