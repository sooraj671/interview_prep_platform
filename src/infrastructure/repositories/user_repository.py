"""
SQLAlchemy User Repository
User repository implementation using SQLAlchemy ORM
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload, joinedload

from domain.entities.user import User, UserRole, AuthProvider, UserStatus, UserProfile, UserStats, UserSession
from application.interfaces.repositories import UserRepository
from infrastructure.database.models.user import User as UserModel, UserProfile as UserProfileModel, UserStats as UserStatsModel, UserSession as UserSessionModel
from shared.exceptions.domain_exceptions import NotFoundException, DatabaseException, DuplicateResourceException


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy user repository implementation"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user with profile and stats"""
        try:
            # Check if email already exists
            existing_user = await self.get_by_email(user.email)
            if existing_user:
                raise DuplicateResourceException(
                    resource="user",
                    field="email",
                    value=user.email
                )
            
            # Create user model
            user_model = UserModel(
                email=user.email,
                password_hash=user.password,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value,
                auth_provider=user.auth_provider.value,
                provider_id=user.provider_id,
                status=user.status.value,
                email_verified=user.email_verified,
                phone_verified=user.phone_verified,
                two_factor_enabled=user.two_factor_enabled,
                last_login=user.last_login
            )
            
            self.session.add(user_model)
            
            # Create user profile
            profile_model = UserProfileModel(
                id=user_model.id,  # Use the same ID as user
                bio=user.profile.bio if user.profile else "",
                phone=user.profile.phone if user.profile else None,
                city=user.profile.city if user.profile else None,
                country=user.profile.country if user.profile else None,
                years_of_experience=user.profile.years_of_experience if user.profile else None,
                domain=user.profile.domain if user.profile else None,
                linkedin_url=user.profile.linkedin_url if user.profile else None,
                github_url=user.profile.github_url if user.profile else None,
                portfolio_url=user.profile.portfolio_url if user.profile else None,
                resume_url=user.profile.resume_url if user.profile else None,
                skills=user.profile.skills if user.profile else [],
                preferences=user.profile.preferences if user.profile else {}
            )
            
            self.session.add(profile_model)
            
            # Create user stats
            stats_model = UserStatsModel(
                id=user_model.id,  # Use the same ID as user
                total_assessments=user.stats.total_assessments if user.stats else 0,
                completed_assessments=user.stats.completed_assessments if user.stats else 0,
                average_score=user.stats.average_score if user.stats else 0.0,
                total_study_time=user.stats.total_study_time if user.stats else 0,
                current_streak=user.stats.current_streak if user.stats else 0,
                longest_streak=user.stats.longest_streak if user.stats else 0,
                skill_count=user.stats.skill_count if user.stats else 0,
                roadmap_count=user.stats.roadmap_count if user.stats else 0,
                last_active=user.stats.last_active if user.stats else None
            )
            
            self.session.add(stats_model)
            
            # Flush to get the ID
            await self.session.flush()
            
            # Update domain entity with generated ID
            user.id = user_model.id
            user.created_at = user_model.created_at
            user.updated_at = user_model.updated_at
            
            return user
            
        except DuplicateResourceException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="create_user",
                reason=f"Failed to create user: {str(e)}"
            )
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID with profile and stats"""
        try:
            stmt = (
                select(UserModel)
                .options(
                    selectinload(UserModel.profile),
                    selectinload(UserModel.stats),
                    selectinload(UserModel.sessions)
                )
                .where(UserModel.id == user_id)
            )
            
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return self._model_to_entity(user_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_user_by_id",
                reason=f"Failed to get user: {str(e)}"
            )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email with profile and stats"""
        try:
            stmt = (
                select(UserModel)
                .options(
                    selectinload(UserModel.profile),
                    selectinload(UserModel.stats),
                    selectinload(UserModel.sessions)
                )
                .where(UserModel.email == email)
            )
            
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return self._model_to_entity(user_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_user_by_email",
                reason=f"Failed to get user by email: {str(e)}"
            )
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Get all users with pagination and filters"""
        try:
            stmt = (
                select(UserModel)
                .options(
                    selectinload(UserModel.profile),
                    selectinload(UserModel.stats)
                )
                .offset(skip)
                .limit(limit)
            )
            
            # Apply filters
            filters = []
            if role:
                filters.append(UserModel.role == role.value)
            if status:
                filters.append(UserModel.status == status.value)
            if search:
                filters.append(
                    or_(
                        UserModel.first_name.ilike(f"%{search}%"),
                        UserModel.last_name.ilike(f"%{search}%"),
                        UserModel.email.ilike(f"%{search}%")
                    )
                )
            
            if filters:
                stmt = stmt.where(and_(*filters))
            
            # Order by created_at
            stmt = stmt.order_by(UserModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            user_models = result.scalars().all()
            
            return [self._model_to_entity(user_model) for user_model in user_models]
            
        except Exception as e:
            raise DatabaseException(
                operation="get_all_users",
                reason=f"Failed to get users: {str(e)}"
            )
    
    async def update(self, user: User) -> User:
        """Update user and related entities"""
        try:
            # Get existing user
            stmt = select(UserModel).where(UserModel.id == user.id)
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                raise NotFoundException(
                    resource="user",
                    identifier=str(user.id)
                )
            
            # Update user fields
            user_model.email = user.email
            user_model.password_hash = user.password
            user_model.first_name = user.first_name
            user_model.last_name = user.last_name
            user_model.role = user.role.value
            user_model.auth_provider = user.auth_provider.value
            user_model.provider_id = user.provider_id
            user_model.status = user.status.value
            user_model.email_verified = user.email_verified
            user_model.phone_verified = user.phone_verified
            user_model.two_factor_enabled = user.two_factor_enabled
            user_model.last_login = user.last_login
            
            # Update profile if exists
            if user_model.profile:
                user_model.profile.bio = user.profile.bio
                user_model.profile.phone = user.profile.phone
                user_model.profile.city = user.profile.city
                user_model.profile.country = user.profile.country
                user_model.profile.years_of_experience = user.profile.years_of_experience
                user_model.profile.domain = user.profile.domain
                user_model.profile.linkedin_url = user.profile.linkedin_url
                user_model.profile.github_url = user.profile.github_url
                user_model.profile.portfolio_url = user.profile.portfolio_url
                user_model.profile.resume_url = user.profile.resume_url
                user_model.profile.skills = user.profile.skills
                user_model.profile.preferences = user.profile.preferences
            
            # Update stats if exists
            if user_model.stats:
                user_model.stats.total_assessments = user.stats.total_assessments
                user_model.stats.completed_assessments = user.stats.completed_assessments
                user_model.stats.average_score = user.stats.average_score
                user_model.stats.total_study_time = user.stats.total_study_time
                user_model.stats.current_streak = user.stats.current_streak
                user_model.stats.longest_streak = user.stats.longest_streak
                user_model.stats.skill_count = user.stats.skill_count
                user_model.stats.roadmap_count = user.stats.roadmap_count
                user_model.stats.last_active = user.stats.last_active
            
            await self.session.flush()
            
            # Update timestamps
            user.updated_at = user_model.updated_at
            
            return user
            
        except NotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="update_user",
                reason=f"Failed to update user: {str(e)}"
            )
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID"""
        try:
            stmt = delete(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            
            return result.rowcount > 0
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="delete_user",
                reason=f"Failed to delete user: {str(e)}"
            )
    
    async def count(
        self,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> int:
        """Count users with filters"""
        try:
            stmt = select(UserModel)
            
            # Apply filters
            filters = []
            if role:
                filters.append(UserModel.role == role.value)
            if status:
                filters.append(UserModel.status == status.value)
            if search:
                filters.append(
                    or_(
                        UserModel.first_name.ilike(f"%{search}%"),
                        UserModel.last_name.ilike(f"%{search}%"),
                        UserModel.email.ilike(f"%{search}%")
                    )
                )
            
            if filters:
                stmt = stmt.where(and_(*filters))
            
            result = await self.session.execute(stmt)
            return len(result.scalars().all())
            
        except Exception as e:
            raise DatabaseException(
                operation="count_users",
                reason=f"Failed to count users: {str(e)}"
            )
    
    async def create_session(self, user_id: UUID, access_token: str, refresh_token: str, expires_at: datetime, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> UserSession:
        """Create a new user session"""
        try:
            session_model = UserSessionModel(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.session.add(session_model)
            await self.session.flush()
            
            return UserSession(
                id=session_model.id,
                user_id=session_model.user_id,
                access_token=session_model.access_token,
                refresh_token=session_model.refresh_token,
                expires_at=session_model.expires_at,
                created_at=session_model.created_at,
                last_used=session_model.last_used,
                ip_address=session_model.ip_address,
                user_agent=session_model.user_agent
            )
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="create_session",
                reason=f"Failed to create session: {str(e)}"
            )
    
    async def get_active_sessions(self, user_id: UUID) -> List[UserSession]:
        """Get all active sessions for a user"""
        try:
            stmt = (
                select(UserSessionModel)
                .where(
                    and_(
                        UserSessionModel.user_id == user_id,
                        UserSessionModel.expires_at > datetime.utcnow()
                    )
                )
                .order_by(UserSessionModel.last_used.desc())
            )
            
            result = await self.session.execute(stmt)
            session_models = result.scalars().all()
            
            return [
                UserSession(
                    id=session.id,
                    user_id=session.user_id,
                    access_token=session.access_token,
                    refresh_token=session.refresh_token,
                    expires_at=session.expires_at,
                    created_at=session.created_at,
                    last_used=session.last_used,
                    ip_address=session.ip_address,
                    user_agent=session.user_agent
                )
                for session in session_models
            ]
            
        except Exception as e:
            raise DatabaseException(
                operation="get_active_sessions",
                reason=f"Failed to get active sessions: {str(e)}"
            )
    
    def _model_to_entity(self, user_model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity"""
        # Convert profile
        profile = None
        if user_model.profile:
            profile = UserProfile(
                bio=user_model.profile.bio,
                phone=user_model.profile.phone,
                city=user_model.profile.city,
                country=user_model.profile.country,
                years_of_experience=user_model.profile.years_of_experience,
                domain=user_model.profile.domain,
                linkedin_url=user_model.profile.linkedin_url,
                github_url=user_model.profile.github_url,
                portfolio_url=user_model.profile.portfolio_url,
                resume_url=user_model.profile.resume_url,
                skills=user_model.profile.skills,
                preferences=user_model.profile.preferences
            )
        
        # Convert stats
        stats = None
        if user_model.stats:
            stats = UserStats(
                total_assessments=user_model.stats.total_assessments,
                completed_assessments=user_model.stats.completed_assessments,
                average_score=float(user_model.stats.average_score),
                total_study_time=user_model.stats.total_study_time,
                current_streak=user_model.stats.current_streak,
                longest_streak=user_model.stats.longest_streak,
                skill_count=user_model.stats.skill_count,
                roadmap_count=user_model.stats.roadmap_count,
                last_active=user_model.stats.last_active
            )
        
        # Convert user
        return User(
            id=user_model.id,
            email=user_model.email,
            password=user_model.password_hash,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            role=UserRole(user_model.role),
            auth_provider=AuthProvider(user_model.auth_provider),
            provider_id=user_model.provider_id,
            status=UserStatus(user_model.status),
            email_verified=user_model.email_verified,
            phone_verified=user_model.phone_verified,
            two_factor_enabled=user_model.two_factor_enabled,
            last_login=user_model.last_login,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            profile=profile,
            stats=stats
        )
