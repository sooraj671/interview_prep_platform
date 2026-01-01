from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid

from app.models.user import User, UserProfile, UserSkill, UserExperience, UserEducation
from app.models.skill import Skill
from app.schemas.user import (
    UserUpdate, UserWithProfileResponse, UserProfileUpdate,
    UserSkillCreate, UserSkillUpdate, UserExperienceCreate, UserExperienceUpdate,
    UserEducationCreate, UserEducationUpdate
)
from app.core.exceptions import NotFoundError, ValidationError

class UserService:
    """Service for user management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_with_profile(self, user_id: uuid.UUID) -> UserWithProfileResponse:
        """Get user with complete profile information."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        return UserWithProfileResponse(
            **user.__dict__,
            profile=user.profile,
            skills=user.skills,
            experiences=user.experiences,
            education=user.education
        )
    
    def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> User:
        """Update user information."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_profile(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Get user profile."""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def update_user_profile(self, user_id: uuid.UUID, profile_update: UserProfileUpdate) -> UserProfile:
        """Update user profile."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            # Create profile if it doesn't exist
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
        
        # Update fields
        update_data = profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    # Skills methods
    def get_user_skills(self, user_id: uuid.UUID) -> List[UserSkill]:
        """Get user's skills."""
        return self.db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    
    def add_user_skill(self, user_id: uuid.UUID, skill_create: UserSkillCreate) -> UserSkill:
        """Add skill to user's profile."""
        # Verify skill exists
        skill = self.db.query(Skill).filter(Skill.id == skill_create.skill_id).first()
        if not skill:
            raise NotFoundError("Skill not found")
        
        # Check if skill already exists for user
        existing_skill = self.db.query(UserSkill).filter(
            and_(UserSkill.user_id == user_id, UserSkill.skill_id == skill_create.skill_id)
        ).first()
        
        if existing_skill:
            raise ValidationError("Skill already added to profile")
        
        # Create user skill
        user_skill = UserSkill(
            user_id=user_id,
            skill_id=skill_create.skill_id,
            self_rating=skill_create.self_rating,
            confidence_level=skill_create.confidence_level
        )
        
        self.db.add(user_skill)
        self.db.commit()
        self.db.refresh(user_skill)
        return user_skill
    
    def update_user_skill(self, user_id: uuid.UUID, skill_id: str, skill_update: UserSkillUpdate) -> UserSkill:
        """Update user's skill."""
        user_skill = self.db.query(UserSkill).filter(
            and_(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        ).first()
        
        if not user_skill:
            raise NotFoundError("User skill not found")
        
        # Update fields
        update_data = skill_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user_skill, field, value)
        
        self.db.commit()
        self.db.refresh(user_skill)
        return user_skill
    
    def delete_user_skill(self, user_id: uuid.UUID, skill_id: str) -> None:
        """Delete user's skill."""
        user_skill = self.db.query(UserSkill).filter(
            and_(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        ).first()
        
        if not user_skill:
            raise NotFoundError("User skill not found")
        
        self.db.delete(user_skill)
        self.db.commit()
    
    # Experience methods
    def get_user_experiences(self, user_id: uuid.UUID) -> List[UserExperience]:
        """Get user's work experiences."""
        return self.db.query(UserExperience).filter(UserExperience.user_id == user_id).all()
    
    def add_user_experience(self, user_id: uuid.UUID, experience_create: UserExperienceCreate) -> UserExperience:
        """Add work experience to user's profile."""
        user_experience = UserExperience(
            user_id=user_id,
            **experience_create.dict()
        )
        
        self.db.add(user_experience)
        self.db.commit()
        self.db.refresh(user_experience)
        return user_experience
    
    def update_user_experience(self, user_id: uuid.UUID, experience_id: str, experience_update: UserExperienceUpdate) -> UserExperience:
        """Update user's work experience."""
        user_experience = self.db.query(UserExperience).filter(
            and_(UserExperience.user_id == user_id, UserExperience.id == experience_id)
        ).first()
        
        if not user_experience:
            raise NotFoundError("User experience not found")
        
        # Update fields
        update_data = experience_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user_experience, field, value)
        
        self.db.commit()
        self.db.refresh(user_experience)
        return user_experience
    
    def delete_user_experience(self, user_id: uuid.UUID, experience_id: str) -> None:
        """Delete user's work experience."""
        user_experience = self.db.query(UserExperience).filter(
            and_(UserExperience.user_id == user_id, UserExperience.id == experience_id)
        ).first()
        
        if not user_experience:
            raise NotFoundError("User experience not found")
        
        self.db.delete(user_experience)
        self.db.commit()
    
    # Education methods
    def get_user_education(self, user_id: uuid.UUID) -> List[UserEducation]:
        """Get user's education."""
        return self.db.query(UserEducation).filter(UserEducation.user_id == user_id).all()
    
    def add_user_education(self, user_id: uuid.UUID, education_create: UserEducationCreate) -> UserEducation:
        """Add education to user's profile."""
        user_education = UserEducation(
            user_id=user_id,
            **education_create.dict()
        )
        
        self.db.add(user_education)
        self.db.commit()
        self.db.refresh(user_education)
        return user_education
    
    def update_user_education(self, user_id: uuid.UUID, education_id: str, education_update: UserEducationUpdate) -> UserEducation:
        """Update user's education."""
        user_education = self.db.query(UserEducation).filter(
            and_(UserEducation.user_id == user_id, UserEducation.id == education_id)
        ).first()
        
        if not user_education:
            raise NotFoundError("User education not found")
        
        # Update fields
        update_data = education_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user_education, field, value)
        
        self.db.commit()
        self.db.refresh(user_education)
        return user_education
    
    def delete_user_education(self, user_id: uuid.UUID, education_id: str) -> None:
        """Delete user's education."""
        user_education = self.db.query(UserEducation).filter(
            and_(UserEducation.user_id == user_id, UserEducation.id == education_id)
        ).first()
        
        if not user_education:
            raise NotFoundError("User education not found")
        
        self.db.delete(user_education)
        self.db.commit()
