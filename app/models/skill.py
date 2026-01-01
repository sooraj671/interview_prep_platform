from sqlalchemy import Column, String, Boolean, Text, ForeignKey, JSONB
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel

class Skill(BaseModel):
    __tablename__ = "skills"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50))  # Technical, Soft Skills, Domain-specific
    embedding = Column(ARRAY)  # For semantic similarity matching
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_skills = relationship("UserSkill", back_populates="skill")
    questions = relationship("Question", back_populates="skill")

class Domain(BaseModel):
    __tablename__ = "domains"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    embedding = Column(ARRAY)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    roles = relationship("Role", back_populates="domain")

class Role(BaseModel):
    __tablename__ = "roles"
    
    title = Column(String(100), nullable=False)
    description = Column(Text)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"))
    required_skills = Column(JSONB)  # Array of skill IDs with required levels
    embedding = Column(ARRAY)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    domain = relationship("Domain", back_populates="roles")
    roadmaps = relationship("Roadmap", back_populates="role")
