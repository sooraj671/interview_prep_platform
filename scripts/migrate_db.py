#!/usr/bin/env python3
"""
Database Migration Script for Railway
Run this script to create database tables and run migrations
"""
import asyncio
import os
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command

# Import your database models
from src.config.settings import config_loader
from src.domain.entities import Base


async def create_database_tables():
    """Create all database tables"""
    print("🗄️ Creating database tables...")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False


async def run_alembic_migrations():
    """Run Alembic migrations"""
    print("🔄 Running Alembic migrations...")
    
    try:
        # Configure Alembic
        alembic_cfg = Config("alembic.ini")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        print("✅ Alembic migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running Alembic migrations: {e}")
        return False


async def main():
    """Main migration function"""
    print("🚀 Starting database migration...")
    
    # Create tables
    tables_created = await create_database_tables()
    
    # Run Alembic migrations
    migrations_completed = await run_alembic_migrations()
    
    if tables_created and migrations_completed:
        print("🎉 Database migration completed successfully!")
    else:
        print("❌ Database migration failed!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
