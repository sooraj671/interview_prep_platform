"""
Authentication Schemas
Pydantic models for authentication requests and responses
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "candidate"
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    years_of_experience: Optional[int] = None
    domain: Optional[str] = None


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    profile: Dict[str, Any]
    stats: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request"""
    code: str
    state: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response"""
    message: str
    code: str
    state: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    """Profile update request"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    years_of_experience: Optional[int] = None
    domain: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str
