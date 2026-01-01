from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db, get_async_db
from app.core.auth import get_current_user, get_current_active_user, get_optional_current_user
from app.models.user import User

# Common dependencies
def get_current_user_dependency():
    """Get current authenticated user."""
    return Depends(get_current_active_user)

def get_optional_user_dependency():
    """Get current user if authenticated, otherwise None."""
    return Depends(get_optional_current_user)

def get_db_dependency():
    """Get database session."""
    return Depends(get_db)

def get_async_db_dependency():
    """Get async database session."""
    return Depends(get_async_db)

# Role-based dependencies
def require_candidate_user(current_user: User = get_current_active_user):
    """Require user to be a candidate."""
    if current_user.user_type.value != "candidate":
        from app.core.exceptions import AuthorizationError
        raise AuthorizationError("This endpoint is only available for candidates")
    return current_user

def require_interviewer_user(current_user: User = get_current_active_user):
    """Require user to be an interviewer."""
    if current_user.user_type.value != "interviewer":
        from app.core.exceptions import AuthorizationError
        raise AuthorizationError("This endpoint is only available for interviewers")
    return current_user
