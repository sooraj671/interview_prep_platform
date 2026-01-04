"""
SQLAlchemy Database Connection
SQLAlchemy async connection management for ORM operations
"""

import os
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    async_sessionmaker, 
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.pool import NullPool

from config.settings import AppConfig
from shared.exceptions.domain_exceptions import DatabaseException
from .models import Base


class SQLAlchemyConnection:
    """SQLAlchemy async connection manager"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    
    async def initialize(self):
        """Initialize SQLAlchemy engine and session factory"""
        try:
            # Build database URL
            database_url = (
                f"postgresql+asyncpg://{self.config.database.user}:"
                f"{self.config.database.password}@{self.config.database.host}:"
                f"{self.config.database.port}/{self.config.database.name}"
            )
            
            # Create async engine
            self._engine = create_async_engine(
                database_url,
                echo=self.config.database.echo_sql,
                pool_size=self.config.database.pool_min_size,
                max_overflow=self.config.database.pool_max_size - self.config.database.pool_min_size,
                pool_pre_ping=True,
                poolclass=NullPool if self.config.database.pool_min_size == 0 else None,
            )
            
            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
            
        except Exception as e:
            raise DatabaseException(
                operation="initialize",
                reason=f"Failed to initialize SQLAlchemy connection: {str(e)}"
            )
    
    async def close(self):
        """Close SQLAlchemy engine"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
    
    async def create_tables(self):
        """Create all tables from models"""
        if not self._engine:
            raise DatabaseException(
                operation="create_tables",
                reason="Database engine not initialized"
            )
        
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            raise DatabaseException(
                operation="create_tables",
                reason=f"Failed to create tables: {str(e)}"
            )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        if not self._session_factory:
            await self.initialize()
        
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise DatabaseException(
                operation="get_session",
                reason=f"Database session error: {str(e)}"
            )
        finally:
            await session.close()
    
    async def get_session_sync(self) -> AsyncSession:
        """Get database session without context manager (for dependency injection)"""
        if not self._session_factory:
            await self.initialize()
        
        return self._session_factory()


class SQLAlchemyManager:
    """SQLAlchemy manager for handling ORM operations"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.connection = SQLAlchemyConnection(config)
    
    async def initialize(self):
        """Initialize SQLAlchemy and create tables if needed"""
        await self.connection.initialize()
        
        # Create tables if they don't exist
        await self._ensure_tables()
    
    async def close(self):
        """Close SQLAlchemy connections"""
        await self.connection.close()
    
    async def _ensure_tables(self):
        """Ensure database tables exist"""
        # Check if users table exists
        async with self.connection.get_session() as session:
            try:
                result = await session.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'users'
                    )
                    """
                )
                table_exists = result.scalar()
                
                if not table_exists:
                    await self.connection.create_tables()
                    
            except Exception as e:
                raise DatabaseException(
                    operation="ensure_tables",
                    reason=f"Failed to check/create tables: {str(e)}"
                )
    
    @property
    def session_factory(self):
        """Get session factory for dependency injection"""
        return self.connection.get_session_sync


# Global SQLAlchemy manager instance
_sqlalchemy_manager: Optional[SQLAlchemyManager] = None


async def get_sqlalchemy_manager(config: AppConfig) -> SQLAlchemyManager:
    """Get or create SQLAlchemy manager instance"""
    global _sqlalchemy_manager
    
    if _sqlalchemy_manager is None:
        _sqlalchemy_manager = SQLAlchemyManager(config)
        await _sqlalchemy_manager.initialize()
    
    return _sqlalchemy_manager


async def close_sqlalchemy():
    """Close global SQLAlchemy manager"""
    global _sqlalchemy_manager
    
    if _sqlalchemy_manager:
        await _sqlalchemy_manager.close()
        _sqlalchemy_manager = None


# Dependency injection function for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting database session"""
    from config.settings import get_settings
    
    config = get_settings()
    manager = await get_sqlalchemy_manager(config)
    
    async with manager.connection.get_session() as session:
        yield session
