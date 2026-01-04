"""
API Layer - Controllers and endpoints
"""

from .v1 import (
    auth_router,
    users_router,
    skills_router,
    assessments_router,
    roadmaps_router,
    analytics_router,
    ai_test_router,
    database_test_router
)

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
