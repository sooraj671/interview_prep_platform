"""
Interview Preparation Platform - Simple ORM Version
Direct SQLAlchemy without complex domain layer
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator

# Helper function for type conversion
def convert_model_types(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert UUID and datetime objects to strings for API responses"""
    # Convert UUID to string
    if 'id' in data and hasattr(data['id'], '__str__'):
        data['id'] = str(data['id'])
    
    # Convert UUID fields that might have different names
    uuid_fields = [
        'user_id', 'skill_id', 'roadmap_id', 'assessment_id', 'topic_id', 
        'resource_id', 'exercise_id', 'milestone_id', 'session_id',
        'question_id', 'response_id', 'evaluation_id', 'leaderboard_id'
    ]
    for uuid_field in uuid_fields:
        if uuid_field in data and hasattr(data[uuid_field], '__str__'):
            data[uuid_field] = str(data[uuid_field])
    
    # Convert datetime fields to ISO format strings
    datetime_fields = [
        'created_at', 'updated_at', 'started_at', 'completed_at', 'expires_at', 
        'last_activity_at', 'last_active', 'timestamp', 'target_date', 'last_updated',
        'last_login', 'last_used', 'submitted_at', 'evaluated_at', 'completed_at'
    ]
    for field in datetime_fields:
        if field in data and hasattr(data[field], 'isoformat'):
            data[field] = data[field].isoformat()
    
    return data

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQLAlchemy imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.sql import text

# Import models directly
from infrastructure.database.models.base import Base
from infrastructure.database.models.user import User as UserModel, UserProfile, UserStats
from infrastructure.database.models.skill import (
    Skill as SkillModel, SkillTopic, SkillResource, UserSkillProgress
)
from infrastructure.database.models.roadmap import (
    Roadmap as RoadmapModel, RoadmapTopic, LearningResource, 
    PracticeExercise, RoadmapMilestone
)
from infrastructure.database.models.assessment import (
    Assessment as AssessmentModel, AssessmentQuestion, AssessmentResponse,
    QuestionEvaluation, SkillAssessment
)
from infrastructure.database.models.analytics import (
    Analytics as AnalyticsModel, AnalyticsDataPoint, Leaderboard
)

# Pydantic models for API
class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    role: str = "candidate"
    bio: str = ""
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    years_of_experience: Optional[int] = None
    domain: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    skills: List[str] = []
    preferences: Dict[str, Any] = {}
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = {'candidate', 'interviewer', 'admin', 'recruiter'}
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(sorted(valid_roles))}")
        return v

# Skills Pydantic models
class SkillCreate(BaseModel):
    """Skill creation model"""
    name: str
    category: str
    description: str = ""
    difficulty: str = "intermediate"
    tags: List[Dict[str, Any]] = []
    prerequisites: List[Dict[str, Any]] = []
    related_skills: List[Dict[str, Any]] = []
    industry_relevance: Dict[str, Any] = {}
    average_salary_impact: Optional[float] = None
    learning_path: List[Dict[str, Any]] = []
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = {
            'programming', 'framework', 'database', 'cloud', 'devops', 'mobile',
            'frontend', 'backend', 'full_stack', 'data_science', 'machine_learning',
            'ai', 'blockchain', 'security', 'testing', 'design', 'project_management',
            'soft_skills', 'domain_specific'
        }
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(sorted(valid_categories))}")
        return v
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        valid_difficulties = {'beginner', 'intermediate', 'advanced', 'expert'}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return v

class SkillUpdate(BaseModel):
    """Skill update model"""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None
    prerequisites: Optional[List[Dict[str, Any]]] = None
    related_skills: Optional[List[Dict[str, Any]]] = None
    industry_relevance: Optional[Dict[str, Any]] = None
    average_salary_impact: Optional[float] = None
    learning_path: Optional[List[Dict[str, Any]]] = None
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is None:
            return v
        valid_categories = {
            'programming', 'framework', 'database', 'cloud', 'devops', 'mobile',
            'frontend', 'backend', 'full_stack', 'data_science', 'machine_learning',
            'ai', 'blockchain', 'security', 'testing', 'design', 'project_management',
            'soft_skills', 'domain_specific'
        }
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(sorted(valid_categories))}")
        return v
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v is None:
            return v
        valid_difficulties = {'beginner', 'intermediate', 'advanced', 'expert'}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return v

class SkillResponse(BaseModel):
    """Skill response model"""
    id: str
    name: str
    category: str
    description: str
    difficulty: str
    tags: List[Dict[str, Any]]
    prerequisites: List[Dict[str, Any]]
    related_skills: List[Dict[str, Any]]
    industry_relevance: Dict[str, Any]
    average_salary_impact: Optional[float]
    learning_path: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class SkillTopicCreate(BaseModel):
    """Skill topic creation model"""
    skill_id: str
    name: str
    description: str = ""
    difficulty: str = "intermediate"
    prerequisites: List[Dict[str, Any]] = []
    learning_objectives: List[Dict[str, Any]] = []
    estimated_hours: int = 0
    resources: List[Dict[str, Any]] = []

class SkillTopicResponse(BaseModel):
    """Skill topic response model"""
    id: str
    skill_id: str
    name: str
    description: str
    difficulty: str
    prerequisites: List[Dict[str, Any]]
    learning_objectives: List[Dict[str, Any]]
    estimated_hours: int
    resources: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class SkillResourceCreate(BaseModel):
    """Skill resource creation model"""
    skill_id: str
    type: str
    title: str
    url: Optional[str] = None
    description: str = ""
    difficulty: str = "intermediate"
    rating: Optional[float] = None
    duration_hours: Optional[int] = None
    cost: Optional[str] = None
    provider: Optional[str] = None

class SkillResourceResponse(BaseModel):
    """Skill resource response model"""
    id: str
    skill_id: str
    type: str
    title: str
    url: Optional[str]
    description: str
    difficulty: str
    rating: Optional[float]
    duration_hours: Optional[int]
    cost: Optional[str]
    provider: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class UserSkillProgressCreate(BaseModel):
    """User skill progress creation model"""
    user_id: str
    skill_id: str
    current_level: int = 1
    target_level: int = 10
    demonstrated_level: int = 1
    confidence_level: str = "low"
    progress_data: Dict[str, Any] = {}

class UserSkillProgressUpdate(BaseModel):
    """User skill progress update model"""
    current_level: Optional[int] = None
    target_level: Optional[int] = None
    demonstrated_level: Optional[int] = None
    confidence_level: Optional[str] = None
    progress_data: Optional[Dict[str, Any]] = None

class UserSkillProgressResponse(BaseModel):
    """User skill progress response model"""
    id: str
    user_id: str
    skill_id: str
    current_level: int
    target_level: int
    demonstrated_level: int
    confidence_level: str
    progress_data: Dict[str, Any]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

# Roadmap Pydantic models
class RoadmapCreate(BaseModel):
    """Roadmap creation model"""
    user_id: str
    title: str
    description: str = ""
    target_role: Optional[str] = None
    duration_weeks: int = 12
    difficulty: str = "intermediate"
    ai_generated: bool = False
    generation_prompt: Optional[str] = None

class RoadmapUpdate(BaseModel):
    """Roadmap update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    target_role: Optional[str] = None
    duration_weeks: Optional[int] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None
    progress_percentage: Optional[int] = None
    total_topics: Optional[int] = None
    completed_topics: Optional[int] = None
    ai_generated: Optional[bool] = None
    generation_prompt: Optional[str] = None
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v is None:
            return v
        valid_difficulties = {'beginner', 'intermediate', 'advanced', 'expert'}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = {'not_started', 'in_progress', 'paused', 'completed', 'archived'}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(sorted(valid_statuses))}")
        return v
    
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class RoadmapResponse(BaseModel):
    """Roadmap response model"""
    id: str
    user_id: str
    title: str
    description: str
    target_role: Optional[str]
    duration_weeks: int
    difficulty: str
    status: str
    progress_percentage: int
    total_topics: int
    completed_topics: int
    ai_generated: bool
    generation_prompt: Optional[str]
    created_at: str
    updated_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class RoadmapTopicCreate(BaseModel):
    """Roadmap topic creation model"""
    roadmap_id: str
    title: str
    description: str = ""
    difficulty: str = "intermediate"
    estimated_hours: int = 0
    prerequisites: List[Dict[str, Any]] = []
    learning_objectives: List[Dict[str, Any]] = []
    content: str = ""
    skills_covered: List[Dict[str, Any]] = []
    assessment_criteria: List[Dict[str, Any]] = []
    milestone: bool = False
    status: str = "not_started"
    progress_percentage: int = 0
    time_spent_hours: int = 0
    notes: str = ""
    week_number: Optional[int] = None
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        valid_difficulties = {'beginner', 'intermediate', 'advanced', 'expert'}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = {'not_started', 'in_progress', 'completed', 'skipped'}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(sorted(valid_statuses))}")
        return v

class RoadmapTopicResponse(BaseModel):
    """Roadmap topic response model"""
    id: str
    roadmap_id: str
    title: str
    description: str
    difficulty: str
    estimated_hours: int
    prerequisites: List[Dict[str, Any]]
    learning_objectives: List[Dict[str, Any]]
    content: str
    skills_covered: List[Dict[str, Any]]
    assessment_criteria: List[Dict[str, Any]]
    milestone: bool
    status: str
    progress_percentage: int
    time_spent_hours: int
    notes: str
    week_number: Optional[int]
    created_at: str
    updated_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class PracticeExerciseCreate(BaseModel):
    """Practice exercise creation model"""
    roadmap_topic_id: str
    type: str
    title: str
    description: str = ""
    estimated_time: int = 30  # minutes
    difficulty: str = "intermediate"
    instructions: str = ""
    resources: List[Dict[str, Any]] = []
    success_criteria: List[Dict[str, Any]] = []
    description: str
    estimated_time: int
    difficulty: str
    instructions: str
    resources: List[Dict[str, Any]]
    success_criteria: List[Dict[str, Any]]
    completed: bool
    completed_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class RoadmapTopicUpdate(BaseModel):
    """Roadmap topic update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[int] = None
    prerequisites: Optional[List[Dict[str, Any]]] = None
    learning_objectives: Optional[List[Dict[str, Any]]] = None
    content: Optional[str] = None
    skills_covered: Optional[List[Dict[str, Any]]] = None
    assessment_criteria: Optional[List[Dict[str, Any]]] = None
    milestone: Optional[bool] = None
    status: Optional[str] = None
    progress_percentage: Optional[int] = None
    time_spent_hours: Optional[int] = None
    notes: Optional[str] = None
    week_number: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v is None:
            return v
        valid_difficulties = {'beginner', 'intermediate', 'advanced', 'expert'}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = {'not_started', 'in_progress', 'completed', 'skipped'}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(sorted(valid_statuses))}")
        return v

