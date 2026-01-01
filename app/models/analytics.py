from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime, CheckConstraint, JSONB
from sqlalchemy.dialects.postgresql import UUID, ARRAY, INET
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel

class UserActivity(BaseModel):
    __tablename__ = "user_activities"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # 'login', 'assessment', 'simulation', 'roadmap_view'
    entity_type = Column(String(50))  # 'skill', 'topic', 'roadmap'
    entity_id = Column(UUID(as_uuid=True))
    metadata = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="activities")

class Leaderboard(BaseModel):
    __tablename__ = "leaderboards"
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    criteria = Column(JSONB)  # Ranking criteria
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"))
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    entries = relationship("LeaderboardEntry", back_populates="leaderboard", cascade="all, delete-orphan")

class LeaderboardEntry(BaseModel):
    __tablename__ = "leaderboard_entries"
    
    leaderboard_id = Column(UUID(as_uuid=True), ForeignKey("leaderboards.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rank = Column(Integer, nullable=False)
    score = Column(CheckConstraint('score >= 0'), nullable=False)
    metadata = Column(JSONB)  # Additional ranking data
    calculated_at = Column(DateTime(timezone=True))
    
    # Relationships
    leaderboard = relationship("Leaderboard", back_populates="entries")
    user = relationship("User")
