"""
API v1 - Version 1 endpoints
"""

from .auth_simple import router as auth_router
from .users import router as users_router
from .ai_test import router as ai_test_router
from .database_test import router as database_test_router

__all__ = [
    "auth_router",
    "users_router", 
    "ai_test_router",
    "database_test_router"
]
