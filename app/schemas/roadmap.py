from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class RoadmapBase(BaseModel):
    title: str
    description: Optional[str] = None
    role_id: Optional[uuid.UUID] = None

class RoadmapCreate(RoadmapBase):
    target_role_name: Optional[str] = None
    job_description_id: Optional[uuid.UUID] = None
    custom_requirements: Optional[Dict[str, Any]] = None

class RoadmapUpdate(RoadmapBase):
    title: Optional[str] = None

class RoadmapResponse(RoadmapBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_topics: int
    covered_topics: int
    progress_percentage: float
    generated_by_ai: bool
    ai_model_version: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_hours: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    skills_covered: Optional[List[str]] = None

class TopicCreate(TopicBase):
    pass

class TopicUpdate(TopicBase):
    title: Optional[str] = None

class TopicResponse(TopicBase):
    id: uuid.UUID
    roadmap_id: uuid.UUID
    order_index: int
    is_covered: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoadmapWithTopicsResponse(RoadmapResponse):
    topics: List[TopicResponse] = []

class RoadmapGenerationRequest(BaseModel):
    target_role: str
    current_skills: List[Dict[str, Any]]
    experience_level: str
    learning_preferences: Optional[Dict[str, Any]] = None
    time_commitment: Optional[str] = None  # hours per week
    focus_areas: Optional[List[str]] = None
