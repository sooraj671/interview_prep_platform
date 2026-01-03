"""
Repository Interfaces - Abstract definitions for data access
Following Clean Architecture principles
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from domain.entities.user import User, UserRole
from domain.entities.skill import Skill, SkillCategory, DifficultyLevel
from domain.entities.roadmap import Roadmap, RoadmapStatus
from domain.entities.assessment import Assessment, AssessmentStatus, AssessmentType
from domain.entities.analytics import Analytics, MetricType


class UserRepository(ABC):
    """Abstract repository for User entities"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_by_oauth_provider(self, provider: str, provider_user_id: str) -> Optional[User]:
        """Get user by OAuth provider info"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        pass
    
    @abstractmethod
    async def list_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """List users by role"""
        pass
    
    @abstractmethod
    async def search(self, query: str, filters: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users"""
        pass


class SkillRepository(ABC):
    """Abstract repository for Skill entities"""
    
    @abstractmethod
    async def create(self, skill: Skill) -> Skill:
        """Create a new skill"""
        pass
    
    @abstractmethod
    async def get_by_id(self, skill_id: UUID) -> Optional[Skill]:
        """Get skill by ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Skill]:
        """Get skill by name"""
        pass
    
    @abstractmethod
    async def update(self, skill: Skill) -> Skill:
        """Update skill"""
        pass
    
    @abstractmethod
    async def delete(self, skill_id: UUID) -> bool:
        """Delete skill"""
        pass
    
    @abstractmethod
    async def list(
        self, 
        category: Optional[SkillCategory] = None,
        difficulty: Optional[DifficultyLevel] = None,
        search: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Skill]:
        """List skills with filters"""
        pass
    
    @abstractmethod
    async def get_domains(self) -> List[str]:
        """Get skill domains"""
        pass
    
    @abstractmethod
    async def get_related_skills(self, skill_id: UUID) -> List[Skill]:
        """Get related skills"""
        pass


class RoadmapRepository(ABC):
    """Abstract repository for Roadmap entities"""
    
    @abstractmethod
    async def create(self, roadmap: Roadmap) -> Roadmap:
        """Create a new roadmap"""
        pass
    
    @abstractmethod
    async def get_by_id(self, roadmap_id: UUID) -> Optional[Roadmap]:
        """Get roadmap by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Roadmap]:
        """Get roadmaps for a user"""
        pass
    
    @abstractmethod
    async def update(self, roadmap: Roadmap) -> Roadmap:
        """Update roadmap"""
        pass
    
    @abstractmethod
    async def delete(self, roadmap_id: UUID) -> bool:
        """Delete roadmap"""
        pass
    
    @abstractmethod
    async def list_by_status(self, status: RoadmapStatus, skip: int = 0, limit: int = 100) -> List[Roadmap]:
        """List roadmaps by status"""
        pass
    
    @abstractmethod
    async def get_by_target_role(self, target_role: str, skip: int = 0, limit: int = 100) -> List[Roadmap]:
        """Get roadmaps by target role"""
        pass


class AssessmentRepository(ABC):
    """Abstract repository for Assessment entities"""
    
    @abstractmethod
    async def create(self, assessment: Assessment) -> Assessment:
        """Create a new assessment"""
        pass
    
    @abstractmethod
    async def get_by_id(self, assessment_id: UUID) -> Optional[Assessment]:
        """Get assessment by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get assessments for a user"""
        pass
    
    @abstractmethod
    async def get_by_roadmap_id(self, roadmap_id: UUID, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get assessments for a roadmap"""
        pass
    
    @abstractmethod
    async def update(self, assessment: Assessment) -> Assessment:
        """Update assessment"""
        pass
    
    @abstractmethod
    async def delete(self, assessment_id: UUID) -> bool:
        """Delete assessment"""
        pass
    
    @abstractmethod
    async def list_by_type(self, assessment_type: AssessmentType, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """List assessments by type"""
        pass
    
    @abstractmethod
    async def list_by_status(self, status: AssessmentStatus, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """List assessments by status"""
        pass
    
    @abstractmethod
    async def get_by_skill_ids(self, skill_ids: List[str], skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get assessments by skill IDs"""
        pass


class AnalyticsRepository(ABC):
    """Abstract repository for Analytics entities"""
    
    @abstractmethod
    async def create(self, analytics: Analytics) -> Analytics:
        """Create analytics for a user"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[Analytics]:
        """Get analytics by user ID"""
        pass
    
    @abstractmethod
    async def update(self, analytics: Analytics) -> Analytics:
        """Update analytics"""
        pass
    
    @abstractmethod
    async def get_skill_progress_trends(self, user_id: UUID, skill_name: str, days: int = 30) -> Dict[str, Any]:
        """Get skill progress trends"""
        pass
    
    @abstractmethod
    async def get_readiness_trends(self, user_id: UUID, target_role: str, days: int = 30) -> Dict[str, Any]:
        """Get readiness trends"""
        pass
    
    @abstractmethod
    async def get_assessment_performance(self, user_id: UUID, assessment_type: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get assessment performance"""
        pass
    
    @abstractmethod
    async def get_study_time_analytics(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get study time analytics"""
        pass
    
    @abstractmethod
    async def get_leaderboard(self, metric_type: MetricType, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard data"""
        pass


class FileStorageRepository(ABC):
    """Abstract repository for file storage"""
    
    @abstractmethod
    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        """Upload file and return URL"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        """Delete file by URL"""
        pass
    
    @abstractmethod
    async def get_file_metadata(self, file_url: str) -> Dict[str, Any]:
        """Get file metadata"""
        pass


class VectorStorageRepository(ABC):
    """Abstract repository for vector storage"""
    
    @abstractmethod
    async def store_embedding(self, text_id: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store text embedding"""
        pass
    
    @abstractmethod
    async def search_similar(self, query_embedding: List[float], limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        pass
    
    @abstractmethod
    async def delete_embedding(self, text_id: str) -> bool:
        """Delete embedding"""
        pass
    
    @abstractmethod
    async def update_embedding(self, text_id: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update embedding"""
        pass


class CacheRepository(ABC):
    """Abstract repository for caching"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern"""
        pass


class EventRepository(ABC):
    """Abstract repository for event sourcing"""
    
    @abstractmethod
    async def save_event(self, aggregate_id: UUID, event_type: str, event_data: Dict[str, Any], version: int) -> bool:
        """Save domain event"""
        pass
    
    @abstractmethod
    async def get_events(self, aggregate_id: UUID, from_version: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get events for aggregate"""
        pass
    
    @abstractmethod
    async def get_latest_version(self, aggregate_id: UUID) -> int:
        """Get latest version for aggregate"""
        pass
