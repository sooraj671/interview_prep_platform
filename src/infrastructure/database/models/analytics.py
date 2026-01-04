"""
Analytics Models
SQLAlchemy models for analytics, data points, and leaderboards
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


class Analytics(BaseModel):
    """Analytics table"""
    __tablename__ = "analytics"
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    skill_progress: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    readiness_trends: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    assessment_history: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    topic_coverage: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    study_time: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    leaderboards: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    summary: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="analytics")
    
    # Indexes
    __table_args__ = (
        Index("idx_analytics_user_id", "user_id"),
    )


class AnalyticsDataPoint(BaseModel):
    """Analytics data points table"""
    __tablename__ = "analytics_data_points"
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(DECIMAL(10, 4), nullable=False)
    metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="analytics_data_points")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "metric_type IN ('skill_progress', 'readiness_trend', 'assessment_history', 'topic_coverage', "
            "'study_time', 'simulation_performance', 'leaderboard_ranking')",
            name="check_metric_type"
        ),
        Index("idx_analytics_data_points_user_id", "user_id"),
        Index("idx_analytics_data_points_metric_type", "metric_type"),
        Index("idx_analytics_data_points_timestamp", "timestamp"),
    )


class Leaderboard(BaseModel):
    """Leaderboards table"""
    __tablename__ = "leaderboards"
    leaderboard_type: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    entries: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    total_participants: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "leaderboard_type IN ('skill_mastery', 'assessment_scores', 'readiness_score', 'study_time', 'completion_rate')",
            name="check_leaderboard_type"
        ),
    )
