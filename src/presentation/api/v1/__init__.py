"""
API v1 - Version 1 endpoints
"""

from .auth_simple import router as auth_router
from .users import router as users_router
from .skills import router as skills_router
from .assessments import router as assessments_router
from .roadmaps import router as roadmaps_router
from .analytics import router as analytics_router
from .ai_test import router as ai_test_router
from .database_test import router as database_test_router

__all__ = [
    "auth_router",
    "users_router", 
    "skills_router",
    "assessments_router",
    "roadmaps_router",
    "analytics_router",
    "ai_test_router",
    "database_test_router"
]
