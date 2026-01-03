#!/usr/bin/env python3
"""
Railway Database Initialization Script
This script initializes the PostgreSQL database with the schema
"""
import os
import asyncio
import asyncpg
from pathlib import Path

async def init_database():
    """Initialize database with schema"""
    
    # Get database connection details from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Build from individual variables
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))
        database = os.getenv("DB_NAME", "interview_prep")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")
        
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    print(f"Connecting to database...")
    
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(db_url)
        
        # Read schema file
        schema_path = Path(__file__).parent.parent / "database_schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("Executing database schema...")
        
        # Split and execute statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement and not statement.startswith('--'):
                try:
                    await conn.execute(statement)
                    print(f"✓ Executed statement {i}")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"⚠ Statement {i} skipped (already exists): {e}")
                    else:
                        print(f"✗ Error in statement {i}: {e}")
                        raise
        
        await conn.close()
        print("✅ Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
