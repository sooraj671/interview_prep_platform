"""
Create User Use Case
Use case for creating a new user
"""

from typing import Dict, Any
from uuid import UUID

from domain.entities.user import User, UserRole, AuthProvider, UserStatus, UserProfile, UserStats
from application.interfaces.repositories import UserRepository
from shared.exceptions.domain_exceptions import DuplicateResourceException, ValidationException


class CreateUserUseCase:
    """Use case for creating a new user"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, user_data: Dict[str, Any]) -> User:
        """Execute create user use case"""
        
        # Validate required fields
        self._validate_user_data(user_data)
        
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_data["email"])
        if existing_user:
            raise DuplicateResourceException(
                resource="user",
                field="email",
                value=user_data["email"]
            )
        
        # Create user entity
        user = User(
            email=user_data["email"],
            password_hash=user_data["password_hash"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=UserRole(user_data.get("role", "candidate")),
            auth_provider=AuthProvider(user_data.get("auth_provider", "email")),
            provider_id=user_data.get("provider_id"),
            status=UserStatus("pending_verification"),
            email_verified=False,
            phone_verified=False,
            two_factor_enabled=False,
            profile=UserProfile(
                bio=user_data.get("bio", ""),
                phone=user_data.get("phone"),
                city=user_data.get("city"),
                country=user_data.get("country"),
                years_of_experience=user_data.get("years_of_experience"),
                domain=user_data.get("domain"),
                linkedin_url=user_data.get("linkedin_url"),
                github_url=user_data.get("github_url"),
                portfolio_url=user_data.get("portfolio_url"),
                resume_url=user_data.get("resume_url"),
                skills=user_data.get("skills", []),
                preferences=user_data.get("preferences", {})
            ),
            stats=UserStats(
                total_assessments=0,
                completed_assessments=0,
                average_score=0.0,
                total_study_time=0,
                current_streak=0,
                longest_streak=0,
                skill_count=0,
                roadmap_count=0
            )
        )
        
        # Create user
        created_user = await self.user_repository.create(user)
        
        return created_user
    
    def _validate_user_data(self, user_data: Dict[str, Any]) -> None:
        """Validate user data"""
        
        # Required fields
        required_fields = ["email", "password_hash", "first_name", "last_name"]
        
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValidationException(
                    field=field,
                    message=f"{field} is required"
                )
        
        # Email validation
        email = user_data["email"]
        if "@" not in email or "." not in email:
            raise ValidationException(
                field="email",
                message="Invalid email format"
            )
        
        # Name validation
        first_name = user_data["first_name"]
        last_name = user_data["last_name"]
        
        if len(first_name) < 2 or len(first_name) > 100:
            raise ValidationException(
                field="first_name",
                message="First name must be between 2 and 100 characters"
            )
        
        if len(last_name) < 2 or len(last_name) > 100:
            raise ValidationException(
                field="last_name",
                message="Last name must be between 2 and 100 characters"
            )
        
        # Password hash validation
        password_hash = user_data["password_hash"]
        if len(password_hash) < 10:
            raise ValidationException(
                field="password_hash",
                message="Password hash must be at least 10 characters"
            )
        
        # Optional field validations
        if "role" in user_data:
            valid_roles = ["candidate", "interviewer", "admin", "recruiter"]
            if user_data["role"] not in valid_roles:
                raise ValidationException(
                    field="role",
                    message=f"Role must be one of: {', '.join(valid_roles)}"
                )
        
        if "auth_provider" in user_data:
            valid_providers = ["email", "google", "github", "linkedin"]
            if user_data["auth_provider"] not in valid_providers:
                raise ValidationException(
                    field="auth_provider",
                    message=f"Auth provider must be one of: {', '.join(valid_providers)}"
                )
