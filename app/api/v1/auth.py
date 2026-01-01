from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.database import get_db
from app.models.user import User, UserProfile
from app.schemas.user import (
    LoginRequest, LoginResponse, OAuthCallbackRequest,
    TokenRefreshRequest, TokenResponse, UserCreate, UserResponse
)
from app.core.auth import (
    create_access_token, create_refresh_token, verify_token,
    get_password_hash, verify_password
)
from app.core.exceptions import AuthenticationError, ValidationError, NotFoundError
from app.services.auth_service import AuthService
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user."""
    auth_service = AuthService(db)
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValidationError("Email already registered")
    
    # Create user
    user = auth_service.create_user(user_data)
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Login user and return tokens."""
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise AuthenticationError("Invalid email or password")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@router.post("/oauth/callback", response_model=LoginResponse)
async def oauth_callback(
    callback_data: OAuthCallbackRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Handle OAuth callback from providers."""
    auth_service = AuthService(db)
    
    # Process OAuth callback
    user = auth_service.process_oauth_callback(
        provider=callback_data.provider,
        code=callback_data.code,
        state=callback_data.state
    )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token."""
    try:
        payload = verify_token(refresh_data.refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if token_type != "refresh" or not user_id:
            raise AuthenticationError("Invalid refresh token")
        
        # Verify user exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(access_token=access_token)
        
    except Exception:
        raise AuthenticationError("Invalid refresh token")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user information."""
    return current_user

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Logout user (client-side token invalidation)."""
    # In a real implementation, you might want to invalidate tokens
    # by maintaining a blacklist in Redis
    return {"message": "Successfully logged out"}
