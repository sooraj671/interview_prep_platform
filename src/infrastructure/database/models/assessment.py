"""
Assessment Management Models
SQLAlchemy models for assessments, questions, responses, evaluations, and skill assessments
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


class Assessment(BaseModel):
    """Assessments table"""
    __tablename__ = "assessments"
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    assessment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_ids: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    difficulty: Mapped[str] = mapped_column(
        String(50), 
        default="intermediate",
        server_default=text("'intermediate'")
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, server_default=text("60"))
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True
    )
    roadmap_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("roadmaps.id", ondelete="CASCADE"), 
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), 
        default="created",
        server_default=text("'created'")
    )
    adaptive_difficulty: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("TRUE"))
    allow_hints: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("TRUE"))
    allow_review: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("TRUE"))
    randomize_questions: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("TRUE"))
    passing_score: Mapped[int] = mapped_column(Integer, default=70, server_default=text("70"))
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, server_default=text("3"))
    time_limit_per_question: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roadmap: Mapped[Optional["Roadmap"]] = relationship("Roadmap")
    questions: Mapped[List["AssessmentQuestion"]] = relationship(
        "AssessmentQuestion", 
        back_populates="assessment", 
        cascade="all, delete-orphan"
    )
    responses: Mapped[List["AssessmentResponse"]] = relationship(
        "AssessmentResponse", 
        back_populates="assessment", 
        cascade="all, delete-orphan"
    )
    evaluations: Mapped[List["QuestionEvaluation"]] = relationship(
        "QuestionEvaluation", 
        back_populates="assessment", 
        cascade="all, delete-orphan"
    )
    skill_assessments: Mapped[List["SkillAssessment"]] = relationship(
        "SkillAssessment", 
        back_populates="assessment", 
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "assessment_type IN ('technical', 'behavioral', 'problem_solving', 'system_design', 'coding', 'situational', 'mixed')",
            name="check_assessment_type"
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_assessment_difficulty"
        ),
        CheckConstraint(
            "status IN ('created', 'started', 'in_progress', 'completed', 'expired', 'abandoned')",
            name="check_assessment_status"
        ),
        Index("idx_assessments_user_id", "user_id"),
        Index("idx_assessments_status", "status"),
        Index("idx_assessments_type", "assessment_type"),
    )


class AssessmentQuestion(BaseModel):
    """Assessment questions table"""
    __tablename__ = "assessment_questions"
    assessment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("assessments.id", ondelete="CASCADE"), 
        nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    difficulty: Mapped[str] = mapped_column(
        String(50), 
        default="intermediate",
        server_default=text("'intermediate'")
    )
    estimated_time: Mapped[int] = mapped_column(Integer, default=5, server_default=text("5"))  # minutes
    points: Mapped[int] = mapped_column(Integer, default=10, server_default=text("10"))
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
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )  # For multiple choice
    correct_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_answer_format: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    code_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    constraints: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    evaluation_criteria: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    hints: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    explanation: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    tags: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    dependencies: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    
    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="questions")
    responses: Mapped[List["AssessmentResponse"]] = relationship(
        "AssessmentResponse", 
        back_populates="question", 
        cascade="all, delete-orphan"
    )
    evaluations: Mapped[List["QuestionEvaluation"]] = relationship(
        "QuestionEvaluation", 
        back_populates="question", 
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('multiple_choice', 'theoretical', 'coding', 'design', 'essay', 'practical')",
            name="check_question_type"
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name="check_question_difficulty"
        ),
        Index("idx_assessment_questions_assessment_id", "assessment_id"),
    )


class AssessmentResponse(BaseModel):
    """Assessment responses table"""
    __tablename__ = "assessment_responses"
    assessment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("assessments.id", ondelete="CASCADE"), 
        nullable=False
    )
    question_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("assessment_questions.id", ondelete="CASCADE"), 
        nullable=False
    )
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    time_taken: Mapped[int] = mapped_column(Integer, nullable=False)  # seconds
    hints_used: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    attempts: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="responses")
    question: Mapped["AssessmentQuestion"] = relationship("AssessmentQuestion", back_populates="responses")
    
    # Constraints
    __table_args__ = (
        Index("idx_assessment_responses_assessment_id", "assessment_id"),
    )


class QuestionEvaluation(BaseModel):
    """Question evaluations table"""
    __tablename__ = "question_evaluations"
    assessment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("assessments.id", ondelete="CASCADE"), 
        nullable=False
    )
    question_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("assessment_questions.id", ondelete="CASCADE"), 
        nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    correctness: Mapped[int] = mapped_column(Integer, nullable=False)
    efficiency: Mapped[int] = mapped_column(Integer, nullable=False)
    style: Mapped[int] = mapped_column(Integer, nullable=False)
    completeness: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("FALSE"))
    feedback: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    detailed_analysis: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict, 
        server_default=text("'{}'::jsonb")
    )
    improvement_areas: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    next_steps: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    encouragement: Mapped[str] = mapped_column(Text, default="", server_default=text("''"))
    
    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="evaluations")
    question: Mapped["AssessmentQuestion"] = relationship("AssessmentQuestion", back_populates="evaluations")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="check_score_range"),
        CheckConstraint("correctness >= 0 AND correctness <= 100", name="check_correctness_range"),
        CheckConstraint("efficiency >= 0 AND efficiency <= 100", name="check_efficiency_range"),
        CheckConstraint("style >= 0 AND style <= 100", name="check_style_range"),
        CheckConstraint("completeness >= 0 AND completeness <= 100", name="check_completeness_range"),
    )


class SkillAssessment(BaseModel):
    """Skill assessments table"""
    __tablename__ = "skill_assessments"
    assessment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("assessments.id", ondelete="CASCADE"), 
        nullable=False
    )
    skill: Mapped[str] = mapped_column(String(255), nullable=False)
    current_level: Mapped[int] = mapped_column(Integer, nullable=False)
    target_level: Mapped[int] = mapped_column(Integer, nullable=False)
    demonstrated_level: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_level: Mapped[str] = mapped_column(
        String(50), 
        default="low",
        server_default=text("'low'")
    )
    recommendations: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB, 
        default=list, 
        server_default=text("'[]'::jsonb")
    )
    
    # Relationships
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="skill_assessments")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("current_level >= 1 AND current_level <= 10", name="check_current_level_range"),
        CheckConstraint("target_level >= 1 AND target_level <= 10", name="check_target_level_range"),
        CheckConstraint("demonstrated_level >= 1 AND demonstrated_level <= 10", name="check_demonstrated_level_range"),
        CheckConstraint(
            "confidence_level IN ('low', 'medium', 'high')",
            name="check_confidence_level"
        ),
    )
