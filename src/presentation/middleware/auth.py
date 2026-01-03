"""
Authentication Middleware
Handles JWT token validation and user authentication
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from uuid import UUID

from src.infrastructure.auth.jwt_service import JWTService
from src.application.interfaces.repositories import UserRepository


security = HTTPBearer()


async def get_jwt_service() -> JWTService:
    """Get JWT service instance"""
    # This would be injected from the dependency injection container
    # For now, return a mock instance
    return JWTService()


async def get_user_repository() -> UserRepository:
    """Get user repository instance"""
    # This would be injected from the dependency injection container
    # For now, return a mock instance
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service),
    user_repository: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        # Validate JWT token
        payload = jwt_service.decode_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await user_repository.get_by_id(UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.profile.first_name,
            "last_name": user.profile.last_name,
            "role": user.role.value,
            "profile": user.profile.to_dict(),
            "stats": user.stats.to_dict(),
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service),
    user_repository: UserRepository = Depends(get_user_repository)
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, jwt_service, user_repository)
    except HTTPException:
        return None


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current active user"""
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user


async def get_current_verified_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current verified user"""
    if not current_user.get("is_verified", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not verified"
        )
    return current_user


def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker


def require_any_role(roles: list):
    """Decorator to require any of the specified roles"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if current_user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required one of roles: {', '.join(roles)}"
            )
        return current_user
    return role_checker


# Role-specific dependencies
require_admin = require_role("admin")
require_interviewer = require_role("interviewer")
require_candidate = require_role("candidate")

# Multiple role dependencies
require_interviewer_or_admin = require_any_role(["interviewer", "admin"])
require_candidate_or_interviewer = require_any_role(["candidate", "interviewer"])
