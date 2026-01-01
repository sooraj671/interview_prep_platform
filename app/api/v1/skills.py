from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
import uuid

from app.database import get_db
from app.models.user import User
from app.models.skill import Skill, Domain
from app.schemas.skill import SkillResponse, SkillCreate, SkillUpdate, DomainResponse
from app.services.skill_service import SkillService
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[SkillResponse])
async def get_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Any:
    """Get list of skills with optional filtering."""
    skill_service = SkillService(db)
    return skill_service.get_skills(skip=skip, limit=limit, category=category, search=search)

@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Any:
    """Get skill by ID."""
    skill_service = SkillService(db)
    skill = skill_service.get_skill(skill_id)
    if not skill:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Skill not found")
    return skill

@router.post("/", response_model=SkillResponse)
async def create_skill(
    skill_create: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new skill (admin only for now)."""
    skill_service = SkillService(db)
    return skill_service.create_skill(skill_create)

@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: uuid.UUID,
    skill_update: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update skill (admin only for now)."""
    skill_service = SkillService(db)
    skill = skill_service.update_skill(skill_id, skill_update)
    if not skill:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Skill not found")
    return skill

@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete skill (admin only for now)."""
    skill_service = SkillService(db)
    skill_service.delete_skill(skill_id)
    return {"message": "Skill deleted successfully"}

# Domain endpoints
@router.get("/domains/", response_model=List[DomainResponse])
async def get_domains(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> Any:
    """Get list of domains."""
    skill_service = SkillService(db)
    return skill_service.get_domains(skip=skip, limit=limit)

@router.get("/domains/{domain_id}", response_model=DomainResponse)
async def get_domain(
    domain_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Any:
    """Get domain by ID."""
    skill_service = SkillService(db)
    domain = skill_service.get_domain(domain_id)
    if not domain:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Domain not found")
    return domain

@router.post("/domains/", response_model=DomainResponse)
async def create_domain(
    domain_create: dict,  # Simplified for now
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new domain (admin only for now)."""
    skill_service = SkillService(db)
    return skill_service.create_domain(domain_create)
