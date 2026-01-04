"""
User Management Models
SQLAlchemy models for users, profiles, stats, and sessions
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import (
    Boolean, Integer, String, Text, DateTime, ForeignKey, 
    CheckConstraint, Index, func, DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from .base import BaseModel, Base


class User(BaseModel):
    """Users table"""
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="candidate",
        server_default=text("'candidate'"),
        comment="candidate, interviewer, admin, recruiter"
    )
    auth_provider: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="email",
        server_default=text("'email'"),
        comment="email, google, github, linkedin"
    )
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="pending_verification",
        server_default=text("'pending_verification'"),
        comment="active, inactive, suspended, pending_verification"
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("FALSE"))
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("FALSE"))
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("FALSE"))
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('candidate', 'interviewer', 'admin', 'recruiter')", name="check_user_role"),
        CheckConstraint("auth_provider IN ('email', 'google', 'github', 'linkedin')", name="check_auth_provider"),
        CheckConstraint("status IN ('active', 'inactive', 'suspended', 'pending_verification')", name="check_user_status"),
        Index("idx_users_email", "email"),
        Index("idx_users_status", "status"),
        Index("idx_users_role", "role"),
        Index("idx_users_created_at", "created_at"),
    )


class UserProfile(Base):
    """User profiles table"""
    __tablename__ = "user_profiles"
    
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        primary_key=True
    )
    bio: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    resume_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    skills: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    preferences: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )


class UserStats(Base):
    """User statistics table"""
    __tablename__ = "user_stats"
    
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        primary_key=True
    )
    total_assessments: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    completed_assessments: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    average_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2), 
        default=0.0,
        server_default=text("0.0")
    )
    total_study_time: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))  # minutes
    current_streak: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    skill_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    roadmap_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class UserSession(BaseModel):
    """User sessions table"""
    __tablename__ = "user_sessions"
    
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("uuid_generate_v4()")
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    last_used: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_user_sessions_user_id", "user_id"),
        Index("idx_user_sessions_expires_at", "expires_at"),
    )
