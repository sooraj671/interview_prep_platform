"""
Skills Management Models
SQLAlchemy models for skills, topics, resources, and user progress
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import (
    Boolean, Integer, String, Text, DateTime, ForeignKey, 
    CheckConstraint, Index, func, DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from .base import BaseModel


class Skill(BaseModel):
    """Skills table"""
    __tablename__ = "skills"
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    difficulty: Mapped[str] = mapped_column(
        String(50), 
        default="intermediate",
        server_default=text("'intermediate'")
    )
    tags: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    prerequisites: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    related_skills: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    industry_relevance: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    average_salary_impact: Mapped[Optional[float]] = mapped_column(
        DECIMAL(10, 2), 
        nullable=True
    )
    learning_path: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    
    # Relationships
    topics: Mapped[List["SkillTopic"]] = relationship(
        "SkillTopic", 
        back_populates="skill", 
        cascade="all, delete-orphan"
    )
    resources: Mapped[List["SkillResource"]] = relationship(
        "SkillResource", 
        back_populates="skill", 
        cascade="all, delete-orphan"
    )
    user_progress: Mapped[List["UserSkillProgress"]] = relationship(
        "UserSkillProgress", 
        back_populates="skill", 
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "category IN ('programming', 'framework', 'database', 'cloud', 'devops', 'mobile', "
            "'frontend', 'backend', 'full_stack', 'data_science', 'machine_learning', "
            "'ai', 'blockchain', 'security', 'testing', 'design', 'project_management', "
            "'soft_skills', 'domain_specific')",
            name="check_skill_category"
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_skill_difficulty"
        ),
        Index("idx_skills_category", "category"),
        Index("idx_skills_difficulty", "difficulty"),
    )


class SkillTopic(BaseModel):
    """Skill topics table"""
    __tablename__ = "skill_topics"
    skill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("skills.id", ondelete="CASCADE"), 
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    difficulty: Mapped[str] = mapped_column(
        String(50), 
        default="intermediate",
        server_default=text("'intermediate'")
    )
    prerequisites: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    learning_objectives: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    estimated_hours: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    resources: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    
    # Relationships
    skill: Mapped["Skill"] = relationship("Skill", back_populates="topics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_skill_topic_difficulty"
        ),
        Index("idx_skill_topics_skill_id", "skill_id"),
    )


class SkillResource(BaseModel):
    """Skill resources table"""
    __tablename__ = "skill_resources"
    skill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("skills.id", ondelete="CASCADE"), 
        nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    difficulty: Mapped[str] = mapped_column(
        String(50), 
        default="intermediate",
        server_default=text("'intermediate'")
    )
    rating: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2), nullable=True)
    duration_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    skill: Mapped["Skill"] = relationship("Skill", back_populates="resources")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('course', 'book', 'tutorial', 'documentation', 'tool')",
            name="check_skill_resource_type"
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_skill_resource_difficulty"
        ),
    )


class UserSkillProgress(BaseModel):
    """User skill progress table"""
    __tablename__ = "user_skill_progress"
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    skill_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("skills.id", ondelete="CASCADE"), 
        nullable=False
    )
    current_level: Mapped[int] = mapped_column(
        Integer, 
        default=1, 
        server_default=text("1")
    )
    target_level: Mapped[int] = mapped_column(
        Integer, 
        default=10, 
        server_default=text("10")
    )
    demonstrated_level: Mapped[int] = mapped_column(
        Integer, 
        default=1, 
        server_default=text("1")
    )
    confidence_level: Mapped[str] = mapped_column(
        String(50), 
        default="low",
        server_default=text("'low'")
    )
    progress_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    
    # Relationships
    skill: Mapped["Skill"] = relationship("Skill", back_populates="user_progress")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "current_level >= 1 AND current_level <= 10",
            name="check_current_level_range"
        ),
        CheckConstraint(
            "target_level >= 1 AND target_level <= 10",
            name="check_target_level_range"
        ),
        CheckConstraint(
            "demonstrated_level >= 1 AND demonstrated_level <= 10",
            name="check_demonstrated_level_range"
        ),
        CheckConstraint(
            "confidence_level IN ('low', 'medium', 'high')",
            name="check_confidence_level"
        ),
        Index("idx_user_skill_progress_user_id", "user_id"),
        Index("idx_user_skill_progress_skill_id", "skill_id"),
    )
