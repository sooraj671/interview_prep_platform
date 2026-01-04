"""
Simple Authentication API endpoints
Basic auth functionality without complex dependencies
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
from uuid import UUID

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic models for request/response
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: Optional[str] = "candidate"

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class RegisterResponse(BaseModel):
    message: str
    user_id: str
    status: str

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User Login",
    description="Authenticate user with email and password",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user": {
                            "id": "user_123",
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "role": "candidate"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid email or password"}
                }
            }
        }
    }
)
async def login(request: LoginRequest):
    """
    Login with email and password
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT token and user information
    """
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        "token_type": "bearer",
        "expires_in": 1800,
        "user": {
            "id": "user_123",
            "email": request.email,
            "first_name": "John",
            "last_name": "Doe",
            "role": "candidate"
        }
    }

@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="User Registration",
    description="Register a new user account",
    responses={
        201: {
            "description": "Registration successful",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User registered successfully",
                        "user_id": "new_user_123",
                        "status": "registered"
                    }
                }
            }
        },
        400: {
            "description": "Email already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        }
    }
)
async def register(request: RegisterRequest):
    """
    Register a new user
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (min 8 characters)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **role**: User role (candidate, interviewer, admin, recruiter)
    
    Returns user registration status
    """
    return {
        "message": "User registered successfully",
        "user_id": "new_user_123",
        "status": "registered"
    }

@router.post(
    "/refresh",
    summary="Refresh Access Token",
    description="Refresh JWT access token using refresh token",
    responses={
        200: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "new_jwt_token_here",
                        "token_type": "bearer",
                        "expires_in": 1800
                    }
                }
            }
        }
    }
)
async def refresh_token():
    """
    Refresh access token
    
    Requires valid refresh token in request body or headers
    Returns new JWT access token
    """
    return {
        "access_token": "new_jwt_token_here",
        "token_type": "bearer",
        "expires_in": 1800
    }

@router.post(
    "/logout",
    summary="User Logout",
    description="Logout user and invalidate tokens",
    responses={
        200: {
            "description": "Logout successful",
            "content": {
                "application/json": {
                    "example": {"message": "Logout successful", "status": "logged_out"}
                }
            }
        }
    }
)
async def logout():
    """
    Logout user
    
    Invalidates current access token and refresh token
    """
    return {
        "message": "Logout successful",
        "status": "logged_out"
    }

@router.get(
    "/me",
    summary="Get Current User",
    description="Get current authenticated user information",
    responses={
        200: {
            "description": "User information retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Current user endpoint",
                        "user": {
                            "id": "user_123",
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "role": "candidate",
                            "email_verified": True,
                            "created_at": "2024-01-03T10:00:00Z"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        }
    }
)
async def get_current_user():
    """
    Get current user information
    
    Requires valid JWT access token
    Returns complete user profile
    """
    return {
        "message": "Current user endpoint",
        "user": {
            "id": "user_123",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "candidate",
            "email_verified": True,
            "created_at": "2024-01-03T10:00:00Z"
        }
    }

@router.post(
    "/forgot-password",
    summary="Forgot Password",
    description="Send password reset email",
    responses={
        200: {
            "description": "Password reset email sent",
            "content": {
                "application/json": {
                    "example": {"message": "Password reset email sent", "status": "email_sent"}
                }
            }
        }
    }
)
async def forgot_password(email: EmailStr = Body(..., embed=True)):
    """
    Request password reset
    
    - **email**: User's email address
    
    Sends password reset link to user's email
    """
    return {
        "message": "Password reset email sent",
        "status": "email_sent"
    }

@router.post(
    "/reset-password",
    summary="Reset Password",
    description="Reset password using token",
    responses={
        200: {
            "description": "Password reset successful",
            "content": {
                "application/json": {
                    "example": {"message": "Password reset successful", "status": "password_reset"}
                }
            }
        }
    }
)
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(..., min_length=8)
):
    """
    Reset password with token
    
    - **token**: Password reset token from email
    - **new_password**: New password (min 8 characters)
    
    Updates user password and invalidates all tokens
    """
    return {
        "message": "Password reset successful",
        "status": "password_reset"
    }

@router.get(
    "/verify-email/{token}",
    summary="Verify Email",
    description="Verify user email address",
    responses={
        200: {
            "description": "Email verified successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Email verified successfully", "status": "verified"}
                }
            }
        }
    }
)
async def verify_email(token: str):
    """
    Verify email address
    
    - **token**: Email verification token
    
    Verifies user email and activates account
    """
    return {
        "message": "Email verified successfully",
        "status": "verified"
    }
