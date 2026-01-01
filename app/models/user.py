from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import BaseModel

class UserTypeEnum(enum.Enum):
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"

class AuthProviderEnum(enum.Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    EMAIL = "email"

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    auth_provider = Column(ENUM(AuthProviderEnum), nullable=False)
    provider_id = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255))  # For email auth only
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    user_type = Column(ENUM(UserTypeEnum), default=UserTypeEnum.CANDIDATE)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    experiences = relationship("UserExperience", back_populates="user", cascade="all, delete-orphan")
    education = relationship("UserEducation", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("InterviewFeedback", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")

class UserProfile(BaseModel):
    __tablename__ = "user_profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_picture_url = Column(Text)
    phone_number = Column(String(20))
    bio = Column(Text)
    location_city = Column(String(100))
    location_country = Column(String(100))
    years_of_experience = Column(Integer, CheckConstraint('years_of_experience >= 0'))
    linkedin_url = Column(Text)
    github_url = Column(Text)
    resume_url = Column(Text)
    resume_parsed_data = Column(JSONB)  # Parsed resume skills, projects, etc.
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    
    # Relationships
    user = relationship("User", back_populates="profile")

class UserSkill(BaseModel):
    __tablename__ = "user_skills"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    self_rating = Column(Integer, CheckConstraint('self_rating >= 1 AND self_rating <= 10'))
    assessed_score = Column(CheckConstraint('assessed_score >= 0 AND assessed_score <= 100'))
    confidence_level = Column(Integer, CheckConstraint('confidence_level >= 1 AND confidence_level <= 10'))
    last_assessed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")

class UserExperience(BaseModel):
    __tablename__ = "user_experiences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(200), nullable=False)
    role_title = Column(String(150), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_current_job = Column(Boolean, default=False)
    skills_used = Column(JSONB)  # Array of skill IDs
    projects = Column(JSONB)  # Project details
    
    # Relationships
    user = relationship("User", back_populates="experiences")

class UserEducation(BaseModel):
    __tablename__ = "user_education"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    institution_name = Column(String(200), nullable=False)
    degree = Column(String(100), nullable=False)
    field_of_study = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    gpa = Column(CheckConstraint('gpa >= 0 AND gpa <= 4.0'))
    
    # Relationships
    user = relationship("User", back_populates="education")
