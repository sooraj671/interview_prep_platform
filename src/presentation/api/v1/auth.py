"""
Authentication API v1
Handles OAuth authentication, registration, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any

from src.application.use_cases.auth.oauth_login import OAuthLoginUseCase, OAuthLoginRequest, OAuthLoginResponse
from src.application.use_cases.auth.register_user import RegisterUserUseCase, RegisterUserRequest, RegisterUserResponse
from src.presentation.schemas.auth import (
    LoginResponse, RegisterResponse, RefreshTokenRequest, 
    RefreshTokenResponse, UserResponse
)
from src.presentation.middleware.auth import get_current_user, get_current_user_optional
from src.shared.exceptions.domain_exceptions import (
    DuplicateUserException, InvalidCredentialsException,
    AccountNotActiveException, AccountNotVerifiedException
)


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(request: RegisterUserRequest):
    """Register a new user"""
    try:
        use_case = RegisterUserUseCase()
        response = await use_case.execute(request)
        return response
    except DuplicateUserException as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(request: OAuthLoginRequest):
    """Login user with OAuth or credentials"""
    try:
        use_case = OAuthLoginUseCase(
            user_repository=None,  # Will be injected
            prompt_service=None,
            jwt_service=None,
            password_service=None
        )
        response = await use_case.execute(request)
        return response
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
    except AccountNotActiveException as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except AccountNotVerifiedException as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=200)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        # This would use the JWT service to refresh the token
        # For now, return mock response
        return RefreshTokenResponse(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            token_type="bearer",
            expires_in=3600
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout", status_code=200)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout user"""
    try:
        # This would invalidate the token
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse, status_code=200)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    try:
        # This would get the full user profile
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            first_name=current_user["first_name"],
            last_name=current_user["last_name"],
            role=current_user["role"],
            profile=current_user["profile"],
            stats=current_user["stats"],
            created_at=current_user["created_at"],
            updated_at=current_user["updated_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.put("/me", response_model=UserResponse, status_code=200)
async def update_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    profile_data: Dict[str, Any]
):
    """Update current user profile"""
    try:
        # This would update the user profile
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            first_name=current_user["first_name"],
            last_name=current_user["last_name"],
            role=current_user["role"],
            profile={**current_user["profile"], **profile_data},
            stats=current_user["stats"],
            created_at=current_user["created_at"],
            updated_at=current_user["updated_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.post("/me/change-password", status_code=200)
async def change_password(
    current_user: Dict[str, Any] = Depends(get_current_user),
    password_data: Dict[str, str]
):
    """Change user password"""
    try:
        # This would validate and update the password
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to change password: {str(e)}"
        )


@router.get("/oauth/{provider}/login", status_code=200)
async def get_oauth_login_url(provider: str):
    """Get OAuth login URL for specified provider"""
    try:
        # This would generate the OAuth login URL for the specified provider
        oauth_urls = {
            "google": "https://accounts.google.com/oauth/authorize?client_id=YOUR_GOOGLE_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=openid profile email",
            "microsoft": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=YOUR_MICROSOFT_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=openid profile email",
            "github": "https://github.com/login/oauth/authorize?client_id=YOUR_GITHUB_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=user:email",
            "linkedin": "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_LINKEDIN_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=r_lite r_emailaddress"
        }
        
        if provider.lower() not in oauth_urls:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported OAuth provider: {provider}"
            )
        
        return {"login_url": oauth_urls[provider.lower()]}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get OAuth URL: {str(e)}"
        )


@router.get("/oauth/{provider}/callback", status_code=200)
async def oauth_callback(
    provider: str,
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None
):
    """Handle OAuth callback"""
    try:
        if error:
            raise HTTPException(
                status_code=400,
                detail=f"OAuth error: {error_description or error}"
            )
        
        # This would handle the OAuth callback
        # For now, return mock response
        return {
            "message": f"OAuth callback received for {provider}",
            "code": code,
            "state": state
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth callback failed: {str(e)}"
        )
