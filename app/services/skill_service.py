from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import uuid

from app.models.skill import Skill, Domain, Role
from app.schemas.skill import SkillCreate, SkillUpdate, DomainCreate

class SkillService:
    """Service for skill, domain, and role management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_skills(self, skip: int = 0, limit: int = 100, category: Optional[str] = None, search: Optional[str] = None) -> List[Skill]:
        """Get skills with optional filtering."""
        query = self.db.query(Skill).filter(Skill.is_active == True)
        
        if category:
            query = query.filter(Skill.category == category)
        
        if search:
            query = query.filter(
                or_(
                    Skill.name.ilike(f"%{search}%"),
                    Skill.description.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def get_skill(self, skill_id: uuid.UUID) -> Optional[Skill]:
        """Get skill by ID."""
        return self.db.query(Skill).filter(Skill.id == skill_id).first()
    
    def create_skill(self, skill_create: SkillCreate) -> Skill:
        """Create a new skill."""
        # Check if skill already exists
        existing_skill = self.db.query(Skill).filter(Skill.name == skill_create.name).first()
        if existing_skill:
            from app.core.exceptions import ValidationError
            raise ValidationError("Skill with this name already exists")
        
        skill = Skill(**skill_create.dict())
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill
    
    def update_skill(self, skill_id: uuid.UUID, skill_update: SkillUpdate) -> Optional[Skill]:
        """Update skill."""
        skill = self.get_skill(skill_id)
        if not skill:
            return None
        
        update_data = skill_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(skill, field, value)
        
        self.db.commit()
        self.db.refresh(skill)
        return skill
    
    def delete_skill(self, skill_id: uuid.UUID) -> bool:
        """Delete skill (soft delete)."""
        skill = self.get_skill(skill_id)
        if not skill:
            return False
        
        skill.is_active = False
        self.db.commit()
        return True
    
    def get_domains(self, skip: int = 0, limit: int = 100) -> List[Domain]:
        """Get domains."""
        return self.db.query(Domain).filter(Domain.is_active == True).offset(skip).limit(limit).all()
    
    def get_domain(self, domain_id: uuid.UUID) -> Optional[Domain]:
        """Get domain by ID."""
        return self.db.query(Domain).filter(Domain.id == domain_id).first()
    
    def create_domain(self, domain_create: dict) -> Domain:
        """Create a new domain."""
        # Check if domain already exists
        existing_domain = self.db.query(Domain).filter(Domain.name == domain_create["name"]).first()
        if existing_domain:
            from app.core.exceptions import ValidationError
            raise ValidationError("Domain with this name already exists")
        
        domain = Domain(**domain_create)
        self.db.add(domain)
        self.db.commit()
        self.db.refresh(domain)
        return domain
    
    def get_roles(self, domain_id: Optional[uuid.UUID] = None) -> List[Role]:
        """Get roles, optionally filtered by domain."""
        query = self.db.query(Role).filter(Role.is_active == True)
        
        if domain_id:
            query = query.filter(Role.domain_id == domain_id)
        
        return query.all()
    
    def get_role(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get role by ID."""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_skill_categories(self) -> List[str]:
        """Get all unique skill categories."""
        result = self.db.query(Skill.category).filter(Skill.category.isnot(None)).distinct().all()
        return [row[0] for row in result if row[0]]