class LearningResourceCreate(BaseModel):
    """Learning resource creation model"""
    roadmap_topic_id: str
    type: str
    title: str
    url: Optional[str] = None
    description: str = ""
    difficulty: str = "intermediate"
    duration_hours: int = 0
    cost: Optional[str] = None
    provider: Optional[str] = None
    rating: Optional[float] = None
    is_required: bool = True
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid_types = {'course', 'book', 'tutorial', 'documentation', 'tool', 'video'}
        if v not in valid_types:
            raise ValueError(f"Type must be one of: {', '.join(sorted(valid_types))}")
        return v
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        valid_difficulties = {'beginner', 'intermediate', 'advanced', 'expert'}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return v

class LearningResourceResponse(BaseModel):
    """Learning resource response model"""
    id: str
    roadmap_topic_id: str
    type: str
    title: str
    url: Optional[str]
    description: str
    difficulty: str
    duration_hours: int
    cost: Optional[str]
    provider: Optional[str]
    rating: Optional[float]
    is_required: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class PracticeExerciseCreate(BaseModel):
    """Practice exercise creation model"""
    roadmap_topic_id: str
    type: str
    title: str
    description: str = ""
    estimated_time: int = 30  # minutes
    difficulty: str = "intermediate"
    instructions: str = ""
    resources: List[Dict[str, Any]] = []
    success_criteria: List[Dict[str, Any]] = []
    completed: bool = False
    completed_at: Optional[str] = None
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid_types = {'coding', 'project', 'reading', 'quiz', 'simulation'}
        if v not in valid_types:
            raise ValueError(f"Type must be one of: {', '.join(sorted(valid_types))}")
        return v
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        valid_difficulties = {'beginner', 'intermediate', 'advanced', 'expert'}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return v

class PracticeExerciseResponse(BaseModel):
    """Practice exercise response model"""
    id: str
    roadmap_topic_id: str
    type: str
    title: str
    description: str
    estimated_time: int
    difficulty: str
    instructions: str
    resources: List[Dict[str, Any]]
    success_criteria: List[Dict[str, Any]]
    completed: bool
    completed_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class RoadmapMilestoneCreate(BaseModel):
    """Roadmap milestone creation model"""
    roadmap_id: str
    title: str
    description: str = ""
    week_number: int
    skills_to_master: List[Dict[str, Any]] = []
    assessment_type: str = "quiz"
    target_date: Optional[str] = None

class RoadmapMilestoneResponse(BaseModel):
    """Roadmap milestone response model"""
    id: str
    roadmap_id: str
    title: str
    description: str
    week_number: int
    skills_to_master: List[Dict[str, Any]]
    assessment_type: str
    status: str
    target_date: Optional[str]
    completed_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

# Assessment Pydantic models
class AssessmentCreate(BaseModel):
    """Assessment creation model"""
    title: str
    assessment_type: str
    skill_ids: List[Dict[str, Any]] = []
    difficulty: str = "intermediate"
    duration_minutes: int = 60
    user_id: Optional[str] = None
    roadmap_id: Optional[str] = None
    status: str = "created"
    adaptive_difficulty: bool = True
    allow_hints: bool = True
    allow_review: bool = True
    randomize_questions: bool = True
    passing_score: int = 70
    max_attempts: int = 3
    time_limit_per_question: Optional[int] = None
    
    @field_validator('assessment_type')
    @classmethod
    def validate_assessment_type(cls, v):
        valid_types = {'technical', 'behavioral', 'problem_solving', 'system_design', 'coding', 'situational', 'mixed'}
        if v not in valid_types:
            raise ValueError(f"Assessment type must be one of: {', '.join(sorted(valid_types))}")
        return v
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        valid_difficulties = {'beginner', 'intermediate', 'advanced', 'expert'}
        if v not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(sorted(valid_difficulties))}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = {'created', 'started', 'in_progress', 'completed', 'expired', 'abandoned'}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(sorted(valid_statuses))}")
        return v

class AssessmentUpdate(BaseModel):
    """Assessment update model"""
    title: Optional[str] = None
    assessment_type: Optional[str] = None
    skill_ids: Optional[List[Dict[str, Any]]] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    adaptive_difficulty: Optional[bool] = None
    allow_hints: Optional[bool] = None
    allow_review: Optional[bool] = None
    randomize_questions: Optional[bool] = None
    passing_score: Optional[int] = None
    max_attempts: Optional[int] = None
    time_limit_per_question: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    expires_at: Optional[str] = None
    last_activity_at: Optional[str] = None

class AssessmentResponse(BaseModel):
    """Assessment response model"""
    id: str
    title: str
    assessment_type: str
    skill_ids: List[Dict[str, Any]]
    difficulty: str
    duration_minutes: int
    user_id: Optional[str]
    roadmap_id: Optional[str]
    status: str
    adaptive_difficulty: bool
    allow_hints: bool
    allow_review: bool
    randomize_questions: bool
    passing_score: int
    max_attempts: int
    time_limit_per_question: Optional[int]
    started_at: Optional[str]
    completed_at: Optional[str]
    expires_at: Optional[str]
    last_activity_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class AssessmentQuestionCreate(BaseModel):
    """Assessment question creation model"""
    assessment_id: str
    type: str
    title: str
    description: str = ""
    difficulty: str = "intermediate"
    estimated_time: int = 5  # minutes
    points: int = 10
    prerequisites: List[Dict[str, Any]] = []
    learning_objectives: List[Dict[str, Any]] = []
    question: str
    options: List[Dict[str, Any]] = []
    correct_answer: Optional[str] = None
    expected_answer_format: Optional[str] = None
    code_template: Optional[str] = None
    constraints: List[Dict[str, Any]] = []
    evaluation_criteria: List[Dict[str, Any]] = []
    hints: List[Dict[str, Any]] = []
    explanation: str = ""
    tags: List[Dict[str, Any]] = []
    dependencies: List[Dict[str, Any]] = []

class AssessmentQuestionResponse(BaseModel):
    """Assessment question response model"""
    id: str
    assessment_id: str
    type: str
    title: str
    description: str
    difficulty: str
    estimated_time: int
    points: int
    prerequisites: List[Dict[str, Any]]
    learning_objectives: List[Dict[str, Any]]
    question: str
    options: List[Dict[str, Any]]
    correct_answer: Optional[str]
    expected_answer_format: Optional[str]
    code_template: Optional[str]
    constraints: List[Dict[str, Any]]
    evaluation_criteria: List[Dict[str, Any]]
    hints: List[Dict[str, Any]]
    explanation: str
    tags: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class AssessmentResponseCreate(BaseModel):
    """Assessment response creation model"""
    assessment_id: str
    question_id: str
    answer: str
    time_taken: int  # seconds
    hints_used: List[Dict[str, Any]] = []
    attempts: int = 1

class AssessmentResponseResponse(BaseModel):
    """Assessment response response model"""
    id: str
    assessment_id: str
    question_id: str
    answer: str
    time_taken: int
    hints_used: List[Dict[str, Any]]
    attempts: int
    submitted_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class QuestionEvaluationCreate(BaseModel):
    """Question evaluation creation model"""
    assessment_id: str
    question_id: str
    score: int
    correctness: int
    efficiency: int
    style: int
    completeness: int
    is_correct: bool = False
    feedback: str = ""
    detailed_analysis: Dict[str, Any] = {}
    improvement_areas: List[Dict[str, Any]] = []
    next_steps: List[Dict[str, Any]] = []
    encouragement: str = ""

