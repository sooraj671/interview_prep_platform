"""
Repository Factory
Factory for creating repository instances
"""

from sqlalchemy.ext.asyncio import AsyncSession

from .user_repository import SQLAlchemyUserRepository


class RepositoryFactory:
    """Factory for creating repository instances"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def user_repository(self) -> SQLAlchemyUserRepository:
        """Create user repository"""
        return SQLAlchemyUserRepository(self.session)


# Dependency injection function for FastAPI
async def get_repository_factory(session: AsyncSession) -> RepositoryFactory:
    """Get repository factory for dependency injection"""
    return RepositoryFactory(session)
