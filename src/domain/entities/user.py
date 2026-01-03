"""
User Domain Entity
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from dataclasses import dataclass, field


class UserRole(str, Enum):
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"
    ADMIN = "admin"
    RECRUITER = "recruiter"


class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"
    LINKEDIN = "linkedin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


@dataclass
class UserProfile:
    """User profile information"""
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
    skills: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserStats:
    """User statistics"""
    total_assessments: int = 0
    completed_assessments: int = 0
    average_score: float = 0.0
    total_study_time: int = 0  # minutes
    current_streak: int = 0
    longest_streak: int = 0
    skill_count: int = 0
    roadmap_count: int = 0
    last_active: Optional[datetime] = None


@dataclass
class UserSession:
    """User session information"""
    session_id: UUID
    access_token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = uuid4()


class User:
    """User domain entity"""
    
    def __init__(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.CANDIDATE,
        auth_provider: AuthProvider = AuthProvider.EMAIL,
        provider_id: Optional[str] = None,
        profile: Optional[UserProfile] = None,
        stats: Optional[UserStats] = None,
        status: UserStatus = UserStatus.PENDING_VERIFICATION,
        email_verified: bool = False,
        phone_verified: bool = False,
        two_factor_enabled: bool = False,
        sessions: Optional[List[UserSession]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        id: Optional[UUID] = None,
    ):
        self.id = id or uuid4()
        self.email = email.lower().strip()
        self.password = password
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.role = role
        self.auth_provider = auth_provider
        self.provider_id = provider_id
        self.profile = profile or UserProfile()
        self.stats = stats or UserStats()
        self.status = status
        self.email_verified = email_verified
        self.phone_verified = phone_verified
        self.two_factor_enabled = two_factor_enabled
        self.sessions = sessions or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_login = last_login
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def update_profile(self, **kwargs) -> None:
        """Update user profile"""
        for key, value in kwargs.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)
        self.updated_at = datetime.utcnow()
    
    def update_stats(self, **kwargs) -> None:
        """Update user statistics"""
        for key, value in kwargs.items():
            if hasattr(self.stats, key):
                setattr(self.stats, key, value)
        self.updated_at = datetime.utcnow()
    
    def add_session(self, session: UserSession) -> None:
        """Add a new session"""
        # Remove expired sessions
        self.sessions = [s for s in self.sessions if s.expires_at > datetime.utcnow()]
        
        # Add new session
        self.sessions.append(session)
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def remove_session(self, session_id: UUID) -> None:
        """Remove a session"""
        self.sessions = [s for s in self.sessions if s.session_id != session_id]
        self.updated_at = datetime.utcnow()
    
    def clear_all_sessions(self) -> None:
        """Clear all sessions"""
        self.sessions = []
        self.updated_at = datetime.utcnow()
    
    def verify_email(self) -> None:
        """Mark email as verified"""
        self.email_verified = True
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def verify_phone(self) -> None:
        """Mark phone as verified"""
        self.phone_verified = True
        self.updated_at = datetime.utcnow()
    
    def enable_two_factor(self) -> None:
        """Enable two-factor authentication"""
        self.two_factor_enabled = True
        self.updated_at = datetime.utcnow()
    
    def disable_two_factor(self) -> None:
        """Disable two-factor authentication"""
        self.two_factor_enabled = False
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        self.status = UserStatus.INACTIVE
        self.clear_all_sessions()
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate user account"""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def suspend(self) -> None:
        """Suspend user account"""
        self.status = UserStatus.SUSPENDED
        self.clear_all_sessions()
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE
    
    def is_verified(self) -> bool:
        """Check if user is verified"""
        return self.email_verified
    
    def has_valid_session(self) -> bool:
        """Check if user has any valid sessions"""
        return any(s.expires_at > datetime.utcnow() for s in self.sessions)
    
    def get_active_sessions(self) -> List[UserSession]:
        """Get all active sessions"""
        return [s for s in self.sessions if s.expires_at > datetime.utcnow()]
    
    def update_last_active(self) -> None:
        """Update last active timestamp"""
        self.stats.last_active = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "id": str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role.value,
            "auth_provider": self.auth_provider.value,
            "provider_id": self.provider_id,
            "status": self.status.value,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "two_factor_enabled": self.two_factor_enabled,
            "profile": {
                "bio": self.profile.bio,
                "phone": self.profile.phone,
                "city": self.profile.city,
                "country": self.profile.country,
                "years_of_experience": self.profile.years_of_experience,
                "domain": self.profile.domain,
                "linkedin_url": self.profile.linkedin_url,
                "github_url": self.profile.github_url,
                "portfolio_url": self.profile.portfolio_url,
                "resume_url": self.profile.resume_url,
                "skills": self.profile.skills,
                "preferences": self.profile.preferences
            },
            "stats": {
                "total_assessments": self.stats.total_assessments,
                "completed_assessments": self.stats.completed_assessments,
                "average_score": self.stats.average_score,
                "total_study_time": self.stats.total_study_time,
                "current_streak": self.stats.current_streak,
                "longest_streak": self.stats.longest_streak,
                "skill_count": self.stats.skill_count,
                "roadmap_count": self.stats.roadmap_count,
                "last_active": self.stats.last_active.isoformat() if self.stats.last_active else None
            },
            "sessions": [
                {
                    "session_id": str(session.session_id),
                    "expires_at": session.expires_at.isoformat(),
                    "created_at": session.created_at.isoformat(),
                    "last_used": session.last_used.isoformat(),
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent
                }
                for session in self.get_active_sessions()
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
