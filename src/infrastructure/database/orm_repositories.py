"""
Database Repository Implementations using SQLAlchemy ORM
PostgreSQL repository implementations following Clean Architecture with SQLAlchemy ORM
"""
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload

from domain.entities.user import User, UserRole, AuthProvider, UserStatus, UserProfile, UserStats, UserSession
from domain.entities.skill import Skill, SkillCategory, DifficultyLevel
from domain.entities.roadmap import Roadmap, RoadmapStatus, RoadmapTopic, TopicStatus
from domain.entities.assessment import Assessment, AssessmentType, AssessmentStatus
from domain.entities.analytics import Analytics
from application.interfaces.repositories import (
    UserRepository, SkillRepository, RoadmapRepository, 
    AssessmentRepository, AnalyticsRepository
)
from infrastructure.database.models import (
    User as UserModel, UserProfile as UserProfileModel, UserStats as UserStatsModel,
    UserSession as UserSessionModel, Skill as SkillModel, SkillTopic as SkillTopicModel,
    SkillResource as SkillResourceModel, UserSkillProgress as UserSkillProgressModel,
    Roadmap as RoadmapModel, RoadmapTopic as RoadmapTopicModel,
    LearningResource as LearningResourceModel, PracticeExercise as PracticeExerciseModel,
    RoadmapMilestone as RoadmapMilestoneModel, Assessment as AssessmentModel,
    AssessmentQuestion as AssessmentQuestionModel, AssessmentResponse as AssessmentResponseModel,
    QuestionEvaluation as QuestionEvaluationModel, SkillAssessment as SkillAssessmentModel,
    Analytics as AnalyticsModel, AnalyticsDataPoint as AnalyticsDataPointModel,
    Leaderboard as LeaderboardModel
)
from shared.exceptions.domain_exceptions import NotFoundException, DatabaseException


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL user repository implementation using SQLAlchemy ORM"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        try:
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
            await self.session.flush()  # Get the ID
            
            # Create profile if provided
            if user.profile:
                profile_model = UserProfileModel(
                    user_id=user_model.id,
                    bio=user.profile.bio,
                    phone=user.profile.phone,
                    city=user.profile.city,
                    country=user.profile.country,
                    years_of_experience=user.profile.years_of_experience,
                    domain=user.profile.domain,
                    linkedin_url=user.profile.linkedin_url,
                    github_url=user.profile.github_url,
                    portfolio_url=user.profile.portfolio_url,
                    resume_url=user.profile.resume_url,
                    skills=user.profile.skills,
                    preferences=user.profile.preferences
                )
                self.session.add(profile_model)
            
            # Create stats if provided
            if user.stats:
                stats_model = UserStatsModel(
                    user_id=user_model.id,
                    total_assessments=user.stats.total_assessments,
                    completed_assessments=user.stats.completed_assessments,
                    average_score=user.stats.average_score,
                    total_study_time=user.stats.total_study_time,
                    current_streak=user.stats.current_streak,
                    longest_streak=user.stats.longest_streak,
                    skill_count=user.stats.skill_count,
                    roadmap_count=user.stats.roadmap_count,
                    last_active=user.stats.last_active
                )
                self.session.add(stats_model)
            
            await self.session.commit()
            
            # Update domain entity with generated ID
            user.id = user_model.id
            
            return user
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="create_user",
                reason=f"Failed to create user: {str(e)}"
            )
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        try:
            stmt = select(UserModel).options(
                selectinload(UserModel.profile),
                selectinload(UserModel.stats),
                selectinload(UserModel.sessions),
                selectinload(UserModel.skill_progress),
                selectinload(UserModel.roadmaps),
                selectinload(UserModel.assessments),
                selectinload(UserModel.analytics)
            ).where(UserModel.id == user_id)
            
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return self._map_to_domain_user(user_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_user_by_id",
                reason=f"Failed to get user: {str(e)}"
            )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            stmt = select(UserModel).options(
                selectinload(UserModel.profile),
                selectinload(UserModel.stats)
            ).where(UserModel.email == email)
            
            result = await self.session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            return self._map_to_domain_user(user_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_user_by_email",
                reason=f"Failed to get user by email: {str(e)}"
            )
    
    async def update(self, user: User) -> User:
        """Update user"""
        try:
            stmt = update(UserModel).where(UserModel.id == user.id).values(
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
                last_login=user.last_login,
                updated_at=datetime.now(timezone.utc)
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            return user
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="update_user",
                reason=f"Failed to update user: {str(e)}"
            )
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        try:
            stmt = delete(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="delete_user",
                reason=f"Failed to delete user: {str(e)}"
            )
    
    async def list(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List users"""
        try:
            stmt = select(UserModel).options(
                selectinload(UserModel.profile),
                selectinload(UserModel.stats)
            ).limit(limit).offset(offset)
            
            result = await self.session.execute(stmt)
            user_models = result.scalars().all()
            
            return [self._map_to_domain_user(user_model) for user_model in user_models]
            
        except Exception as e:
            raise DatabaseException(
                operation="list_users",
                reason=f"Failed to list users: {str(e)}"
            )
    
    def _map_to_domain_user(self, user_model: UserModel) -> User:
        """Map SQLAlchemy model to domain entity"""
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
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login=user_model.last_login,
            profile=profile,
            stats=stats
        )


class PostgreSQLSkillRepository(SkillRepository):
    """PostgreSQL skill repository implementation using SQLAlchemy ORM"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, skill: Skill) -> Skill:
        """Create a new skill"""
        try:
            skill_model = SkillModel(
                name=skill.name,
                category=skill.category.value,
                description=skill.description,
                difficulty=skill.difficulty.value,
                tags=skill.tags,
                prerequisites=skill.prerequisites,
                related_skills=skill.related_skills,
                industry_relevance=skill.industry_relevance,
                average_salary_impact=skill.average_salary_impact,
                learning_path=skill.learning_path
            )
            
            self.session.add(skill_model)
            await self.session.commit()
            
            skill.id = skill_model.id
            return skill
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="create_skill",
                reason=f"Failed to create skill: {str(e)}"
            )
    
    async def get_by_id(self, skill_id: UUID) -> Optional[Skill]:
        """Get skill by ID"""
        try:
            stmt = select(SkillModel).options(
                selectinload(SkillModel.topics),
                selectinload(SkillModel.resources),
                selectinload(SkillModel.user_progress)
            ).where(SkillModel.id == skill_id)
            
            result = await self.session.execute(stmt)
            skill_model = result.scalar_one_or_none()
            
            if not skill_model:
                return None
            
            return self._map_to_domain_skill(skill_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_skill_by_id",
                reason=f"Failed to get skill: {str(e)}"
            )
    
    async def get_by_name(self, name: str) -> Optional[Skill]:
        """Get skill by name"""
        try:
            stmt = select(SkillModel).where(SkillModel.name == name)
            result = await self.session.execute(stmt)
            skill_model = result.scalar_one_or_none()
            
            if not skill_model:
                return None
            
            return self._map_to_domain_skill(skill_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_skill_by_name",
                reason=f"Failed to get skill by name: {str(e)}"
            )
    
    async def list(self, category: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Skill]:
        """List skills"""
        try:
            stmt = select(SkillModel)
            
            if category:
                stmt = stmt.where(SkillModel.category == category)
            
            stmt = stmt.limit(limit).offset(offset)
            
            result = await self.session.execute(stmt)
            skill_models = result.scalars().all()
            
            return [self._map_to_domain_skill(skill_model) for skill_model in skill_models]
            
        except Exception as e:
            raise DatabaseException(
                operation="list_skills",
                reason=f"Failed to list skills: {str(e)}"
            )
    
    async def update(self, skill: Skill) -> Skill:
        """Update skill"""
        try:
            stmt = update(SkillModel).where(SkillModel.id == skill.id).values(
                name=skill.name,
                category=skill.category.value,
                description=skill.description,
                difficulty=skill.difficulty.value,
                tags=skill.tags,
                prerequisites=skill.prerequisites,
                related_skills=skill.related_skills,
                industry_relevance=skill.industry_relevance,
                average_salary_impact=skill.average_salary_impact,
                learning_path=skill.learning_path,
                updated_at=datetime.now(timezone.utc)
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            return skill
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="update_skill",
                reason=f"Failed to update skill: {str(e)}"
            )
    
    async def delete(self, skill_id: UUID) -> bool:
        """Delete skill"""
        try:
            stmt = delete(SkillModel).where(SkillModel.id == skill_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="delete_skill",
                reason=f"Failed to delete skill: {str(e)}"
            )
    
    def _map_to_domain_skill(self, skill_model: SkillModel) -> Skill:
        """Map SQLAlchemy model to domain entity"""
        return Skill(
            id=skill_model.id,
            name=skill_model.name,
            category=SkillCategory(skill_model.category),
            description=skill_model.description,
            difficulty=DifficultyLevel(skill_model.difficulty),
            tags=skill_model.tags,
            prerequisites=skill_model.prerequisites,
            related_skills=skill_model.related_skills,
            industry_relevance=skill_model.industry_relevance,
            average_salary_impact=skill_model.average_salary_impact,
            learning_path=skill_model.learning_path,
            created_at=skill_model.created_at,
            updated_at=skill_model.updated_at
        )


