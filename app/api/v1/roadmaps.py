from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
import uuid

from app.database import get_db
from app.models.user import User
from app.schemas.roadmap import (
    RoadmapResponse, RoadmapCreate, RoadmapUpdate,
    TopicResponse, TopicCreate, TopicUpdate
)
from app.services.roadmap_service import RoadmapService
from app.dependencies import get_current_user, require_candidate_user

router = APIRouter()

@router.get("/", response_model=List[RoadmapResponse])
async def get_my_roadmaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's roadmaps."""
    roadmap_service = RoadmapService(db)
    return roadmap_service.get_user_roadmaps(current_user.id)

@router.post("/", response_model=RoadmapResponse)
async def create_roadmap(
    roadmap_create: RoadmapCreate,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new personalized roadmap."""
    roadmap_service = RoadmapService(db)
    return await roadmap_service.create_roadmap(current_user.id, roadmap_create)

@router.get("/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get roadmap by ID."""
    roadmap_service = RoadmapService(db)
    roadmap = roadmap_service.get_roadmap(roadmap_id, current_user.id)
    if not roadmap:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Roadmap not found")
    return roadmap

@router.put("/{roadmap_id}", response_model=RoadmapResponse)
async def update_roadmap(
    roadmap_id: uuid.UUID,
    roadmap_update: RoadmapUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update roadmap."""
    roadmap_service = RoadmapService(db)
    roadmap = roadmap_service.update_roadmap(roadmap_id, current_user.id, roadmap_update)
    if not roadmap:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Roadmap not found")
    return roadmap

@router.delete("/{roadmap_id}")
async def delete_roadmap(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete roadmap."""
    roadmap_service = RoadmapService(db)
    roadmap_service.delete_roadmap(roadmap_id, current_user.id)
    return {"message": "Roadmap deleted successfully"}

@router.post("/{roadmap_id}/regenerate", response_model=RoadmapResponse)
async def regenerate_roadmap(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Regenerate roadmap with updated parameters."""
    roadmap_service = RoadmapService(db)
    return await roadmap_service.regenerate_roadmap(roadmap_id, current_user.id)

# Topic endpoints
@router.get("/{roadmap_id}/topics", response_model=List[TopicResponse])
async def get_roadmap_topics(
    roadmap_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get topics for a roadmap."""
    roadmap_service = RoadmapService(db)
    # Verify roadmap belongs to user
    roadmap = roadmap_service.get_roadmap(roadmap_id, current_user.id)
    if not roadmap:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Roadmap not found")
    
    return roadmap_service.get_roadmap_topics(roadmap_id)

@router.get("/{roadmap_id}/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    roadmap_id: uuid.UUID,
    topic_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get topic by ID."""
    roadmap_service = RoadmapService(db)
    topic = roadmap_service.get_topic(topic_id, roadmap_id, current_user.id)
    if not topic:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Topic not found")
    return topic

@router.put("/{roadmap_id}/topics/{topic_id}/cover")
async def mark_topic_covered(
    roadmap_id: uuid.UUID,
    topic_id: uuid.UUID,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Mark topic as covered."""
    roadmap_service = RoadmapService(db)
    topic = roadmap_service.mark_topic_covered(topic_id, roadmap_id, current_user.id)
    if not topic:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Topic not found")
    
    return {"message": "Topic marked as covered"}
