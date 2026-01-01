from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime, Enum, CheckConstraint, JSONB
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import BaseModel

class QuestionTypeEnum(enum.Enum):
    MCQ = "mcq"
    THEORETICAL = "theoretical"
    CODING = "coding"
    BEHAVIORAL = "behavioral"

class SkillLevelEnum(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Question(BaseModel):
    __tablename__ = "questions"
    
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"))
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"))
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionTypeEnum), nullable=False)
    options = Column(JSONB)  # For MCQ questions
    correct_answer = Column(Text)
    explanation = Column(Text)
    difficulty_level = Column(Enum(SkillLevelEnum))
    time_limit_seconds = Column(Integer)
    embedding = Column(ARRAY)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    skill = relationship("Skill", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    assessment_answers = relationship("AssessmentAnswer", back_populates="question")

class AssessmentStatusEnum(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"

class Assessment(BaseModel):
    __tablename__ = "assessments"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"))
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"))
    assessment_type = Column(String(50))  # 'skill_assessment', 'topic_assessment', 'simulation'
    status = Column(Enum(AssessmentStatusEnum), default=AssessmentStatusEnum.PENDING)
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    score_percentage = Column(CheckConstraint('score_percentage >= 0 AND score_percentage <= 100'))
    time_taken_seconds = Column(Integer)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    topic = relationship("Topic")
    skill = relationship("Skill")
    answers = relationship("AssessmentAnswer", back_populates="assessment", cascade="all, delete-orphan")

class AssessmentAnswer(BaseModel):
    __tablename__ = "assessment_answers"
    
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    user_answer = Column(Text)
    is_correct = Column(Boolean)
    time_taken_seconds = Column(Integer)
    feedback = Column(Text)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="answers")
    question = relationship("Question", back_populates="assessment_answers")
