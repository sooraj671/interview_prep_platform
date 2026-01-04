"""
Database Connection Infrastructure
PostgreSQL connection management following Clean Architecture
"""
import os
import asyncpg
import aiofiles
from typing import Optional
from contextlib import asynccontextmanager

from ..config.settings import AppSettings
from shared.exceptions.domain_exceptions import DatabaseException


class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self, config: AppSettings):
        self.config = config
        self._pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self._pool = await asyncpg.create_pool(
                host=self.config.database.host,
                port=self.config.database.port,
                database=self.config.database.name,
                user=self.config.database.user,
                password=self.config.database.password,
                min_size=self.config.database.pool_min_size,
                max_size=self.config.database.pool_max_size,
                command_timeout=self.config.database.command_timeout
            )
        except Exception as e:
            raise DatabaseException(
                operation="initialize",
                reason=f"Failed to initialize database connection: {str(e)}"
            )
    
    async def close(self):
        """Close database connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self._pool:
            await self.initialize()
        
        conn = None
        try:
            conn = await self._pool.acquire()
            yield conn
        except Exception as e:
            if conn:
                await conn.rollback()
            raise DatabaseException(
                operation="get_connection",
                reason=f"Database operation failed: {str(e)}"
            )
        finally:
            if conn:
                await self._pool.release(conn)
    
    async def execute(self, query: str, *args):
        """Execute a query without returning results"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Execute a query and return all results"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Execute a query and return first result"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Execute a query and return single value"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def execute_many(self, query: str, args_list):
        """Execute a query multiple times with different arguments"""
        async with self.get_connection() as conn:
            return await conn.executemany(query, args_list)
    
    async def transaction(self):
        """Execute operations in a transaction"""
        if not self._pool:
            await self.initialize()
        
        return self._pool.transaction()


class DatabaseManager:
    """Database manager for handling database operations"""
    
    def __init__(self, config: AppSettings):
        self.config = config
        self.connection = DatabaseConnection(config)
    
    async def initialize(self):
        """Initialize database and run migrations if needed"""
        await self.connection.initialize()
        
        # Run schema if tables don't exist
        await self._ensure_schema()
    
    async def close(self):
        """Close database connections"""
        await self.connection.close()
    
    async def _ensure_schema(self):
        """Ensure database schema exists"""
        # Check if users table exists
        result = await self.connection.fetchval(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
            """
        )
        
        if not result:
            await self._create_schema()
    
    async def _create_schema(self):
        """Create database schema from SQL file"""
        schema_file = os.path.join(
            os.path.dirname(__file__),
            "../../../database_schema.sql"
        )
        
        try:
            async with aiofiles.open(schema_file, 'r') as f:
                schema_sql = await f.read()
            
            # Split by semicolons and execute each statement
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement and not statement.startswith('--'):
                    await self.connection.execute(statement)
                    
        except FileNotFoundError:
            raise DatabaseException(
                operation="create_schema",
                reason="Database schema file not found"
            )
        except Exception as e:
            raise DatabaseException(
                operation="create_schema",
                reason=f"Failed to create database schema: {str(e)}"
            )
    
    @property
    def db(self):
        """Get database connection for direct access"""
        return self.connection


# Global database manager instance
_database_manager: Optional[DatabaseManager] = None


async def get_database_manager(config: AppSettings) -> DatabaseManager:
    """Get or create database manager instance"""
    global _database_manager
    
    if _database_manager is None:
        _database_manager = DatabaseManager(config)
        await _database_manager.initialize()
    
    return _database_manager


async def close_database():
    """Close global database manager"""
    global _database_manager
    
    if _database_manager:
        await _database_manager.close()
        _database_manager = None
