from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime, Enum, CheckConstraint, JSONB
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import BaseModel

class RoadmapStatusEnum(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    REGENERATED = "regenerated"

class SkillLevelEnum(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Roadmap(BaseModel):
    __tablename__ = "roadmaps"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(RoadmapStatusEnum), default=RoadmapStatusEnum.ACTIVE)
    total_topics = Column(Integer, default=0)
    covered_topics = Column(Integer, default=0)
    progress_percentage = Column(CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100'), default=0)
    embedding = Column(ARRAY)
    generated_by_ai = Column(Boolean, default=True)
    ai_model_version = Column(String(50))
    
    # Relationships
    user = relationship("User", back_populates="roadmaps")
    role = relationship("Role", back_populates="roadmaps")
    topics = relationship("Topic", back_populates="roadmap", cascade="all, delete-orphan")

class Topic(BaseModel):
    __tablename__ = "topics"
    
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content = Column(Text)  # Learning content
    difficulty_level = Column(Enum(SkillLevelEnum))
    estimated_hours = Column(Integer)
    prerequisites = Column(JSONB)  # Array of topic IDs
    skills_covered = Column(JSONB)  # Array of skill IDs
    order_index = Column(Integer, nullable=False)
    is_covered = Column(Boolean, default=False)
    embedding = Column(ARRAY)
    
    # Relationships
    roadmap = relationship("Roadmap", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
    assessments = relationship("Assessment", back_populates="topic")
