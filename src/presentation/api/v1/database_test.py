"""
Database Test API endpoints
Test Supabase database connection
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

router = APIRouter(prefix="/database", tags=["Database Testing"])

@router.get(
    "/test",
    summary="Test Database Connection",
    description="Test connection to Supabase database",
    responses={
        200: {
            "description": "Database connection successful",
            "content": {
                "application/json": {
                    "example": {
                        "status": "connected",
                        "database": "postgres",
                        "host": "aws-1-ap-southeast-1.pooler.supabase.com",
                        "user": "postgres.dfymgksznlpyfuueqomg",
                        "version": "PostgreSQL 15.x..."
                    }
                }
            }
        },
        500: {
            "description": "Database connection failed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "error": "Connection failed",
                        "database": "postgres",
                        "host": "aws-1-ap-southeast-1.pooler.supabase.com"
                    }
                }
            }
        }
    }
)
async def test_database():
    """
    Test database connection to Supabase
    
    Returns connection status and database information
    """
    try:
        from infrastructure.database.simple_connection import test_database_connection
        return test_database_connection()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database test failed: {str(e)}"
        )

@router.get(
    "/schema",
    summary="Check Database Schema",
    description="Check if database schema is initialized",
    responses={
        200: {
            "description": "Schema check completed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "checked",
                        "users_table_exists": True,
                        "database": "postgres",
                        "message": "Database schema appears to be initialized"
                    }
                }
            }
        }
    }
)
async def check_schema():
    """
    Check database schema initialization
    
    Returns schema status and table information
    """
    try:
        from infrastructure.database.simple_connection import initialize_database_schema
        return initialize_database_schema()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Schema check failed: {str(e)}"
        )
