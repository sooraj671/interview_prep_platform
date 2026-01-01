from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr
    user_type: str = "candidate"

class UserCreate(UserBase):
    password: Optional[str] = None
    auth_provider: str = "email"
    provider_id: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    auth_provider: str
    is_active: bool
    is_verified: bool
    user_type: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    years_of_experience: Optional[int] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"

    @validator('years_of_experience')
    def validate_experience(cls, v):
        if v is not None and v < 0:
            raise ValueError('Years of experience cannot be negative')
        return v

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    profile_picture_url: Optional[str]
    resume_url: Optional[str]
    resume_parsed_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserSkillBase(BaseModel):
    self_rating: Optional[int] = None
    confidence_level: Optional[int] = None

    @validator('self_rating', 'confidence_level')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Rating must be between 1 and 10')
        return v

class UserSkillCreate(UserSkillBase):
    skill_id: uuid.UUID

class UserSkillUpdate(UserSkillBase):
    pass

class UserSkillResponse(UserSkillBase):
    id: uuid.UUID
    user_id: uuid.UUID
    skill_id: uuid.UUID
    assessed_score: Optional[float]
    last_assessed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserExperienceBase(BaseModel):
    company_name: str
    role_title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_current_job: bool = False
    skills_used: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None

class UserExperienceCreate(UserExperienceBase):
    pass

class UserExperienceUpdate(UserExperienceBase):
    pass

class UserExperienceResponse(UserExperienceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserEducationBase(BaseModel):
    institution_name: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    gpa: Optional[float] = None

    @validator('gpa')
    def validate_gpa(cls, v):
        if v is not None and (v < 0 or v > 4.0):
            raise ValueError('GPA must be between 0 and 4.0')
        return v

class UserEducationCreate(UserEducationBase):
    pass

class UserEducationUpdate(UserEducationBase):
    pass

class UserEducationResponse(UserEducationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserWithProfileResponse(UserResponse):
    profile: Optional[UserProfileResponse] = None
    skills: List[UserSkillResponse] = []
    experiences: List[UserExperienceResponse] = []
    education: List[UserEducationResponse] = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserWithProfileResponse

class OAuthCallbackRequest(BaseModel):
    provider: str
    code: str
    state: Optional[str] = None

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