# Additional repository classes would follow the same pattern...
class PostgreSQLRoadmapRepository(RoadmapRepository):
    """PostgreSQL roadmap repository implementation using SQLAlchemy ORM"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, roadmap: Roadmap) -> Roadmap:
        """Create a new roadmap"""
        try:
            roadmap_model = RoadmapModel(
                user_id=roadmap.user_id,
                title=roadmap.title,
                description=roadmap.description,
                target_role=roadmap.target_role,
                duration_weeks=roadmap.duration_weeks,
                difficulty=roadmap.difficulty.value,
                status=roadmap.status.value,
                progress_percentage=roadmap.progress_percentage,
                total_topics=roadmap.total_topics,
                completed_topics=roadmap.completed_topics,
                ai_generated=roadmap.ai_generated,
                generation_prompt=roadmap.generation_prompt,
                started_at=roadmap.started_at,
                completed_at=roadmap.completed_at
            )
            
            self.session.add(roadmap_model)
            await self.session.commit()
            
            roadmap.id = roadmap_model.id
            return roadmap
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="create_roadmap",
                reason=f"Failed to create roadmap: {str(e)}"
            )
    
    async def get_by_id(self, roadmap_id: UUID) -> Optional[Roadmap]:
        """Get roadmap by ID"""
        try:
            stmt = select(RoadmapModel).options(
                selectinload(RoadmapModel.topics),
                selectinload(RoadmapModel.milestones)
            ).where(RoadmapModel.id == roadmap_id)
            
            result = await self.session.execute(stmt)
            roadmap_model = result.scalar_one_or_none()
            
            if not roadmap_model:
                return None
            
            return self._map_to_domain_roadmap(roadmap_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_roadmap_by_id",
                reason=f"Failed to get roadmap: {str(e)}"
            )
    
    async def list(self, user_id: Optional[UUID] = None, limit: int = 100, offset: int = 0) -> List[Roadmap]:
        """List roadmaps"""
        try:
            stmt = select(RoadmapModel)
            
            if user_id:
                stmt = stmt.where(RoadmapModel.user_id == user_id)
            
            stmt = stmt.limit(limit).offset(offset)
            
            result = await self.session.execute(stmt)
            roadmap_models = result.scalars().all()
            
            return [self._map_to_domain_roadmap(roadmap_model) for roadmap_model in roadmap_models]
            
        except Exception as e:
            raise DatabaseException(
                operation="list_roadmaps",
                reason=f"Failed to list roadmaps: {str(e)}"
            )
    
    def _map_to_domain_roadmap(self, roadmap_model: RoadmapModel) -> Roadmap:
        """Map SQLAlchemy model to domain entity"""
        return Roadmap(
            id=roadmap_model.id,
            user_id=roadmap_model.user_id,
            title=roadmap_model.title,
            description=roadmap_model.description,
            target_role=roadmap_model.target_role,
            duration_weeks=roadmap_model.duration_weeks,
            difficulty=DifficultyLevel(roadmap_model.difficulty),
            status=RoadmapStatus(roadmap_model.status),
            progress_percentage=roadmap_model.progress_percentage,
            total_topics=roadmap_model.total_topics,
            completed_topics=roadmap_model.completed_topics,
            ai_generated=roadmap_model.ai_generated,
            generation_prompt=roadmap_model.generation_prompt,
            created_at=roadmap_model.created_at,
            updated_at=roadmap_model.updated_at,
            started_at=roadmap_model.started_at,
            completed_at=roadmap_model.completed_at
        )


class PostgreSQLAssessmentRepository(AssessmentRepository):
    """PostgreSQL assessment repository implementation using SQLAlchemy ORM"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, assessment: Assessment) -> Assessment:
        """Create a new assessment"""
        try:
            assessment_model = AssessmentModel(
                title=assessment.title,
                assessment_type=assessment.assessment_type.value,
                skill_ids=assessment.skill_ids,
                difficulty=assessment.difficulty.value,
                duration_minutes=assessment.duration_minutes,
                user_id=assessment.user_id,
                roadmap_id=assessment.roadmap_id,
                status=assessment.status.value,
                adaptive_difficulty=assessment.adaptive_difficulty,
                allow_hints=assessment.allow_hints,
                allow_review=assessment.allow_review,
                randomize_questions=assessment.randomize_questions,
                passing_score=assessment.passing_score,
                max_attempts=assessment.max_attempts,
                time_limit_per_question=assessment.time_limit_per_question,
                started_at=assessment.started_at,
                completed_at=assessment.completed_at,
                expires_at=assessment.expires_at,
                last_activity_at=assessment.last_activity_at
            )
            
            self.session.add(assessment_model)
            await self.session.commit()
            
            assessment.id = assessment_model.id
            return assessment
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="create_assessment",
                reason=f"Failed to create assessment: {str(e)}"
            )
    
    async def get_by_id(self, assessment_id: UUID) -> Optional[Assessment]:
        """Get assessment by ID"""
        try:
            stmt = select(AssessmentModel).options(
                selectinload(AssessmentModel.questions),
                selectinload(AssessmentModel.responses),
                selectinload(AssessmentModel.evaluations),
                selectinload(AssessmentModel.skill_assessments)
            ).where(AssessmentModel.id == assessment_id)
            
            result = await self.session.execute(stmt)
            assessment_model = result.scalar_one_or_none()
            
            if not assessment_model:
                return None
            
            return self._map_to_domain_assessment(assessment_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_assessment_by_id",
                reason=f"Failed to get assessment: {str(e)}"
            )
    
    def _map_to_domain_assessment(self, assessment_model: AssessmentModel) -> Assessment:
        """Map SQLAlchemy model to domain entity"""
        return Assessment(
            id=assessment_model.id,
            title=assessment_model.title,
            assessment_type=AssessmentType(assessment_model.assessment_type),
            skill_ids=assessment_model.skill_ids,
            difficulty=DifficultyLevel(assessment_model.difficulty),
            duration_minutes=assessment_model.duration_minutes,
            user_id=assessment_model.user_id,
            roadmap_id=assessment_model.roadmap_id,
            status=AssessmentStatus(assessment_model.status),
            adaptive_difficulty=assessment_model.adaptive_difficulty,
            allow_hints=assessment_model.allow_hints,
            allow_review=assessment_model.allow_review,
            randomize_questions=assessment_model.randomize_questions,
            passing_score=assessment_model.passing_score,
            max_attempts=assessment_model.max_attempts,
            time_limit_per_question=assessment_model.time_limit_per_question,
            started_at=assessment_model.started_at,
            completed_at=assessment_model.completed_at,
            expires_at=assessment_model.expires_at,
            last_activity_at=assessment_model.last_activity_at,
            created_at=assessment_model.created_at,
            updated_at=assessment_model.updated_at
        )


