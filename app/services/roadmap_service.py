from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid
from datetime import datetime

from app.models.roadmap import Roadmap, Topic, RoadmapStatusEnum
from app.models.user import User
from app.models.skill import Role
from app.schemas.roadmap import RoadmapCreate, RoadmapUpdate
from app.core.exceptions import NotFoundError, ValidationError
from app.ai.roadmap_generator import RoadmapGenerator

class RoadmapService:
    """Service for roadmap and topic management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.roadmap_generator = RoadmapGenerator()
    
    def get_user_roadmaps(self, user_id: uuid.UUID) -> List[Roadmap]:
        """Get all roadmaps for a user."""
        return self.db.query(Roadmap).filter(Roadmap.user_id == user_id).all()
    
    def get_roadmap(self, roadmap_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Roadmap]:
        """Get roadmap by ID for a specific user."""
        return self.db.query(Roadmap).filter(
            and_(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
        ).first()
    
    async def create_roadmap(self, user_id: uuid.UUID, roadmap_create: RoadmapCreate) -> Roadmap:
        """Create a new personalized roadmap."""
        # Archive existing active roadmaps for this user
        existing_roadmaps = self.db.query(Roadmap).filter(
            and_(Roadmap.user_id == user_id, Roadmap.status == RoadmapStatusEnum.ACTIVE)
        ).all()
        
        for roadmap in existing_roadmaps:
            roadmap.status = RoadmapStatusEnum.ARCHIVED
        
        # Get user's current profile and skills
        user_profile = self.db.query(User).filter(User.id == user_id).first()
        if not user_profile:
            raise NotFoundError("User not found")
        
        # Generate roadmap using AI
        generated_roadmap = await self.roadmap_generator.generate_roadmap(
            user_id=user_id,
            target_role=roadmap_create.target_role_name or "Software Engineer",
            current_skills=self._get_user_skills_summary(user_id),
            experience_level=self._get_user_experience_level(user_id),
            custom_requirements=roadmap_create.custom_requirements
        )
        
        # Create roadmap
        roadmap = Roadmap(
            user_id=user_id,
            role_id=roadmap_create.role_id,
            title=generated_roadmap["title"],
            description=generated_roadmap["description"],
            generated_by_ai=True,
            ai_model_version="llama3.1",
            total_topics=len(generated_roadmap["topics"])
        )
        
        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)
        
        # Create topics
        for i, topic_data in enumerate(generated_roadmap["topics"]):
            topic = Topic(
                roadmap_id=roadmap.id,
                title=topic_data["title"],
                description=topic_data["description"],
                content=topic_data.get("content"),
                difficulty_level=topic_data.get("difficulty"),
                estimated_hours=topic_data.get("estimated_hours"),
                prerequisites=topic_data.get("prerequisites"),
                skills_covered=topic_data.get("skills_covered"),
                order_index=i
            )
            self.db.add(topic)
        
        self.db.commit()
        self.db.refresh(roadmap)
        
        return roadmap
    
    def update_roadmap(self, roadmap_id: uuid.UUID, user_id: uuid.UUID, roadmap_update: RoadmapUpdate) -> Optional[Roadmap]:
        """Update roadmap."""
        roadmap = self.get_roadmap(roadmap_id, user_id)
        if not roadmap:
            return None
        
        update_data = roadmap_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(roadmap, field, value)
        
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap
    
    def delete_roadmap(self, roadmap_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete roadmap."""
        roadmap = self.get_roadmap(roadmap_id, user_id)
        if not roadmap:
            return False
        
        self.db.delete(roadmap)
        self.db.commit()
        return True
    
    async def regenerate_roadmap(self, roadmap_id: uuid.UUID, user_id: uuid.UUID) -> Roadmap:
        """Regenerate roadmap with updated parameters."""
        roadmap = self.get_roadmap(roadmap_id, user_id)
        if not roadmap:
            raise NotFoundError("Roadmap not found")
        
        # Get progress from current roadmap
        covered_topics = self.db.query(Topic).filter(
            and_(Topic.roadmap_id == roadmap_id, Topic.is_covered == True)
        ).all()
        
        covered_topic_ids = [topic.id for topic in covered_topics]
        
        # Archive current roadmap
        roadmap.status = RoadmapStatusEnum.REGENERATED
        
        # Generate new roadmap
        generated_roadmap = await self.roadmap_generator.generate_roadmap(
            user_id=user_id,
            target_role=roadmap.title,  # Use current title as target
            current_skills=self._get_user_skills_summary(user_id),
            experience_level=self._get_user_experience_level(user_id),
            preserve_progress=covered_topic_ids
        )
        
        # Create new roadmap
        new_roadmap = Roadmap(
            user_id=user_id,
            role_id=roadmap.role_id,
            title=generated_roadmap["title"],
            description=generated_roadmap["description"],
            generated_by_ai=True,
            ai_model_version="llama3.1",
            total_topics=len(generated_roadmap["topics"])
        )
        
        self.db.add(new_roadmap)
        self.db.commit()
        self.db.refresh(new_roadmap)
        
        # Create topics
        covered_count = 0
        for i, topic_data in enumerate(generated_roadmap["topics"]):
            # Check if this topic was covered in previous roadmap
            is_covered = self._should_mark_as_covered(topic_data, covered_topics)
            if is_covered:
                covered_count += 1
            
            topic = Topic(
                roadmap_id=new_roadmap.id,
                title=topic_data["title"],
                description=topic_data["description"],
                content=topic_data.get("content"),
                difficulty_level=topic_data.get("difficulty"),
                estimated_hours=topic_data.get("estimated_hours"),
                prerequisites=topic_data.get("prerequisites"),
                skills_covered=topic_data.get("skills_covered"),
                order_index=i,
                is_covered=is_covered
            )
            self.db.add(topic)
        
        # Update progress
        new_roadmap.covered_topics = covered_count
        new_roadmap.progress_percentage = (covered_count / new_roadmap.total_topics) * 100 if new_roadmap.total_topics > 0 else 0
        
        self.db.commit()
        self.db.refresh(new_roadmap)
        
        return new_roadmap
    
    def get_roadmap_topics(self, roadmap_id: uuid.UUID) -> List[Topic]:
        """Get all topics for a roadmap."""
        return self.db.query(Topic).filter(Topic.roadmap_id == roadmap_id).order_by(Topic.order_index).all()
    
    def get_topic(self, topic_id: uuid.UUID, roadmap_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Topic]:
        """Get topic by ID, ensuring it belongs to user's roadmap."""
        return self.db.query(Topic).join(Roadmap).filter(
            and_(
                Topic.id == topic_id,
                Topic.roadmap_id == roadmap_id,
                Roadmap.user_id == user_id
            )
        ).first()
    
    def mark_topic_covered(self, topic_id: uuid.UUID, roadmap_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Topic]:
        """Mark topic as covered and update roadmap progress."""
        topic = self.get_topic(topic_id, roadmap_id, user_id)
        if not topic:
            return None
        
        topic.is_covered = True
        self.db.commit()
        
        # Update roadmap progress
        roadmap = self.get_roadmap(roadmap_id, user_id)
        if roadmap:
            covered_count = self.db.query(Topic).filter(
                and_(Topic.roadmap_id == roadmap_id, Topic.is_covered == True)
            ).count()
            
            roadmap.covered_topics = covered_count
            roadmap.progress_percentage = (covered_count / roadmap.total_topics) * 100 if roadmap.total_topics > 0 else 0
            self.db.commit()
        
        return topic
    
    def _get_user_skills_summary(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get summary of user's skills for roadmap generation."""
        from app.models.user import UserSkill
        from app.models.skill import Skill
        
        user_skills = self.db.query(UserSkill, Skill).join(Skill).filter(UserSkill.user_id == user_id).all()
        
        return [
            {
                "name": skill.name,
                "category": skill.category,
                "rating": user_skill.self_rating,
                "assessed_score": user_skill.assessed_score
            }
            for user_skill, skill in user_skills
        ]
    
    def _get_user_experience_level(self, user_id: uuid.UUID) -> str:
        """Determine user's experience level."""
        from app.models.user import UserProfile
        
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile and profile.years_of_experience:
            if profile.years_of_experience < 2:
                return "beginner"
            elif profile.years_of_experience < 5:
                return "intermediate"
            else:
                return "advanced"
        
        return "beginner"
    
    def _should_mark_as_covered(self, new_topic: Dict[str, Any], covered_topics: List[Topic]) -> bool:
        """Determine if a topic should be marked as covered based on previous progress."""
        new_title = new_topic.get("title", "").lower()
        
        for covered_topic in covered_topics:
            covered_title = covered_topic.title.lower()
            # Simple matching - could be improved with semantic similarity
            if new_title == covered_title or new_title in covered_title or covered_title in new_title:
                return True
        
        return False
