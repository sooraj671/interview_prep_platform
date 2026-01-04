"""
SQLAlchemy Database Configuration
Database connection and session management using SQLAlchemy
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
from sqlalchemy import text

from ..models import Base


class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:password@localhost:5432/postgres"
        )
        self.echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        self.pool_size = int(os.getenv("DATABASE_POOL_SIZE", "5"))  # Reduced for Railway
        self.max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))  # Reduced for Railway
        self.pool_timeout = int(os.getenv("DATABASE_POOL_TIMEOUT", "10"))  # Reduced timeout
        self.pool_recycle = int(os.getenv("DATABASE_POOL_RECYCLE", "1800"))  # 30 minutes
        self.connect_timeout = int(os.getenv("DATABASE_CONNECT_TIMEOUT", "5"))  # 5 seconds


class DatabaseManager:
    """Database manager for SQLAlchemy operations"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    
    async def initialize(self) -> None:
        """Initialize database engine and session factory - non-blocking"""
        if self._engine is not None:
            return
        
        try:
            # Create async engine with connection timeout
            self._engine = create_async_engine(
                self.config.database_url,
                echo=self.config.echo,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                poolclass=NullPool if "test" in self.config.database_url else None,
                connect_args={
                    "command_timeout": self.config.connect_timeout,
                    "server_settings": {
                        "application_name": "interview_prep_platform",
                        "jit": "off",
                        "connect_timeout": self.config.connect_timeout
                    }
                }
            )
            
            # Create session factory
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # Skip table creation in production for faster startup
            if "test" in self.config.database_url:
                await self.create_tables()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Don't re-raise, allow application to start
    
    async def create_tables(self) -> None:
        """Create all database tables"""
        if self._engine is None:
            await self.initialize()
        
        async with self._engine.begin() as conn:
            # Enable UUID extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self) -> None:
        """Drop all database tables (use with caution!)"""
        if self._engine is None:
            await self.initialize()
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def close(self) -> None:
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        if self._session_factory is None:
            await self.initialize()
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def get_session_sync(self) -> AsyncSession:
        """Get database session (for dependency injection)"""
        if self._session_factory is None:
            await self.initialize()
        
        return self._session_factory()
    
    @property
    def engine(self) -> Optional[AsyncEngine]:
        """Get database engine"""
        return self._engine
    
    async def health_check(self) -> dict:
        """Quick database health check with timeout"""
        if self._engine is None:
            return {
                "status": "unhealthy",
                "error": "Database not initialized",
                "database_url": self.config.database_url.split("@")[-1] if "@" in self.config.database_url else "unknown"
            }
        
        try:
            # Very simple and fast health check
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                return {
                    "status": "healthy",
                    "database_url": self.config.database_url.split("@")[-1] if "@" in self.config.database_url else "unknown",
                    "pool_size": self.config.pool_size,
                    "max_overflow": self.config.max_overflow
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_url": self.config.database_url.split("@")[-1] if "@" in self.config.database_url else "unknown"
            }


# Global database manager instance
_database_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _database_manager
    
    if _database_manager is None:
        _database_manager = DatabaseManager()
        await _database_manager.initialize()
    
    return _database_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (for FastAPI dependency)"""
    db_manager = await get_database_manager()
    async with db_manager.get_session() as session:
        yield session


async def close_database() -> None:
    """Close global database manager"""
    global _database_manager
    
    if _database_manager:
        await _database_manager.close()
        _database_manager = None


# Database dependency for FastAPI
async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session"""
    async for session in get_db_session():
        yield session
