"""
Skill Domain Entity
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from domain.value_objects.skill_level import SkillLevel


class SkillCategory(str, Enum):
    PROGRAMMING = "programming"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD = "cloud"
    DEVOPS = "devops"
    MOBILE = "mobile"
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULL_STACK = "full_stack"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    AI = "ai"
    BLOCKCHAIN = "blockchain"
    SECURITY = "security"
    TESTING = "testing"
    DESIGN = "design"
    PROJECT_MANAGEMENT = "project_management"
    SOFT_SKILLS = "soft_skills"
    DOMAIN_SPECIFIC = "domain_specific"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class SkillTopic:
    """Skill topic or sub-skill"""
    id: UUID
    name: str
    description: str
    difficulty: DifficultyLevel
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    estimated_hours: int = 0
    resources: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()


@dataclass
class SkillAssessment:
    """Skill assessment criteria"""
    question_types: List[str] = field(default_factory=list)
    difficulty_range: str = "beginner-expert"
    time_limit_minutes: int = 60
    passing_score: int = 70
    adaptive_difficulty: bool = True


@dataclass
class SkillResource:
    """Learning resource for skill"""
    type: str  # course, book, tutorial, documentation, tool
    title: str
    url: Optional[str] = None
    description: str = ""
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    rating: Optional[float] = None
    duration_hours: Optional[int] = None
    cost: Optional[str] = None
    provider: Optional[str] = None


class Skill:
    """Skill domain entity"""
    
    def __init__(
        self,
        name: str,
        category: SkillCategory,
        description: str = "",
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
        topics: Optional[List[SkillTopic]] = None,
        assessment: Optional[SkillAssessment] = None,
        resources: Optional[List[SkillResource]] = None,
        tags: Optional[List[str]] = None,
        prerequisites: Optional[List[str]] = None,
        related_skills: Optional[List[str]] = None,
        industry_relevance: Optional[Dict[str, float]] = None,
        average_salary_impact: Optional[float] = None,
        learning_path: Optional[List[str]] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.name = name.strip()
        self.category = category
        self.description = description.strip()
        self.difficulty = difficulty
        self.topics = topics or []
        self.assessment = assessment or SkillAssessment()
        self.resources = resources or []
        self.tags = tags or []
        self.prerequisites = prerequisites or []
        self.related_skills = related_skills or []
        self.industry_relevance = industry_relevance or {}
        self.average_salary_impact = average_salary_impact
        self.learning_path = learning_path or []
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def add_topic(self, topic: SkillTopic) -> None:
        """Add a topic to the skill"""
        self.topics.append(topic)
        self.updated_at = datetime.utcnow()
    
    def remove_topic(self, topic_id: UUID) -> None:
        """Remove a topic from the skill"""
        self.topics = [t for t in self.topics if t.id != topic_id]
        self.updated_at = datetime.utcnow()
    
    def add_resource(self, resource: SkillResource) -> None:
        """Add a learning resource"""
        self.resources.append(resource)
        self.updated_at = datetime.utcnow()
    
    def remove_resource(self, resource_index: int) -> None:
        """Remove a learning resource by index"""
        if 0 <= resource_index < len(self.resources):
            self.resources.pop(resource_index)
            self.updated_at = datetime.utcnow()
    
    def update_assessment(self, assessment: SkillAssessment) -> None:
        """Update skill assessment criteria"""
        self.assessment = assessment
        self.updated_at = datetime.utcnow()
    
    def add_prerequisite(self, skill_name: str) -> None:
        """Add a prerequisite skill"""
        if skill_name not in self.prerequisites:
            self.prerequisites.append(skill_name)
            self.updated_at = datetime.utcnow()
    
    def remove_prerequisite(self, skill_name: str) -> None:
        """Remove a prerequisite skill"""
        if skill_name in self.prerequisites:
            self.prerequisites.remove(skill_name)
            self.updated_at = datetime.utcnow()
    
    def add_related_skill(self, skill_name: str) -> None:
        """Add a related skill"""
        if skill_name not in self.related_skills:
            self.related_skills.append(skill_name)
            self.updated_at = datetime.utcnow()
    
    def remove_related_skill(self, skill_name: str) -> None:
        """Remove a related skill"""
        if skill_name in self.related_skills:
            self.related_skills.remove(skill_name)
            self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the skill"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the skill"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def update_industry_relevance(self, industry: str, relevance_score: float) -> None:
        """Update industry relevance score"""
        if not 0 <= relevance_score <= 1:
            raise ValueError("Relevance score must be between 0 and 1")
        self.industry_relevance[industry] = relevance_score
        self.updated_at = datetime.utcnow()
    
    def get_total_learning_hours(self) -> int:
        """Get total estimated learning hours"""
        topic_hours = sum(topic.estimated_hours for topic in self.topics)
        resource_hours = sum(r.duration_hours or 0 for r in self.resources)
        return topic_hours + resource_hours
    
    def get_difficulty_distribution(self) -> Dict[str, int]:
        """Get distribution of topics by difficulty"""
        distribution = {level.value: 0 for level in DifficultyLevel}
        for topic in self.topics:
            distribution[topic.difficulty.value] += 1
        return distribution
    
    def get_resource_types(self) -> Dict[str, int]:
        """Get distribution of resources by type"""
        resource_types = {}
        for resource in self.resources:
            resource_types[resource.type] = resource_types.get(resource.type, 0) + 1
        return resource_types
    
    def is_prerequisite_satisfied(self, user_skills: List[str]) -> bool:
        """Check if all prerequisites are satisfied"""
        return all(prereq in user_skills for prereq in self.prerequisites)
    def get_missing_prerequisites(self, user_skills: List[str]) -> List[str]:
        """Get missing prerequisites for a user"""
        return [prereq for prereq in self.prerequisites if prereq not in user_skills]
    
    def calculate_readiness_score(self, user_skill_level: SkillLevel) -> int:
        """Calculate readiness score for a user based on their skill level"""
        level_scores = {
            SkillLevel.BEGINNER: 25,
            SkillLevel.INTERMEDIATE: 50,
            SkillLevel.ADVANCED: 75,
            SkillLevel.EXPERT: 100
        }
        
        user_score = level_scores.get(user_skill_level, 0)
        skill_score = level_scores.get(self.difficulty, 50)
        
        # Calculate readiness based on the gap between user level and skill difficulty
        if user_score >= skill_score:
            return 100  # User is ready
        elif user_score >= skill_score - 25:
            return 75  # User is close
        elif user_score >= skill_score - 50:
            return 50  # User needs some work
        else:
            return 25  # User needs significant work
    
    def activate(self) -> None:
        """Activate the skill"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the skill"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "difficulty": self.difficulty.value,
            "topics": [
                {
                    "id": str(topic.id),
                    "name": topic.name,
                    "description": topic.description,
                    "difficulty": topic.difficulty.value,
                    "prerequisites": topic.prerequisites,
                    "learning_objectives": topic.learning_objectives,
                    "estimated_hours": topic.estimated_hours,
                    "resources": topic.resources
                }
                for topic in self.topics
            ],
            "assessment": {
                "question_types": self.assessment.question_types,
                "difficulty_range": self.assessment.difficulty_range,
                "time_limit_minutes": self.assessment.time_limit_minutes,
                "passing_score": self.assessment.passing_score,
                "adaptive_difficulty": self.assessment.adaptive_difficulty
            },
            "resources": [
                {
                    "type": resource.type,
                    "title": resource.title,
                    "url": resource.url,
                    "description": resource.description,
                    "difficulty": resource.difficulty.value,
                    "rating": resource.rating,
                    "duration_hours": resource.duration_hours,
                    "cost": resource.cost,
                    "provider": resource.provider
                }
                for resource in self.resources
            ],
            "tags": self.tags,
            "prerequisites": self.prerequisites,
            "related_skills": self.related_skills,
            "industry_relevance": self.industry_relevance,
            "average_salary_impact": self.average_salary_impact,
            "learning_path": self.learning_path,
            "total_learning_hours": self.get_total_learning_hours(),
            "difficulty_distribution": self.get_difficulty_distribution(),
            "resource_types": self.get_resource_types(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
