"""
User SQLAlchemy Models
SQLAlchemy models for user-related tables
"""

from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import text
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from .base import BaseModel


class User(BaseModel):
    """User model for users table"""
    __tablename__ = "users"
    
    # Override id from BaseModel to match schema
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
        nullable=False
    )
    
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="candidate",
        server_default=text("'candidate'"),
        index=True
    )
    auth_provider: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="email",
        server_default=text("'email'")
    )
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="pending_verification",
        server_default=text("'pending_verification'"),
        index=True
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False,
        server_default=text("FALSE")
    )
    phone_verified: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False,
        server_default=text("FALSE")
    )
    two_factor_enabled: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False,
        server_default=text("FALSE")
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class UserProfile(BaseModel):
    """User profile model for user_profiles table"""
    __tablename__ = "user_profiles"
    
    # Override id from BaseModel - user_id is the primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
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
    skills: Mapped[List[str]] = mapped_column(JSONB, default=[], server_default=text("'[]'"))
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={}, server_default=text("'{}'"))
    
    # Relationships
    user = relationship("User", back_populates="profile")


class UserStats(BaseModel):
    """User statistics model for user_stats table"""
    __tablename__ = "user_stats"
    
    # Override id from BaseModel - user_id is the primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    total_assessments: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    completed_assessments: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    average_score: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.0, server_default=text("0.0"))
    total_study_time: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))  # minutes
    current_streak: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    skill_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    roadmap_count: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="stats")


class UserSession(BaseModel):
    """User session model for user_sessions table"""
    __tablename__ = "user_sessions"
    
    # Override id from BaseModel - session_id is the primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
        nullable=False
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    last_used: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