class QuestionEvaluationResponse(BaseModel):
    """Question evaluation response model"""
    id: str
    assessment_id: str
    question_id: str
    score: int
    correctness: int
    efficiency: int
    style: int
    completeness: int
    is_correct: bool
    feedback: str
    detailed_analysis: Dict[str, Any]
    improvement_areas: List[Dict[str, Any]]
    next_steps: List[Dict[str, Any]]
    encouragement: str
    evaluated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class SkillAssessmentCreate(BaseModel):
    """Skill assessment creation model"""
    assessment_id: str
    skill: str
    current_level: int
    target_level: int
    demonstrated_level: int
    confidence_level: str = "low"
    recommendations: List[Dict[str, Any]] = []

class SkillAssessmentResponse(BaseModel):
    """Skill assessment response model"""
    id: str
    assessment_id: str
    skill: str
    current_level: int
    target_level: int
    demonstrated_level: int
    confidence_level: str
    recommendations: List[Dict[str, Any]]
    created_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

# Analytics Pydantic models
class AnalyticsCreate(BaseModel):
    """Analytics creation model"""
    user_id: str
    skill_progress: Dict[str, Any] = {}
    readiness_trends: Dict[str, Any] = {}
    assessment_history: Dict[str, Any] = {}
    topic_coverage: Dict[str, Any] = {}
    study_time: Dict[str, Any] = {}
    leaderboards: Dict[str, Any] = {}
    summary: Dict[str, Any] = {}

class AnalyticsUpdate(BaseModel):
    """Analytics update model"""
    skill_progress: Optional[Dict[str, Any]] = None
    readiness_trends: Optional[Dict[str, Any]] = None
    assessment_history: Optional[Dict[str, Any]] = None
    topic_coverage: Optional[Dict[str, Any]] = None
    study_time: Optional[Dict[str, Any]] = None
    leaderboards: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None

class AnalyticsResponse(BaseModel):
    """Analytics response model"""
    id: str
    user_id: str
    skill_progress: Dict[str, Any]
    readiness_trends: Dict[str, Any]
    assessment_history: Dict[str, Any]
    topic_coverage: Dict[str, Any]
    study_time: Dict[str, Any]
    leaderboards: Dict[str, Any]
    summary: Dict[str, Any]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class AnalyticsDataPointCreate(BaseModel):
    """Analytics data point creation model"""
    user_id: str
    metric_type: str
    metric_name: str
    value: float
    metadata: Dict[str, Any] = {}
    
    @field_validator('metric_type')
    @classmethod
    def validate_metric_type(cls, v):
        valid_types = {'skill_progress', 'readiness_trend', 'assessment_history', 'topic_coverage', 'study_time', 'simulation_performance', 'leaderboard_ranking'}
        if v not in valid_types:
            raise ValueError(f"Metric type must be one of: {', '.join(sorted(valid_types))}")
        return v

class AnalyticsDataPointResponse(BaseModel):
    """Analytics data point response model"""
    id: str
    user_id: str
    metric_type: str
    metric_name: str
    value: float
    metadata: Dict[str, Any]
    timestamp: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle field mapping and type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        # Handle the field mapping from database column to model field
        if 'metadata_json' in data:
            data['metadata'] = data.pop('metadata_json')
        
        data = convert_model_types(data)
        return super().model_validate(data)

class LeaderboardCreate(BaseModel):
    """Leaderboard creation model"""
    leaderboard_type: str
    category: str
    entries: List[Dict[str, Any]] = []
    total_participants: int = 0
    
    @field_validator('leaderboard_type')
    @classmethod
    def validate_leaderboard_type(cls, v):
        valid_types = {'skill_mastery', 'assessment_scores', 'readiness_score', 'study_time', 'completion_rate'}
        if v not in valid_types:
            raise ValueError(f"Leaderboard type must be one of: {', '.join(sorted(valid_types))}")
        return v

class LeaderboardUpdate(BaseModel):
    """Leaderboard update model"""
    leaderboard_type: Optional[str] = None
    category: Optional[str] = None
    entries: Optional[List[Dict[str, Any]]] = None
    total_participants: Optional[int] = None

class LeaderboardResponse(BaseModel):
    """Leaderboard response model"""
    id: str
    leaderboard_type: str
    category: str
    entries: List[Dict[str, Any]]
    total_participants: int
    last_updated: str
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    role: str
    auth_provider: str
    provider_id: Optional[str]
    status: str
    email_verified: bool
    phone_verified: bool
    two_factor_enabled: bool
    created_at: str
    updated_at: str
    last_login: Optional[str]
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle type conversion"""
        if hasattr(obj, '__dict__'):
            data = obj.__dict__.copy()
        else:
            data = dict(obj)
        
        data = convert_model_types(data)
        return super().model_validate(data)

# Database setup
class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Convert postgresql:// to postgresql+asyncpg:// for async support
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        self.engine = create_async_engine(
            self.database_url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            future=True
        )
        
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncSession:
        """Get an async session"""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Close the engine"""
        await self.engine.dispose()

# Global database manager
db_manager = DatabaseManager()

async def get_db_session() -> AsyncSession:
    """Dependency to get database session"""
    async for session in db_manager.get_session():
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Interview Preparation Platform with Simple ORM...")
    
    # Initialize database tables if needed
    try:
        await db_manager.create_tables()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database tables: {e}")
    
    logger.info("✅ Application started successfully")
    yield
    
    logger.info("🛑 Shutting down Interview Preparation Platform...")
    await db_manager.close()
    logger.info("✅ Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Interview Preparation Platform - Simple ORM",
    description="AI-powered interview preparation platform with direct SQLAlchemy",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.router.lifespan_context = lifespan

# Helper function to map model to response
def map_user_to_response(user_model: UserModel) -> UserResponse:
    """Map User model to UserResponse"""
    # Return basic user info without relationships for now
    return UserResponse(
        id=str(user_model.id),
        email=user_model.email,
        password_hash=user_model.password_hash,
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        role=user_model.role,
        auth_provider=user_model.auth_provider,
        provider_id=user_model.provider_id,
        status=user_model.status,
        email_verified=user_model.email_verified,
        phone_verified=user_model.phone_verified,
        two_factor_enabled=user_model.two_factor_enabled,
        created_at=user_model.created_at.isoformat(),
        updated_at=user_model.updated_at.isoformat(),
        last_login=user_model.last_login.isoformat() if user_model.last_login else None
    )

# Basic endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Interview Preparation Platform API - Simple ORM Version",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "database": "Direct SQLAlchemy ORM with PostgreSQL"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "database": "Direct SQLAlchemy ORM",
        "orm": "enabled"
    }

