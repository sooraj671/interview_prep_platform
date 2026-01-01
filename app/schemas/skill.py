from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    name: Optional[str] = None

class SkillResponse(SkillBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class DomainBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class DomainCreate(DomainBase):
    pass

class DomainUpdate(DomainBase):
    name: Optional[str] = None

class DomainResponse(DomainBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    title: str
    description: Optional[str] = None
    domain_id: Optional[uuid.UUID] = None
    required_skills: Optional[List[dict]] = None
    is_active: bool = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    title: Optional[str] = None

class RoleResponse(RoleBase):
    id: uuid.UUID
    domain_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
