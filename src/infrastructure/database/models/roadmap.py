"""
Roadmap Management Models
SQLAlchemy models for roadmaps, topics, resources, exercises, and milestones
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import (
    Boolean, Integer, String, Text, DateTime, ForeignKey, 
    CheckConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from .base import BaseModel


class Roadmap(BaseModel):
    """Roadmaps table"""
    __tablename__ = "roadmaps"
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    target_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=12, server_default=text("12"))
    difficulty: Mapped[str] = mapped_column(
        String(50), 
        default="intermediate",
        server_default=text("'intermediate'")
    )
    status: Mapped[str] = mapped_column(
        String(50), 
        default="not_started",
        server_default=text("'not_started'")
    )
    progress_percentage: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        server_default=text("0")
    )
    total_topics: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    completed_topics: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("FALSE"))
    generation_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    topics: Mapped[List["RoadmapTopic"]] = relationship(
        "RoadmapTopic", 
        back_populates="roadmap", 
        cascade="all, delete-orphan"
    )
    milestones: Mapped[List["RoadmapMilestone"]] = relationship(
        "RoadmapMilestone", 
        back_populates="roadmap", 
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_roadmap_difficulty"
        ),
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'paused', 'completed', 'archived')",
            name="check_roadmap_status"
        ),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="check_progress_percentage_range"
        ),
        Index("idx_roadmaps_user_id", "user_id"),
        Index("idx_roadmaps_status", "status"),
    )


class RoadmapTopic(BaseModel):
    """Roadmap topics table"""
    __tablename__ = "roadmap_topics"
    roadmap_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("roadmaps.id", ondelete="CASCADE"), 
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    difficulty: Mapped[str] = mapped_column(
        String(50), 
        default="intermediate",
        server_default=text("'intermediate'")
    )
    estimated_hours: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
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
    content: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    skills_covered: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    assessment_criteria: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    milestone: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("FALSE"))
    status: Mapped[str] = mapped_column(
        String(50), 
        default="not_started",
        server_default=text("'not_started'")
    )
    progress_percentage: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        server_default=text("0")
    )
    time_spent_hours: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    notes: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    week_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="topics")
    learning_resources: Mapped[List["LearningResource"]] = relationship(
        "LearningResource", 
        back_populates="roadmap_topic", 
        cascade="all, delete-orphan"
    )
    practice_exercises: Mapped[List["PracticeExercise"]] = relationship(
        "PracticeExercise", 
        back_populates="roadmap_topic", 
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_roadmap_topic_difficulty"
        ),
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed', 'skipped')",
            name="check_roadmap_topic_status"
        ),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="check_topic_progress_percentage_range"
        ),
        Index("idx_roadmap_topics_roadmap_id", "roadmap_id"),
        Index("idx_roadmap_topics_status", "status"),
    )


class LearningResource(BaseModel):
    """Learning resources table"""
    __tablename__ = "learning_resources"
    roadmap_topic_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("roadmap_topics.id", ondelete="CASCADE"), 
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
    duration_hours: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    cost: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("TRUE"))
    
    # Relationships
    roadmap_topic: Mapped["RoadmapTopic"] = relationship("RoadmapTopic", back_populates="learning_resources")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('course', 'book', 'tutorial', 'documentation', 'tool', 'video')",
            name="check_learning_resource_type"
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_learning_resource_difficulty"
        ),
    )


class PracticeExercise(BaseModel):
    """Practice exercises table"""
    __tablename__ = "practice_exercises"
    roadmap_topic_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("roadmap_topics.id", ondelete="CASCADE"), 
        nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    estimated_time: Mapped[int] = mapped_column(Integer, default=30, server_default=text("30"))  # minutes
    difficulty: Mapped[str] = mapped_column(
        String(50), 
        default="intermediate",
        server_default=text("'intermediate'")
    )
    instructions: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    resources: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    success_criteria: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    completed: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("FALSE"))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roadmap_topic: Mapped["RoadmapTopic"] = relationship("RoadmapTopic", back_populates="practice_exercises")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('coding', 'project', 'reading', 'quiz', 'simulation')",
            name="check_practice_exercise_type"
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_practice_exercise_difficulty"
        ),
    )


class RoadmapMilestone(BaseModel):
    """Roadmap milestones table"""
    __tablename__ = "roadmap_milestones"
    roadmap_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("roadmaps.id", ondelete="CASCADE"), 
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    skills_to_master: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    assessment_type: Mapped[str] = mapped_column(
        String(100), 
        default="quiz",
        server_default=text("'quiz'")
    )
    status: Mapped[str] = mapped_column(
        String(50), 
        default="not_started",
        server_default=text("'not_started'")
    )
    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="milestones")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed', 'overdue')",
            name="check_milestone_status"
        ),
    )