@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "database": "Direct SQLAlchemy ORM configured",
        "environment": os.getenv("APP_ENV", "development"),
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# User endpoints
@app.get("/api/v1/users", response_model=List[UserResponse], tags=["Users"])
async def get_users(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all users"""
    try:
        stmt = select(UserModel).limit(limit).offset(offset)
        
        result = await session.execute(stmt)
        user_models = result.scalars().all()
        
        return [map_user_to_response(user_model) for user_model in user_models]
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@app.get("/api/v1/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get user by ID"""
    try:
        user_uuid = UUID(user_id)
        stmt = select(UserModel).where(UserModel.id == user_uuid)
        
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise HTTPException(status_code=404, detail="User not found")
        
        return map_user_to_response(user_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")

@app.post("/api/v1/users", response_model=UserResponse, tags=["Users"])
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new user"""
    try:
        # Create user model
        user_model = UserModel(
            email=user_data.email,
            password_hash=user_data.password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            auth_provider="email",
            provider_id=None,
            status="pending_verification",
            email_verified=False,
            phone_verified=False,
            two_factor_enabled=False
        )
        
        session.add(user_model)
        await session.flush()  # Get the ID
        
        # Create profile
        profile_model = UserProfile(
            user_id=user_model.id,
            bio=user_data.bio,
            phone=user_data.phone,
            city=user_data.city,
            country=user_data.country,
            years_of_experience=user_data.years_of_experience,
            domain=user_data.domain,
            linkedin_url=user_data.linkedin_url,
            github_url=user_data.github_url,
            portfolio_url=user_data.portfolio_url,
            resume_url=user_data.resume_url,
            skills=user_data.skills,
            preferences=user_data.preferences
        )
        session.add(profile_model)
        
        # Create stats
        stats_model = UserStats(
            user_id=user_model.id,
            total_assessments=0,
            completed_assessments=0,
            average_score=0.0,
            total_study_time=0,
            current_streak=0,
            longest_streak=0,
            skill_count=0,
            roadmap_count=0,
            last_active=None
        )
        session.add(stats_model)
        
        await session.commit()
        
        # Return the created user without relationships for now
        return map_user_to_response(user_model)
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating user: {e}")
        
        # Handle specific database errors
        if "duplicate key value violates unique constraint" in str(e) and "users_email_key" in str(e):
            raise HTTPException(status_code=409, detail="Email already exists")
        elif "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Duplicate entry")
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/api/v1/users/email/{email}", response_model=UserResponse, tags=["Users"])
async def get_user_by_email(
    email: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get user by email"""
    try:
        stmt = select(UserModel).where(UserModel.email == email)
        
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise HTTPException(status_code=404, detail="User not found")
        
        return map_user_to_response(user_model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")

# Skills endpoints
@app.get("/api/v1/skills", response_model=List[SkillResponse], tags=["Skills"])
async def get_skills(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all skills with optional filtering"""
    try:
        stmt = select(SkillModel)
        
        if category:
            stmt = stmt.where(SkillModel.category == category)
        if difficulty:
            stmt = stmt.where(SkillModel.difficulty == difficulty)
        
        stmt = stmt.limit(limit).offset(offset).order_by(SkillModel.name)
        
        result = await session.execute(stmt)
        skill_models = result.scalars().all()
        
        return [SkillResponse.model_validate(skill) for skill in skill_models]
    except Exception as e:
        logger.error(f"Error getting skills: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve skills")

@app.get("/api/v1/skills/{skill_id}", response_model=SkillResponse, tags=["Skills"])
async def get_skill(
    skill_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get skill by ID"""
    try:
        skill_uuid = UUID(skill_id)
        stmt = select(SkillModel).where(SkillModel.id == skill_uuid)
        
        result = await session.execute(stmt)
        skill_model = result.scalar_one_or_none()
        
        if not skill_model:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return SkillResponse.model_validate(skill_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting skill: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve skill")

@app.post("/api/v1/skills", response_model=SkillResponse, tags=["Skills"])
async def create_skill(
    skill_data: SkillCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new skill"""
    try:
        skill_model = SkillModel(
            name=skill_data.name,
            category=skill_data.category,
            description=skill_data.description,
            difficulty=skill_data.difficulty,
            tags=skill_data.tags,
            prerequisites=skill_data.prerequisites,
            related_skills=skill_data.related_skills,
            industry_relevance=skill_data.industry_relevance,
            average_salary_impact=skill_data.average_salary_impact,
            learning_path=skill_data.learning_path
        )
        
        session.add(skill_model)
        await session.commit()
        await session.refresh(skill_model)
        
        return SkillResponse.model_validate(skill_model)
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating skill: {e}")
        raise HTTPException(status_code=500, detail="Failed to create skill")

@app.put("/api/v1/skills/{skill_id}", response_model=SkillResponse, tags=["Skills"])
async def update_skill(
    skill_id: str,
    skill_data: SkillUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a skill"""
    try:
        skill_uuid = UUID(skill_id)
        stmt = select(SkillModel).where(SkillModel.id == skill_uuid)
        
        result = await session.execute(stmt)
        skill_model = result.scalar_one_or_none()
        
        if not skill_model:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        # Update fields
        update_data = skill_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(skill_model, field, value)
        
        await session.commit()
        await session.refresh(skill_model)
        
        return SkillResponse.model_validate(skill_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating skill: {e}")
        raise HTTPException(status_code=500, detail="Failed to update skill")

@app.delete("/api/v1/skills/{skill_id}", tags=["Skills"])
async def delete_skill(
    skill_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a skill"""
    try:
        skill_uuid = UUID(skill_id)
        stmt = select(SkillModel).where(SkillModel.id == skill_uuid)
        
        result = await session.execute(stmt)
        skill_model = result.scalar_one_or_none()
        
        if not skill_model:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        await session.delete(skill_model)
        await session.commit()
        
        return {"message": "Skill deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting skill: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete skill")

# Skill Topics endpoints
@app.get("/api/v1/skills/{skill_id}/topics", response_model=List[SkillTopicResponse], tags=["Skills"])
async def get_skill_topics(
    skill_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all topics for a skill"""
    try:
        skill_uuid = UUID(skill_id)
        stmt = select(SkillTopic).where(SkillTopic.skill_id == skill_uuid).order_by(SkillTopic.name)
        
        result = await session.execute(stmt)
        topic_models = result.scalars().all()
        
        return [SkillTopicResponse.model_validate(topic) for topic in topic_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")
    except Exception as e:
        logger.error(f"Error getting skill topics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve skill topics")

@app.post("/api/v1/skills/{skill_id}/topics", response_model=SkillTopicResponse, tags=["Skills"])
async def create_skill_topic(
    skill_id: str,
    topic_data: SkillTopicCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new topic for a skill"""
    try:
        skill_uuid = UUID(skill_id)
        topic_model = SkillTopic(
            skill_id=skill_uuid,
            name=topic_data.name,
            description=topic_data.description,
            difficulty=topic_data.difficulty,
            prerequisites=topic_data.prerequisites,
            learning_objectives=topic_data.learning_objectives,
            estimated_hours=topic_data.estimated_hours,
            resources=topic_data.resources
        )
        
        session.add(topic_model)
        await session.commit()
        await session.refresh(topic_model)
        
        return SkillTopicResponse.model_validate(topic_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating skill topic: {e}")
        raise HTTPException(status_code=500, detail="Failed to create skill topic")

# Skill Resources endpoints
@app.get("/api/v1/skills/{skill_id}/resources", response_model=List[SkillResourceResponse], tags=["Skills"])
async def get_skill_resources(
    skill_id: str,
    type_filter: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all resources for a skill"""
    try:
        skill_uuid = UUID(skill_id)
        stmt = select(SkillResource).where(SkillResource.skill_id == skill_uuid)
        
        if type_filter:
            stmt = stmt.where(SkillResource.type == type_filter)
        
        stmt = stmt.order_by(SkillResource.title)
        
        result = await session.execute(stmt)
        resource_models = result.scalars().all()
        
        return [SkillResourceResponse.model_validate(resource) for resource in resource_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")
    except Exception as e:
        logger.error(f"Error getting skill resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve skill resources")

@app.post("/api/v1/skills/{skill_id}/resources", response_model=SkillResourceResponse, tags=["Skills"])
async def create_skill_resource(
    skill_id: str,
    resource_data: SkillResourceCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new resource for a skill"""
    try:
        skill_uuid = UUID(skill_id)
        resource_model = SkillResource(
            skill_id=skill_uuid,
            type=resource_data.type,
            title=resource_data.title,
            url=resource_data.url,
            description=resource_data.description,
            difficulty=resource_data.difficulty,
            rating=resource_data.rating,
            duration_hours=resource_data.duration_hours,
            cost=resource_data.cost,
            provider=resource_data.provider
        )
        
        session.add(resource_model)
        await session.commit()
        await session.refresh(resource_model)
        
        return SkillResourceResponse.model_validate(resource_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid skill ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating skill resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to create skill resource")

# User Skill Progress endpoints
@app.get("/api/v1/users/{user_id}/skills/progress", response_model=List[UserSkillProgressResponse], tags=["Skills"])
async def get_user_skill_progress(
    user_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get skill progress for a user"""
    try:
        user_uuid = UUID(user_id)
        stmt = select(UserSkillProgress).where(UserSkillProgress.user_id == user_uuid)
        
        result = await session.execute(stmt)
        progress_models = result.scalars().all()
        
        return [UserSkillProgressResponse.model_validate(progress) for progress in progress_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        logger.error(f"Error getting user skill progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user skill progress")

@app.post("/api/v1/users/{user_id}/skills/{skill_id}/progress", response_model=UserSkillProgressResponse, tags=["Skills"])
async def create_user_skill_progress(
    user_id: str,
    skill_id: str,
    progress_data: UserSkillProgressCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create or update skill progress for a user"""
    try:
        user_uuid = UUID(user_id)
        skill_uuid = UUID(skill_id)
        
        # Check if progress already exists
        stmt = select(UserSkillProgress).where(
            and_(UserSkillProgress.user_id == user_uuid, UserSkillProgress.skill_id == skill_uuid)
        )
        result = await session.execute(stmt)
        existing_progress = result.scalar_one_or_none()
        
        if existing_progress:
            raise HTTPException(status_code=400, detail="Skill progress already exists. Use PUT to update.")
        
        progress_model = UserSkillProgress(
            user_id=user_uuid,
            skill_id=skill_uuid,
            current_level=progress_data.current_level,
            target_level=progress_data.target_level,
            demonstrated_level=progress_data.demonstrated_level,
            confidence_level=progress_data.confidence_level,
            progress_data=progress_data.progress_data
        )
        
        session.add(progress_model)
        await session.commit()
        await session.refresh(progress_model)
        
        return UserSkillProgressResponse.model_validate(progress_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating user skill progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user skill progress")

@app.put("/api/v1/users/{user_id}/skills/{skill_id}/progress", response_model=UserSkillProgressResponse, tags=["Skills"])
async def update_user_skill_progress(
    user_id: str,
    skill_id: str,
    progress_data: UserSkillProgressUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update skill progress for a user"""
    try:
        user_uuid = UUID(user_id)
        skill_uuid = UUID(skill_id)
        
        stmt = select(UserSkillProgress).where(
            and_(UserSkillProgress.user_id == user_uuid, UserSkillProgress.skill_id == skill_uuid)
        )
        result = await session.execute(stmt)
        progress_model = result.scalar_one_or_none()
        
        if not progress_model:
            raise HTTPException(status_code=404, detail="Skill progress not found")
        
        # Update fields
        update_data = progress_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(progress_model, field, value)
        
        await session.commit()
        await session.refresh(progress_model)
        
        return UserSkillProgressResponse.model_validate(progress_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating user skill progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user skill progress")

# Roadmap endpoints
@app.get("/api/v1/roadmaps", response_model=List[RoadmapResponse], tags=["Roadmaps"])
async def get_roadmaps(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all roadmaps with optional filtering"""
    try:
        stmt = select(RoadmapModel)
        
        if user_id:
            user_uuid = UUID(user_id)
            stmt = stmt.where(RoadmapModel.user_id == user_uuid)
        if status:
            stmt = stmt.where(RoadmapModel.status == status)
        if difficulty:
            stmt = stmt.where(RoadmapModel.difficulty == difficulty)
        
        stmt = stmt.limit(limit).offset(offset).order_by(RoadmapModel.created_at.desc())
        
        result = await session.execute(stmt)
        roadmap_models = result.scalars().all()
        
        return [RoadmapResponse.model_validate(roadmap) for roadmap in roadmap_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        logger.error(f"Error getting roadmaps: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve roadmaps")

@app.get("/api/v1/roadmaps/{roadmap_id}", response_model=RoadmapResponse, tags=["Roadmaps"])
async def get_roadmap(
    roadmap_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get roadmap by ID"""
    try:
        roadmap_uuid = UUID(roadmap_id)
        stmt = select(RoadmapModel).where(RoadmapModel.id == roadmap_uuid)
        
        result = await session.execute(stmt)
        roadmap_model = result.scalar_one_or_none()
        
        if not roadmap_model:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        
        return RoadmapResponse.model_validate(roadmap_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roadmap ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting roadmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve roadmap")

@app.post("/api/v1/roadmaps", response_model=RoadmapResponse, tags=["Roadmaps"])
async def create_roadmap(
    roadmap_data: RoadmapCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new roadmap"""
    try:
        user_uuid = UUID(roadmap_data.user_id)
        roadmap_model = RoadmapModel(
            user_id=user_uuid,
            title=roadmap_data.title,
            description=roadmap_data.description,
            target_role=roadmap_data.target_role,
            duration_weeks=roadmap_data.duration_weeks,
            difficulty=roadmap_data.difficulty,
            ai_generated=roadmap_data.ai_generated,
            generation_prompt=roadmap_data.generation_prompt
        )
        
        session.add(roadmap_model)
        await session.commit()
        await session.refresh(roadmap_model)
        
        return RoadmapResponse.model_validate(roadmap_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating roadmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to create roadmap")

@app.put("/api/v1/roadmaps/{roadmap_id}", response_model=RoadmapResponse, tags=["Roadmaps"])
async def update_roadmap(
    roadmap_id: str,
    roadmap_data: RoadmapUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a roadmap"""
    try:
        roadmap_uuid = UUID(roadmap_id)
        stmt = select(RoadmapModel).where(RoadmapModel.id == roadmap_uuid)
        
        result = await session.execute(stmt)
        roadmap_model = result.scalar_one_or_none()
        
        if not roadmap_model:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        
        # Update fields
        update_data = roadmap_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['started_at', 'completed_at'] and value:
                # Convert string to datetime if needed
                if isinstance(value, str):
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            setattr(roadmap_model, field, value)
        
        await session.commit()
        await session.refresh(roadmap_model)
        
        return RoadmapResponse.model_validate(roadmap_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roadmap ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating roadmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to update roadmap")

@app.delete("/api/v1/roadmaps/{roadmap_id}", tags=["Roadmaps"])
async def delete_roadmap(
    roadmap_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a roadmap"""
    try:
        roadmap_uuid = UUID(roadmap_id)
        stmt = select(RoadmapModel).where(RoadmapModel.id == roadmap_uuid)
        
        result = await session.execute(stmt)
        roadmap_model = result.scalar_one_or_none()
        
        if not roadmap_model:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        
        await session.delete(roadmap_model)
        await session.commit()
        
        return {"message": "Roadmap deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roadmap ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting roadmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete roadmap")

# Roadmap Topics endpoints
@app.get("/api/v1/roadmaps/{roadmap_id}/topics", response_model=List[RoadmapTopicResponse], tags=["Roadmaps"])
async def get_roadmap_topics(
    roadmap_id: str,
    status: Optional[str] = None,
    week_number: Optional[int] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all topics for a roadmap"""
    try:
        roadmap_uuid = UUID(roadmap_id)
        stmt = select(RoadmapTopic).where(RoadmapTopic.roadmap_id == roadmap_uuid)
        
        if status:
            stmt = stmt.where(RoadmapTopic.status == status)
        if week_number is not None:
            stmt = stmt.where(RoadmapTopic.week_number == week_number)
        
        stmt = stmt.order_by(RoadmapTopic.week_number, RoadmapTopic.created_at)
        
        result = await session.execute(stmt)
        topic_models = result.scalars().all()
        
        return [RoadmapTopicResponse.model_validate(topic) for topic in topic_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roadmap ID format")
    except Exception as e:
        logger.error(f"Error getting roadmap topics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve roadmap topics")

@app.post("/api/v1/roadmaps/{roadmap_id}/topics", response_model=RoadmapTopicResponse, tags=["Roadmaps"])
async def create_roadmap_topic(
    roadmap_id: str,
    topic_data: RoadmapTopicCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new topic for a roadmap"""
    try:
        roadmap_uuid = UUID(roadmap_id)
        topic_model = RoadmapTopic(
            roadmap_id=roadmap_uuid,
            title=topic_data.title,
            description=topic_data.description,
            difficulty=topic_data.difficulty,
            estimated_hours=topic_data.estimated_hours,
            prerequisites=topic_data.prerequisites,
            learning_objectives=topic_data.learning_objectives,
            content=topic_data.content,
            skills_covered=topic_data.skills_covered,
            assessment_criteria=topic_data.assessment_criteria,
            milestone=topic_data.milestone,
            week_number=topic_data.week_number
        )
        
        session.add(topic_model)
        await session.commit()
        await session.refresh(topic_model)
        
        return RoadmapTopicResponse.model_validate(topic_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roadmap ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating roadmap topic: {e}")
        raise HTTPException(status_code=500, detail="Failed to create roadmap topic")

@app.put("/api/v1/roadmap-topics/{topic_id}", response_model=RoadmapTopicResponse, tags=["Roadmaps"])
async def update_roadmap_topic(
    topic_id: str,
    topic_data: RoadmapTopicUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a roadmap topic"""
    try:
        topic_uuid = UUID(topic_id)
        stmt = select(RoadmapTopic).where(RoadmapTopic.id == topic_uuid)
        
        result = await session.execute(stmt)
        topic_model = result.scalar_one_or_none()
        
        if not topic_model:
            raise HTTPException(status_code=404, detail="Roadmap topic not found")
        
        # Update fields
        update_data = topic_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['started_at', 'completed_at'] and value:
                # Convert string to datetime if needed
                if isinstance(value, str):
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            setattr(topic_model, field, value)
        
        await session.commit()
        await session.refresh(topic_model)
        
        return RoadmapTopicResponse.model_validate(topic_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid topic ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating roadmap topic: {e}")
        raise HTTPException(status_code=500, detail="Failed to update roadmap topic")

# Learning Resources endpoints
@app.get("/api/v1/roadmap-topics/{topic_id}/resources", response_model=List[LearningResourceResponse], tags=["Roadmaps"])
async def get_learning_resources(
    topic_id: str,
    type_filter: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all learning resources for a roadmap topic"""
    try:
        topic_uuid = UUID(topic_id)
        stmt = select(LearningResource).where(LearningResource.roadmap_topic_id == topic_uuid)
        
        if type_filter:
            stmt = stmt.where(LearningResource.type == type_filter)
        
        stmt = stmt.order_by(LearningResource.is_required.desc(), LearningResource.title)
        
        result = await session.execute(stmt)
        resource_models = result.scalars().all()
        
        return [LearningResourceResponse.model_validate(resource) for resource in resource_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid topic ID format")
    except Exception as e:
        logger.error(f"Error getting learning resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve learning resources")

@app.post("/api/v1/roadmap-topics/{topic_id}/resources", response_model=LearningResourceResponse, tags=["Roadmaps"])
async def create_learning_resource(
    topic_id: str,
    resource_data: LearningResourceCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new learning resource for a roadmap topic"""
    try:
        topic_uuid = UUID(topic_id)
        resource_model = LearningResource(
            roadmap_topic_id=topic_uuid,
            type=resource_data.type,
            title=resource_data.title,
            url=resource_data.url,
            description=resource_data.description,
            difficulty=resource_data.difficulty,
            duration_hours=resource_data.duration_hours,
            cost=resource_data.cost,
            provider=resource_data.provider,
            rating=resource_data.rating,
            is_required=resource_data.is_required
        )
        
        session.add(resource_model)
        await session.commit()
        await session.refresh(resource_model)
        
        return LearningResourceResponse.model_validate(resource_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid topic ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating learning resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to create learning resource")

# Practice Exercises endpoints
@app.get("/api/v1/roadmap-topics/{topic_id}/exercises", response_model=List[PracticeExerciseResponse], tags=["Roadmaps"])
async def get_practice_exercises(
    topic_id: str,
    type_filter: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all practice exercises for a roadmap topic"""
    try:
        topic_uuid = UUID(topic_id)
        stmt = select(PracticeExercise).where(PracticeExercise.roadmap_topic_id == topic_uuid)
        
        if type_filter:
            stmt = stmt.where(PracticeExercise.type == type_filter)
        
        stmt = stmt.order_by(PracticeExercise.created_at)
        
        result = await session.execute(stmt)
        exercise_models = result.scalars().all()
        
        return [PracticeExerciseResponse.model_validate(exercise) for exercise in exercise_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid topic ID format")
    except Exception as e:
        logger.error(f"Error getting practice exercises: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve practice exercises")

@app.post("/api/v1/roadmap-topics/{topic_id}/exercises", response_model=PracticeExerciseResponse, tags=["Roadmaps"])
async def create_practice_exercise(
    topic_id: str,
    exercise_data: PracticeExerciseCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new practice exercise for a roadmap topic"""
    try:
        topic_uuid = UUID(topic_id)
        exercise_model = PracticeExercise(
            roadmap_topic_id=topic_uuid,
            type=exercise_data.type,
            title=exercise_data.title,
            description=exercise_data.description,
            estimated_time=exercise_data.estimated_time,
            difficulty=exercise_data.difficulty,
            instructions=exercise_data.instructions,
            resources=exercise_data.resources,
            success_criteria=exercise_data.success_criteria
        )
        
        session.add(exercise_model)
        await session.commit()
        await session.refresh(exercise_model)
        
        return PracticeExerciseResponse.model_validate(exercise_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid topic ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating practice exercise: {e}")
        raise HTTPException(status_code=500, detail="Failed to create practice exercise")

# Roadmap Milestones endpoints
@app.get("/api/v1/roadmaps/{roadmap_id}/milestones", response_model=List[RoadmapMilestoneResponse], tags=["Roadmaps"])
async def get_roadmap_milestones(
    roadmap_id: str,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all milestones for a roadmap"""
    try:
        roadmap_uuid = UUID(roadmap_id)
        stmt = select(RoadmapMilestone).where(RoadmapMilestone.roadmap_id == roadmap_uuid)
        
        if status:
            stmt = stmt.where(RoadmapMilestone.status == status)
        
        stmt = stmt.order_by(RoadmapMilestone.week_number)
        
        result = await session.execute(stmt)
        milestone_models = result.scalars().all()
        
        return [RoadmapMilestoneResponse.model_validate(milestone) for milestone in milestone_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roadmap ID format")
    except Exception as e:
        logger.error(f"Error getting roadmap milestones: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve roadmap milestones")

@app.post("/api/v1/roadmaps/{roadmap_id}/milestones", response_model=RoadmapMilestoneResponse, tags=["Roadmaps"])
async def create_roadmap_milestone(
    roadmap_id: str,
    milestone_data: RoadmapMilestoneCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new milestone for a roadmap"""
    try:
        roadmap_uuid = UUID(roadmap_id)
        milestone_model = RoadmapMilestone(
            roadmap_id=roadmap_uuid,
            title=milestone_data.title,
            description=milestone_data.description,
            week_number=milestone_data.week_number,
            skills_to_master=milestone_data.skills_to_master,
            assessment_type=milestone_data.assessment_type,
            target_date=datetime.fromisoformat(milestone_data.target_date.replace('Z', '+00:00')) if milestone_data.target_date else None
        )
        
        session.add(milestone_model)
        await session.commit()
        await session.refresh(milestone_model)
        
        return RoadmapMilestoneResponse.model_validate(milestone_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid roadmap ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating roadmap milestone: {e}")
        raise HTTPException(status_code=500, detail="Failed to create roadmap milestone")

# Assessment endpoints
@app.get("/api/v1/assessments", response_model=List[AssessmentResponse], tags=["Assessments"])
async def get_assessments(
    user_id: Optional[str] = None,
    roadmap_id: Optional[str] = None,
    assessment_type: Optional[str] = None,
    status: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all assessments with optional filtering"""
    try:
        stmt = select(AssessmentModel)
        
        if user_id:
            user_uuid = UUID(user_id)
            stmt = stmt.where(AssessmentModel.user_id == user_uuid)
        if roadmap_id:
            roadmap_uuid = UUID(roadmap_id)
            stmt = stmt.where(AssessmentModel.roadmap_id == roadmap_uuid)
        if assessment_type:
            stmt = stmt.where(AssessmentModel.assessment_type == assessment_type)
        if status:
            stmt = stmt.where(AssessmentModel.status == status)
        if difficulty:
            stmt = stmt.where(AssessmentModel.difficulty == difficulty)
        
        stmt = stmt.limit(limit).offset(offset).order_by(AssessmentModel.created_at.desc())
        
        result = await session.execute(stmt)
        assessment_models = result.scalars().all()
        
        return [AssessmentResponse.model_validate(assessment) for assessment in assessment_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        logger.error(f"Error getting assessments: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessments")

@app.get("/api/v1/assessments/{assessment_id}", response_model=AssessmentResponse, tags=["Assessments"])
async def get_assessment(
    assessment_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get assessment by ID"""
    try:
        assessment_uuid = UUID(assessment_id)
        stmt = select(AssessmentModel).where(AssessmentModel.id == assessment_uuid)
        
        result = await session.execute(stmt)
        assessment_model = result.scalar_one_or_none()
        
        if not assessment_model:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        return AssessmentResponse.model_validate(assessment_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment")

@app.post("/api/v1/assessments", response_model=AssessmentResponse, tags=["Assessments"])
async def create_assessment(
    assessment_data: AssessmentCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new assessment"""
    try:
        user_uuid = UUID(assessment_data.user_id) if assessment_data.user_id else None
        roadmap_uuid = UUID(assessment_data.roadmap_id) if assessment_data.roadmap_id else None
        
        assessment_model = AssessmentModel(
            title=assessment_data.title,
            assessment_type=assessment_data.assessment_type,
            skill_ids=assessment_data.skill_ids,
            difficulty=assessment_data.difficulty,
            duration_minutes=assessment_data.duration_minutes,
            user_id=user_uuid,
            roadmap_id=roadmap_uuid,
            adaptive_difficulty=assessment_data.adaptive_difficulty,
            allow_hints=assessment_data.allow_hints,
            allow_review=assessment_data.allow_review,
            randomize_questions=assessment_data.randomize_questions,
            passing_score=assessment_data.passing_score,
            max_attempts=assessment_data.max_attempts,
            time_limit_per_question=assessment_data.time_limit_per_question
        )
        
        session.add(assessment_model)
        await session.commit()
        await session.refresh(assessment_model)
        
        return AssessmentResponse.model_validate(assessment_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create assessment")

@app.put("/api/v1/assessments/{assessment_id}", response_model=AssessmentResponse, tags=["Assessments"])
async def update_assessment(
    assessment_id: str,
    assessment_data: AssessmentUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update an assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        stmt = select(AssessmentModel).where(AssessmentModel.id == assessment_uuid)
        
        result = await session.execute(stmt)
        assessment_model = result.scalar_one_or_none()
        
        if not assessment_model:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Update fields
        update_data = assessment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['started_at', 'completed_at', 'expires_at', 'last_activity_at'] and value:
                # Convert string to datetime if needed
                if isinstance(value, str):
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            setattr(assessment_model, field, value)
        
        await session.commit()
        await session.refresh(assessment_model)
        
        return AssessmentResponse.model_validate(assessment_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to update assessment")

@app.delete("/api/v1/assessments/{assessment_id}", tags=["Assessments"])
async def delete_assessment(
    assessment_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete an assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        stmt = select(AssessmentModel).where(AssessmentModel.id == assessment_uuid)
        
        result = await session.execute(stmt)
        assessment_model = result.scalar_one_or_none()
        
        if not assessment_model:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        await session.delete(assessment_model)
        await session.commit()
        
        return {"message": "Assessment deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete assessment")

# Assessment Questions endpoints
@app.get("/api/v1/assessments/{assessment_id}/questions", response_model=List[AssessmentQuestionResponse], tags=["Assessments"])
async def get_assessment_questions(
    assessment_id: str,
    difficulty: Optional[str] = None,
    type_filter: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all questions for an assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        stmt = select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == assessment_uuid)
        
        if difficulty:
            stmt = stmt.where(AssessmentQuestion.difficulty == difficulty)
        if type_filter:
            stmt = stmt.where(AssessmentQuestion.type == type_filter)
        
        stmt = stmt.order_by(AssessmentQuestion.created_at)
        
        result = await session.execute(stmt)
        question_models = result.scalars().all()
        
        return [AssessmentQuestionResponse.model_validate(question) for question in question_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except Exception as e:
        logger.error(f"Error getting assessment questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment questions")

@app.post("/api/v1/assessments/{assessment_id}/questions", response_model=AssessmentQuestionResponse, tags=["Assessments"])
async def create_assessment_question(
    assessment_id: str,
    question_data: AssessmentQuestionCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new question for an assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        question_model = AssessmentQuestion(
            assessment_id=assessment_uuid,
            type=question_data.type,
            title=question_data.title,
            description=question_data.description,
            difficulty=question_data.difficulty,
            estimated_time=question_data.estimated_time,
            points=question_data.points,
            prerequisites=question_data.prerequisites,
            learning_objectives=question_data.learning_objectives,
            question=question_data.question,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            expected_answer_format=question_data.expected_answer_format,
            code_template=question_data.code_template,
            constraints=question_data.constraints,
            evaluation_criteria=question_data.evaluation_criteria,
            hints=question_data.hints,
            explanation=question_data.explanation,
            tags=question_data.tags,
            dependencies=question_data.dependencies
        )
        
        session.add(question_model)
        await session.commit()
        await session.refresh(question_model)
        
        return AssessmentQuestionResponse.model_validate(question_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating assessment question: {e}")
        raise HTTPException(status_code=500, detail="Failed to create assessment question")

# Assessment Responses endpoints
@app.get("/api/v1/assessments/{assessment_id}/responses", response_model=List[AssessmentResponseResponse], tags=["Assessments"])
async def get_assessment_responses(
    assessment_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all responses for an assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        stmt = select(AssessmentResponse).where(AssessmentResponse.assessment_id == assessment_uuid)
        stmt = stmt.order_by(AssessmentResponse.submitted_at)
        
        result = await session.execute(stmt)
        response_models = result.scalars().all()
        
        return [AssessmentResponseResponse.model_validate(response) for response in response_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except Exception as e:
        logger.error(f"Error getting assessment responses: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment responses")

@app.post("/api/v1/assessments/{assessment_id}/responses", response_model=AssessmentResponseResponse, tags=["Assessments"])
async def create_assessment_response(
    assessment_id: str,
    response_data: AssessmentResponseCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new response for an assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        question_uuid = UUID(response_data.question_id)
        
        # Check if response already exists
        stmt = select(AssessmentResponse).where(
            and_(AssessmentResponse.assessment_id == assessment_uuid, 
                 AssessmentResponse.question_id == question_uuid)
        )
        result = await session.execute(stmt)
        existing_response = result.scalar_one_or_none()
        
        if existing_response:
            raise HTTPException(status_code=400, detail="Response already exists for this question")
        
        response_model = AssessmentResponse(
            assessment_id=assessment_uuid,
            question_id=question_uuid,
            answer=response_data.answer,
            time_taken=response_data.time_taken,
            hints_used=response_data.hints_used,
            attempts=response_data.attempts
        )
        
        session.add(response_model)
        await session.commit()
        await session.refresh(response_model)
        
        return AssessmentResponseResponse.model_validate(response_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating assessment response: {e}")
        raise HTTPException(status_code=500, detail="Failed to create assessment response")

# Question Evaluations endpoints
@app.get("/api/v1/assessments/{assessment_id}/evaluations", response_model=List[QuestionEvaluationResponse], tags=["Assessments"])
async def get_question_evaluations(
    assessment_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all evaluations for an assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        stmt = select(QuestionEvaluation).where(QuestionEvaluation.assessment_id == assessment_uuid)
        stmt = stmt.order_by(QuestionEvaluation.evaluated_at)
        
        result = await session.execute(stmt)
        evaluation_models = result.scalars().all()
        
        return [QuestionEvaluationResponse.model_validate(evaluation) for evaluation in evaluation_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except Exception as e:
        logger.error(f"Error getting question evaluations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve question evaluations")

@app.post("/api/v1/assessments/{assessment_id}/evaluations", response_model=QuestionEvaluationResponse, tags=["Assessments"])
async def create_question_evaluation(
    assessment_id: str,
    evaluation_data: QuestionEvaluationCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new evaluation for a question"""
    try:
        assessment_uuid = UUID(assessment_id)
        question_uuid = UUID(evaluation_data.question_id)
        
        # Check if evaluation already exists
        stmt = select(QuestionEvaluation).where(
            and_(QuestionEvaluation.assessment_id == assessment_uuid, 
                 QuestionEvaluation.question_id == question_uuid)
        )
        result = await session.execute(stmt)
        existing_evaluation = result.scalar_one_or_none()
        
        if existing_evaluation:
            raise HTTPException(status_code=400, detail="Evaluation already exists for this question")
        
        evaluation_model = QuestionEvaluation(
            assessment_id=assessment_uuid,
            question_id=question_uuid,
            score=evaluation_data.score,
            correctness=evaluation_data.correctness,
            efficiency=evaluation_data.efficiency,
            style=evaluation_data.style,
            completeness=evaluation_data.completeness,
            is_correct=evaluation_data.is_correct,
            feedback=evaluation_data.feedback,
            detailed_analysis=evaluation_data.detailed_analysis,
            improvement_areas=evaluation_data.improvement_areas,
            next_steps=evaluation_data.next_steps,
            encouragement=evaluation_data.encouragement
        )
        
        session.add(evaluation_model)
        await session.commit()
        await session.refresh(evaluation_model)
        
        return QuestionEvaluationResponse.model_validate(evaluation_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating question evaluation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create question evaluation")

# Skill Assessments endpoints
@app.get("/api/v1/assessments/{assessment_id}/skill-assessments", response_model=List[SkillAssessmentResponse], tags=["Assessments"])
async def get_skill_assessments(
    assessment_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all skill assessments for an assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        stmt = select(SkillAssessment).where(SkillAssessment.assessment_id == assessment_uuid)
        stmt = stmt.order_by(SkillAssessment.skill)
        
        result = await session.execute(stmt)
        skill_assessment_models = result.scalars().all()
        
        return [SkillAssessmentResponse.model_validate(skill_assessment) for skill_assessment in skill_assessment_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except Exception as e:
        logger.error(f"Error getting skill assessments: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve skill assessments")

@app.post("/api/v1/assessments/{assessment_id}/skill-assessments", response_model=SkillAssessmentResponse, tags=["Assessments"])
async def create_skill_assessment(
    assessment_id: str,
    skill_assessment_data: SkillAssessmentCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new skill assessment"""
    try:
        assessment_uuid = UUID(assessment_id)
        
        # Check if skill assessment already exists
        stmt = select(SkillAssessment).where(
            and_(SkillAssessment.assessment_id == assessment_uuid, 
                 SkillAssessment.skill == skill_assessment_data.skill)
        )
        result = await session.execute(stmt)
        existing_skill_assessment = result.scalar_one_or_none()
        
        if existing_skill_assessment:
            raise HTTPException(status_code=400, detail="Skill assessment already exists for this skill")
        
        skill_assessment_model = SkillAssessment(
            assessment_id=assessment_uuid,
            skill=skill_assessment_data.skill,
            current_level=skill_assessment_data.current_level,
            target_level=skill_assessment_data.target_level,
            demonstrated_level=skill_assessment_data.demonstrated_level,
            confidence_level=skill_assessment_data.confidence_level,
            recommendations=skill_assessment_data.recommendations
        )
        
        session.add(skill_assessment_model)
        await session.commit()
        await session.refresh(skill_assessment_model)
        
        return SkillAssessmentResponse.model_validate(skill_assessment_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid assessment ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating skill assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create skill assessment")

# Analytics endpoints
@app.get("/api/v1/analytics", response_model=List[AnalyticsResponse], tags=["Analytics"])
async def get_analytics(
    user_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all analytics with optional filtering"""
    try:
        stmt = select(AnalyticsModel)
        
        if user_id:
            user_uuid = UUID(user_id)
            stmt = stmt.where(AnalyticsModel.user_id == user_uuid)
        
        stmt = stmt.limit(limit).offset(offset).order_by(AnalyticsModel.updated_at.desc())
        
        result = await session.execute(stmt)
        analytics_models = result.scalars().all()
        
        return [AnalyticsResponse.model_validate(analytics) for analytics in analytics_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@app.get("/api/v1/analytics/{analytics_id}", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_analytics_by_id(
    analytics_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get analytics by ID"""
    try:
        analytics_uuid = UUID(analytics_id)
        stmt = select(AnalyticsModel).where(AnalyticsModel.id == analytics_uuid)
        
        result = await session.execute(stmt)
        analytics_model = result.scalar_one_or_none()
        
        if not analytics_model:
            raise HTTPException(status_code=404, detail="Analytics not found")
        
        return AnalyticsResponse.model_validate(analytics_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analytics ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@app.get("/api/v1/users/{user_id}/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_user_analytics(
    user_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get analytics for a specific user"""
    try:
        user_uuid = UUID(user_id)
        stmt = select(AnalyticsModel).where(AnalyticsModel.user_id == user_uuid)
        
        result = await session.execute(stmt)
        analytics_model = result.scalar_one_or_none()
        
        if not analytics_model:
            raise HTTPException(status_code=404, detail="User analytics not found")
        
        return AnalyticsResponse.model_validate(analytics_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user analytics")

@app.post("/api/v1/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
async def create_analytics(
    analytics_data: AnalyticsCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create new analytics for a user"""
    try:
        user_uuid = UUID(analytics_data.user_id)
        
        # Check if analytics already exists for this user
        stmt = select(AnalyticsModel).where(AnalyticsModel.user_id == user_uuid)
        result = await session.execute(stmt)
        existing_analytics = result.scalar_one_or_none()
        
        if existing_analytics:
            raise HTTPException(status_code=400, detail="Analytics already exists for this user")
        
        analytics_model = AnalyticsModel(
            user_id=user_uuid,
            skill_progress=analytics_data.skill_progress,
            readiness_trends=analytics_data.readiness_trends,
            assessment_history=analytics_data.assessment_history,
            topic_coverage=analytics_data.topic_coverage,
            study_time=analytics_data.study_time,
            leaderboards=analytics_data.leaderboards,
            summary=analytics_data.summary
        )
        
        session.add(analytics_model)
        await session.commit()
        await session.refresh(analytics_model)
        
        return AnalyticsResponse.model_validate(analytics_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to create analytics")

@app.put("/api/v1/analytics/{analytics_id}", response_model=AnalyticsResponse, tags=["Analytics"])
async def update_analytics(
    analytics_id: str,
    analytics_data: AnalyticsUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update analytics"""
    try:
        analytics_uuid = UUID(analytics_id)
        stmt = select(AnalyticsModel).where(AnalyticsModel.id == analytics_uuid)
        
        result = await session.execute(stmt)
        analytics_model = result.scalar_one_or_none()
        
        if not analytics_model:
            raise HTTPException(status_code=404, detail="Analytics not found")
        
        # Update fields
        update_data = analytics_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(analytics_model, field, value)
        
        await session.commit()
        await session.refresh(analytics_model)
        
        return AnalyticsResponse.model_validate(analytics_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analytics ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to update analytics")

@app.put("/api/v1/users/{user_id}/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
async def update_user_analytics(
    user_id: str,
    analytics_data: AnalyticsUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update analytics for a user"""
    try:
        user_uuid = UUID(user_id)
        stmt = select(AnalyticsModel).where(AnalyticsModel.user_id == user_uuid)
        
        result = await session.execute(stmt)
        analytics_model = result.scalar_one_or_none()
        
        if not analytics_model:
            raise HTTPException(status_code=404, detail="User analytics not found")
        
        # Update fields
        update_data = analytics_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(analytics_model, field, value)
        
        await session.commit()
        await session.refresh(analytics_model)
        
        return AnalyticsResponse.model_validate(analytics_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user analytics")

# Analytics Data Points endpoints
@app.get("/api/v1/analytics-data-points", response_model=List[AnalyticsDataPointResponse], tags=["Analytics"])
async def get_analytics_data_points(
    user_id: Optional[str] = None,
    metric_type: Optional[str] = None,
    metric_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all analytics data points with optional filtering"""
    try:
        stmt = select(AnalyticsDataPoint)
        
        if user_id:
            user_uuid = UUID(user_id)
            stmt = stmt.where(AnalyticsDataPoint.user_id == user_uuid)
        if metric_type:
            stmt = stmt.where(AnalyticsDataPoint.metric_type == metric_type)
        if metric_name:
            stmt = stmt.where(AnalyticsDataPoint.metric_name == metric_name)
        
        stmt = stmt.limit(limit).offset(offset).order_by(AnalyticsDataPoint.timestamp.desc())
        
        result = await session.execute(stmt)
        data_point_models = result.scalars().all()
        
        return [AnalyticsDataPointResponse.model_validate(data_point) for data_point in data_point_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        logger.error(f"Error getting analytics data points: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics data points")

@app.get("/api/v1/users/{user_id}/analytics-data-points", response_model=List[AnalyticsDataPointResponse], tags=["Analytics"])
async def get_user_analytics_data_points(
    user_id: str,
    metric_type: Optional[str] = None,
    metric_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get analytics data points for a specific user"""
    try:
        user_uuid = UUID(user_id)
        stmt = select(AnalyticsDataPoint).where(AnalyticsDataPoint.user_id == user_uuid)
        
        if metric_type:
            stmt = stmt.where(AnalyticsDataPoint.metric_type == metric_type)
        if metric_name:
            stmt = stmt.where(AnalyticsDataPoint.metric_name == metric_name)
        
        stmt = stmt.limit(limit).offset(offset).order_by(AnalyticsDataPoint.timestamp.desc())
        
        result = await session.execute(stmt)
        data_point_models = result.scalars().all()
        
        return [AnalyticsDataPointResponse.model_validate(data_point) for data_point in data_point_models]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        logger.error(f"Error getting user analytics data points: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user analytics data points")

@app.post("/api/v1/analytics-data-points", response_model=AnalyticsDataPointResponse, tags=["Analytics"])
async def create_analytics_data_point(
    data_point_data: AnalyticsDataPointCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new analytics data point"""
    try:
        user_uuid = UUID(data_point_data.user_id)
        data_point_model = AnalyticsDataPoint(
            user_id=user_uuid,
            metric_type=data_point_data.metric_type,
            metric_name=data_point_data.metric_name,
            value=data_point_data.value,
            metadata_json=data_point_data.metadata
        )
        
        session.add(data_point_model)
        await session.commit()
        await session.refresh(data_point_model)
        
        return AnalyticsDataPointResponse.model_validate(data_point_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating analytics data point: {e}")
        raise HTTPException(status_code=500, detail="Failed to create analytics data point")

# Leaderboards endpoints
@app.get("/api/v1/leaderboards", response_model=List[LeaderboardResponse], tags=["Analytics"])
async def get_leaderboards(
    leaderboard_type: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all leaderboards with optional filtering"""
    try:
        stmt = select(Leaderboard)
        
        if leaderboard_type:
            stmt = stmt.where(Leaderboard.leaderboard_type == leaderboard_type)
        if category:
            stmt = stmt.where(Leaderboard.category == category)
        
        stmt = stmt.limit(limit).offset(offset).order_by(Leaderboard.last_updated.desc())
        
        result = await session.execute(stmt)
        leaderboard_models = result.scalars().all()
        
        return [LeaderboardResponse.model_validate(leaderboard) for leaderboard in leaderboard_models]
    except Exception as e:
        logger.error(f"Error getting leaderboards: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve leaderboards")

@app.get("/api/v1/leaderboards/{leaderboard_id}", response_model=LeaderboardResponse, tags=["Analytics"])
async def get_leaderboard(
    leaderboard_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Get leaderboard by ID"""
    try:
        leaderboard_uuid = UUID(leaderboard_id)
        stmt = select(Leaderboard).where(Leaderboard.id == leaderboard_uuid)
        
        result = await session.execute(stmt)
        leaderboard_model = result.scalar_one_or_none()
        
        if not leaderboard_model:
            raise HTTPException(status_code=404, detail="Leaderboard not found")
        
        return LeaderboardResponse.model_validate(leaderboard_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid leaderboard ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve leaderboard")

@app.post("/api/v1/leaderboards", response_model=LeaderboardResponse, tags=["Analytics"])
async def create_leaderboard(
    leaderboard_data: LeaderboardCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new leaderboard"""
    try:
        leaderboard_model = Leaderboard(
            leaderboard_type=leaderboard_data.leaderboard_type,
            category=leaderboard_data.category,
            entries=leaderboard_data.entries,
            total_participants=leaderboard_data.total_participants
        )
        
        session.add(leaderboard_model)
        await session.commit()
        await session.refresh(leaderboard_model)
        
        return LeaderboardResponse.model_validate(leaderboard_model)
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to create leaderboard")

@app.put("/api/v1/leaderboards/{leaderboard_id}", response_model=LeaderboardResponse, tags=["Analytics"])
async def update_leaderboard(
    leaderboard_id: str,
    leaderboard_data: LeaderboardUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a leaderboard"""
    try:
        leaderboard_uuid = UUID(leaderboard_id)
        stmt = select(Leaderboard).where(Leaderboard.id == leaderboard_uuid)
        
        result = await session.execute(stmt)
        leaderboard_model = result.scalar_one_or_none()
        
        if not leaderboard_model:
            raise HTTPException(status_code=404, detail="Leaderboard not found")
        
        # Update fields
        update_data = leaderboard_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(leaderboard_model, field, value)
        
        await session.commit()
        await session.refresh(leaderboard_model)
        
        return LeaderboardResponse.model_validate(leaderboard_model)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid leaderboard ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error updating leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to update leaderboard")

@app.delete("/api/v1/leaderboards/{leaderboard_id}", tags=["Analytics"])
async def delete_leaderboard(
    leaderboard_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a leaderboard"""
    try:
        leaderboard_uuid = UUID(leaderboard_id)
        stmt = select(Leaderboard).where(Leaderboard.id == leaderboard_uuid)
        
        result = await session.execute(stmt)
        leaderboard_model = result.scalar_one_or_none()
        
        if not leaderboard_model:
            raise HTTPException(status_code=404, detail="Leaderboard not found")
        
        await session.delete(leaderboard_model)
        await session.commit()
        
        return {"message": "Leaderboard deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid leaderboard ID format")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete leaderboard")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Simple ORM application on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
