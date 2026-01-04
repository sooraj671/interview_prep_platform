"""
Interview Preparation Platform - Simple ORM Version
Direct SQLAlchemy without complex domain layer
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQLAlchemy imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.sql import text

# Import models directly
from infrastructure.database.models.base import Base
from infrastructure.database.models.user import User as UserModel, UserProfile, UserStats
from infrastructure.database.models.skill import Skill as SkillModel
from infrastructure.database.models.assessment import Assessment as AssessmentModel
from infrastructure.database.models.roadmap import Roadmap as RoadmapModel
from infrastructure.database.models.analytics import Analytics as AnalyticsModel

# Pydantic models for API
class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    role: str = "candidate"
    bio: str = ""
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    years_of_experience: Optional[int] = None
    domain: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    skills: List[str] = []
    preferences: Dict[str, Any] = {}

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    status: str
    email_verified: bool
    phone_verified: bool
    two_factor_enabled: bool
    created_at: str
    updated_at: str
    last_login: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Database setup
class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Convert postgresql:// to postgresql+asyncpg:// for async support
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        self.engine = create_async_engine(
            self.database_url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            future=True
        )
        
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncSession:
        """Get an async session"""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Close the engine"""
        await self.engine.dispose()

# Global database manager
db_manager = DatabaseManager()

async def get_db_session() -> AsyncSession:
    """Dependency to get database session"""
    async for session in db_manager.get_session():
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Interview Preparation Platform with Simple ORM...")
    
    # Initialize database tables if needed
    try:
        await db_manager.create_tables()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database tables: {e}")
    
    logger.info("✅ Application started successfully")
    yield
    
    logger.info("🛑 Shutting down Interview Preparation Platform...")
    await db_manager.close()
    logger.info("✅ Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Interview Preparation Platform - Simple ORM",
    description="AI-powered interview preparation platform with direct SQLAlchemy",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.router.lifespan_context = lifespan

# Helper function to map model to response
def map_user_to_response(user_model: UserModel) -> UserResponse:
    """Map User model to UserResponse"""
    # Return basic user info without relationships for now
    return UserResponse(
        id=str(user_model.id),
        email=user_model.email,
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        role=user_model.role,
        status=user_model.status,
        email_verified=user_model.email_verified,
        phone_verified=user_model.phone_verified,
        two_factor_enabled=user_model.two_factor_enabled,
        created_at=user_model.created_at.isoformat(),
        updated_at=user_model.updated_at.isoformat(),
        last_login=user_model.last_login.isoformat() if user_model.last_login else None,
        profile=None,  # TODO: Load profile separately when needed
        stats=None     # TODO: Load stats separately when needed
    )

# Basic endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Interview Preparation Platform API - Simple ORM Version",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "database": "Direct SQLAlchemy ORM with PostgreSQL"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "database": "Direct SQLAlchemy ORM",
        "orm": "enabled"
    }

@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "database": "Direct SQLAlchemy ORM configured",
        "environment": os.getenv("APP_ENV", "development"),
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# User endpoints
@app.get("/api/v1/users", response_model=List[UserResponse], tags=["Users"])
async def get_users(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all users"""
    try:
        stmt = select(UserModel).limit(limit).offset(offset)
        
        result = await session.execute(stmt)
        user_models = result.scalars().all()
        
        return [map_user_to_response(user_model) for user_model in user_models]
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@app.get("/api/v1/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get user by ID"""
    try:
        user_uuid = UUID(user_id)
        stmt = select(UserModel).where(UserModel.id == user_uuid)
        
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise HTTPException(status_code=404, detail="User not found")
        
        return map_user_to_response(user_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")

@app.post("/api/v1/users", response_model=UserResponse, tags=["Users"])
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new user"""
    try:
        # Create user model
        user_model = UserModel(
            email=user_data.email,
            password_hash=user_data.password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            auth_provider="email",
            provider_id=None,
            status="pending_verification",
            email_verified=False,
            phone_verified=False,
            two_factor_enabled=False
        )
        
        session.add(user_model)
        await session.flush()  # Get the ID
        
        # Create profile
        profile_model = UserProfile(
            user_id=user_model.id,
            bio=user_data.bio,
            phone=user_data.phone,
            city=user_data.city,
            country=user_data.country,
            years_of_experience=user_data.years_of_experience,
            domain=user_data.domain,
            linkedin_url=user_data.linkedin_url,
            github_url=user_data.github_url,
            portfolio_url=user_data.portfolio_url,
            resume_url=user_data.resume_url,
            skills=user_data.skills,
            preferences=user_data.preferences
        )
        session.add(profile_model)
        
        # Create stats
        stats_model = UserStats(
            user_id=user_model.id,
            total_assessments=0,
            completed_assessments=0,
            average_score=0.0,
            total_study_time=0,
            current_streak=0,
            longest_streak=0,
            skill_count=0,
            roadmap_count=0,
            last_active=None
        )
        session.add(stats_model)
        
        await session.commit()
        
        # Return the created user without relationships for now
        return map_user_to_response(user_model)
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/api/v1/users/email/{email}", response_model=UserResponse, tags=["Users"])
async def get_user_by_email(
    email: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get user by email"""
    try:
        stmt = select(UserModel).where(UserModel.email == email)
        
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise HTTPException(status_code=404, detail="User not found")
        
        return map_user_to_response(user_model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")

# Skills endpoints
@app.get("/api/v1/skills", tags=["Skills"])
async def get_skills(
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all skills"""
    try:
        stmt = select(SkillModel)
        
        if category:
            stmt = stmt.where(SkillModel.category == category)
        
        stmt = stmt.limit(limit).offset(offset)
        
        result = await session.execute(stmt)
        skill_models = result.scalars().all()
        
        return {
            "skills": [
                {
                    "id": str(skill.id),
                    "name": skill.name,
                    "category": skill.category,
                    "description": skill.description,
                    "difficulty": skill.difficulty,
                    "tags": skill.tags,
                    "prerequisites": skill.prerequisites,
                    "related_skills": skill.related_skills,
                    "industry_relevance": skill.industry_relevance,
                    "average_salary_impact": float(skill.average_salary_impact) if skill.average_salary_impact else None,
                    "learning_path": skill.learning_path,
                    "created_at": skill.created_at.isoformat(),
                    "updated_at": skill.updated_at.isoformat()
                }
                for skill in skill_models
            ],
            "total": len(skill_models),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting skills: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve skills")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Simple ORM application on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
