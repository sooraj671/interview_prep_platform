"""
API v1 - Version 1 endpoints
"""

from .auth_simple import router as auth_router
from .users import router as users_router
from .skills import router as skills_router
from .assessments import router as assessments_router
from .roadmaps import router as roadmaps_router
from .analytics import router as analytics_router

__all__ = [
    "auth_router",
    "users_router", 
    "skills_router",
    "assessments_router",
    "roadmaps_router",
    "analytics_router"
]
