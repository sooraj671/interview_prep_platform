"""
Dependency Injection for ORM Repositories
Provides ORM-based repository instances for dependency injection
"""
from typing import AsyncGenerator
from fastapi import Depends

from .orm_session import orm_session_manager
from .orm_repositories import (
    PostgreSQLUserRepository, PostgreSQLSkillRepository,
    PostgreSQLRoadmapRepository, PostgreSQLAssessmentRepository,
    PostgreSQLAnalyticsRepository
)
from application.interfaces.repositories import (
    UserRepository, SkillRepository, RoadmapRepository,
    AssessmentRepository, AnalyticsRepository
)


async def get_db_session() -> AsyncGenerator:
    """Dependency to get database session"""
    async for session in orm_session_manager.get_session():
        yield session


def get_user_repository(session=Depends(get_db_session)) -> UserRepository:
    """Get user repository instance"""
    return PostgreSQLUserRepository(session)


def get_skill_repository(session=Depends(get_db_session)) -> SkillRepository:
    """Get skill repository instance"""
    return PostgreSQLSkillRepository(session)


def get_roadmap_repository(session=Depends(get_db_session)) -> RoadmapRepository:
    """Get roadmap repository instance"""
    return PostgreSQLRoadmapRepository(session)


def get_assessment_repository(session=Depends(get_db_session)) -> AssessmentRepository:
    """Get assessment repository instance"""
    return PostgreSQLAssessmentRepository(session)


def get_analytics_repository(session=Depends(get_db_session)) -> AnalyticsRepository:
    """Get analytics repository instance"""
    return PostgreSQLAnalyticsRepository(session)