class PostgreSQLAnalyticsRepository(AnalyticsRepository):
    """PostgreSQL analytics repository implementation using SQLAlchemy ORM"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, analytics: Analytics) -> Analytics:
        """Create new analytics"""
        try:
            analytics_model = AnalyticsModel(
                user_id=analytics.user_id,
                skill_progress=analytics.skill_progress,
                readiness_trends=analytics.readiness_trends,
                assessment_history=analytics.assessment_history,
                topic_coverage=analytics.topic_coverage,
                study_time=analytics.study_time,
                leaderboards=analytics.leaderboards,
                summary=analytics.summary
            )
            
            self.session.add(analytics_model)
            await self.session.commit()
            
            analytics.id = analytics_model.id
            return analytics
            
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(
                operation="create_analytics",
                reason=f"Failed to create analytics: {str(e)}"
            )
    
    async def get_by_user_id(self, user_id: UUID) -> Optional[Analytics]:
        """Get analytics by user ID"""
        try:
            stmt = select(AnalyticsModel).where(AnalyticsModel.user_id == user_id)
            result = await self.session.execute(stmt)
            analytics_model = result.scalar_one_or_none()
            
            if not analytics_model:
                return None
            
            return self._map_to_domain_analytics(analytics_model)
            
        except Exception as e:
            raise DatabaseException(
                operation="get_analytics_by_user_id",
                reason=f"Failed to get analytics: {str(e)}"
            )
    
    def _map_to_domain_analytics(self, analytics_model: AnalyticsModel) -> Analytics:
        """Map SQLAlchemy model to domain entity"""
        return Analytics(
            id=analytics_model.id,
            user_id=analytics_model.user_id,
            skill_progress=analytics_model.skill_progress,
            readiness_trends=analytics_model.readiness_trends,
            assessment_history=analytics_model.assessment_history,
            topic_coverage=analytics_model.topic_coverage,
            study_time=analytics_model.study_time,
            leaderboards=analytics_model.leaderboards,
            summary=analytics_model.summary,
            created_at=analytics_model.created_at,
            updated_at=analytics_model.updated_at
        )
