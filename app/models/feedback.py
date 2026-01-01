from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, CheckConstraint, JSONB
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel

class InterviewType(BaseModel):
    __tablename__ = "interview_types"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    feedbacks = relationship("InterviewFeedback", back_populates="interview_type")

class InterviewFeedback(BaseModel):
    __tablename__ = "interview_feedbacks"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interview_type_id = Column(UUID(as_uuid=True), ForeignKey("interview_types.id"))
    company_name = Column(String(200))
    role_title = Column(String(150))
    interview_date = Column(DateTime)
    questions_asked = Column(JSONB)
    feedback_text = Column(Text)
    strengths = Column(JSONB)
    weaknesses = Column(JSONB)
    overall_rating = Column(Integer, CheckConstraint('overall_rating >= 1 AND overall_rating <= 5'))
    embedding = Column(ARRAY)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")
    interview_type = relationship("InterviewType", back_populates="feedbacks")
