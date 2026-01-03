"""
Database Repository Implementations
PostgreSQL repository implementations following Clean Architecture
"""
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from domain.entities.user import User, UserRole, AuthProvider, UserStatus, UserProfile, UserStats, UserSession
from domain.entities.skill import Skill, SkillCategory, DifficultyLevel
from domain.entities.roadmap import Roadmap, RoadmapStatus, RoadmapTopic, TopicStatus
from domain.entities.assessment import Assessment, AssessmentType, AssessmentStatus
from domain.entities.analytics import Analytics
from application.interfaces.repositories import (
    UserRepository, SkillRepository, RoadmapRepository, 
    AssessmentRepository, AnalyticsRepository
)
from infrastructure.database.connection import DatabaseManager
from shared.exceptions.domain_exceptions import NotFoundException, DatabaseException


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL user repository implementation"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager.db
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        try:
            # Insert user
            user_id = await self.db.fetchval(
                """
                INSERT INTO users (email, password_hash, first_name, last_name, role, 
                                auth_provider, provider_id, status, email_verified, 
                                phone_verified, two_factor_enabled, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id
                """,
                user.email, user.password, user.first_name, user.last_name,
                user.role.value, user.auth_provider.value, user.provider_id,
                user.status.value, user.email_verified, user.phone_verified,
                user.two_factor_enabled, user.created_at, user.updated_at
            )
            
            user.id = user_id
            
            # Insert profile
            await self.db.execute(
                """
                INSERT INTO user_profiles (user_id, bio, phone, city, country, 
                                       years_of_experience, domain, linkedin_url, 
                                       github_url, portfolio_url, resume_url, skills, preferences)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                user_id, user.profile.bio, user.profile.phone, user.profile.city,
                user.profile.country, user.profile.years_of_experience, user.profile.domain,
                user.profile.linkedin_url, user.profile.github_url, user.profile.portfolio_url,
                user.profile.resume_url, json.dumps(user.profile.skills), 
                json.dumps(user.profile.preferences)
            )
            
            # Insert stats
            await self.db.execute(
                """
                INSERT INTO user_stats (user_id, total_assessments, completed_assessments, 
                                     average_score, total_study_time, current_streak, 
                                     longest_streak, skill_count, roadmap_count, last_active)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                user_id, user.stats.total_assessments, user.stats.completed_assessments,
                user.stats.average_score, user.stats.total_study_time, user.stats.current_streak,
                user.stats.longest_streak, user.stats.skill_count, user.stats.roadmap_count,
                user.stats.last_active
            )
            
            return user
            
        except Exception as e:
            raise DatabaseException(
                operation="create_user",
                reason=f"Failed to create user: {str(e)}"
            )
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        row = await self.db.fetchrow(
            """
            SELECT u.*, up.bio, up.phone, up.city, up.country, up.years_of_experience,
                   up.domain, up.linkedin_url, up.github_url, up.portfolio_url, up.resume_url,
                   up.skills, up.preferences, us.total_assessments, us.completed_assessments,
                   us.average_score, us.total_study_time, us.current_streak, us.longest_streak,
                   us.skill_count, us.roadmap_count, us.last_active
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            LEFT JOIN user_stats us ON u.id = us.user_id
            WHERE u.id = $1
            """,
            user_id
        )
        
        if not row:
            return None
        
        return self._row_to_user(row)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        row = await self.db.fetchrow(
            """
            SELECT u.*, up.bio, up.phone, up.city, up.country, up.years_of_experience,
                   up.domain, up.linkedin_url, up.github_url, up.portfolio_url, up.resume_url,
                   up.skills, up.preferences, us.total_assessments, us.completed_assessments,
                   us.average_score, us.total_study_time, us.current_streak, us.longest_streak,
                   us.skill_count, us.roadmap_count, us.last_active
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            LEFT JOIN user_stats us ON u.id = us.user_id
            WHERE u.email = $1
            """,
            email.lower()
        )
        
        if not row:
            return None
        
        return self._row_to_user(row)
    
    async def update(self, user: User) -> User:
        """Update user"""
        try:
            # Update user
            await self.db.execute(
                """
                UPDATE users SET first_name = $2, last_name = $3, role = $4, status = $5,
                               email_verified = $6, phone_verified = $7, two_factor_enabled = $8,
                               updated_at = $9, last_login = $10
                WHERE id = $1
                """,
                user.id, user.first_name, user.last_name, user.role.value,
                user.status.value, user.email_verified, user.phone_verified,
                user.two_factor_enabled, user.updated_at, user.last_login
            )
            
            # Update profile
            await self.db.execute(
                """
                UPDATE user_profiles SET bio = $2, phone = $3, city = $4, country = $5,
                                       years_of_experience = $6, domain = $7, linkedin_url = $8,
                                       github_url = $9, portfolio_url = $10, resume_url = $11,
                                       skills = $12, preferences = $13
                WHERE user_id = $1
                """,
                user.id, user.profile.bio, user.profile.phone, user.profile.city,
                user.profile.country, user.profile.years_of_experience, user.profile.domain,
                user.profile.linkedin_url, user.profile.github_url, user.profile.portfolio_url,
                user.profile.resume_url, json.dumps(user.profile.skills),
                json.dumps(user.profile.preferences)
            )
            
            # Update stats
            await self.db.execute(
                """
                UPDATE user_stats SET total_assessments = $2, completed_assessments = $3,
                                     average_score = $4, total_study_time = $5, current_streak = $6,
                                     longest_streak = $7, skill_count = $8, roadmap_count = $9,
                                     last_active = $10
                WHERE user_id = $1
                """,
                user.id, user.stats.total_assessments, user.stats.completed_assessments,
                user.stats.average_score, user.stats.total_study_time, user.stats.current_streak,
                user.stats.longest_streak, user.stats.skill_count, user.stats.roadmap_count,
                user.stats.last_active
            )
            
            return user
            
        except Exception as e:
            raise DatabaseException(
                operation="update_user",
                reason=f"Failed to update user: {str(e)}"
            )
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        result = await self.db.execute(
            "DELETE FROM users WHERE id = $1",
            user_id
        )
        return result != "DELETE 0"
    
    def _row_to_user(self, row) -> User:
        """Convert database row to User entity"""
        profile = UserProfile(
            bio=row['bio'] or '',
            phone=row['phone'],
            city=row['city'],
            country=row['country'],
            years_of_experience=row['years_of_experience'],
            domain=row['domain'],
            linkedin_url=row['linkedin_url'],
            github_url=row['github_url'],
            portfolio_url=row['portfolio_url'],
            resume_url=row['resume_url'],
            skills=json.loads(row['skills']) if row['skills'] else [],
            preferences=json.loads(row['preferences']) if row['preferences'] else {}
        )
        
        stats = UserStats(
            total_assessments=row['total_assessments'] or 0,
            completed_assessments=row['completed_assessments'] or 0,
            average_score=float(row['average_score'] or 0),
            total_study_time=row['total_study_time'] or 0,
            current_streak=row['current_streak'] or 0,
            longest_streak=row['longest_streak'] or 0,
            skill_count=row['skill_count'] or 0,
            roadmap_count=row['roadmap_count'] or 0,
            last_active=row['last_active']
        )
        
        return User(
            id=row['id'],
            email=row['email'],
            password=row['password_hash'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            role=UserRole(row['role']),
            auth_provider=AuthProvider(row['auth_provider']),
            provider_id=row['provider_id'],
            status=UserStatus(row['status']),
            email_verified=row['email_verified'],
            phone_verified=row['phone_verified'],
            two_factor_enabled=row['two_factor_enabled'],
            profile=profile,
            stats=stats,
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            last_login=row['last_login']
        )


class PostgreSQLSkillRepository(SkillRepository):
    """PostgreSQL skill repository implementation"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager.db
    
    async def create(self, skill: Skill) -> Skill:
        """Create a new skill"""
        skill_id = await self.db.fetchval(
            """
            INSERT INTO skills (name, category, description, difficulty, tags, 
                             prerequisites, related_skills, industry_relevance, 
                             average_salary_impact, learning_path, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
            """,
            skill.name, skill.category.value, skill.description, skill.difficulty.value,
            json.dumps(skill.tags), json.dumps(skill.prerequisites),
            json.dumps(skill.related_skills), json.dumps(skill.industry_relevance),
            skill.average_salary_impact, json.dumps(skill.learning_path),
            skill.created_at, skill.updated_at
        )
        
        skill.id = skill_id
        return skill
    
    async def get_by_id(self, skill_id: UUID) -> Optional[Skill]:
        """Get skill by ID"""
        row = await self.db.fetchrow(
            "SELECT * FROM skills WHERE id = $1",
            skill_id
        )
        
        if not row:
            return None
        
        return self._row_to_skill(row)
    
    async def get_by_name(self, name: str) -> Optional[Skill]:
        """Get skill by name"""
        row = await self.db.fetchrow(
            "SELECT * FROM skills WHERE name = $1",
            name
        )
        
        if not row:
            return None
        
        return self._row_to_skill(row)
    
    async def list_by_category(self, category: SkillCategory) -> List[Skill]:
        """List skills by category"""
        rows = await self.db.fetch(
            "SELECT * FROM skills WHERE category = $1 ORDER BY name",
            category.value
        )
        
        return [self._row_to_skill(row) for row in rows]
    
    async def update(self, skill: Skill) -> Skill:
        """Update skill"""
        await self.db.execute(
            """
            UPDATE skills SET name = $2, category = $3, description = $4, difficulty = $5,
                             tags = $6, prerequisites = $7, related_skills = $8,
                             industry_relevance = $9, average_salary_impact = $10,
                             learning_path = $11, updated_at = $12
            WHERE id = $1
            """,
            skill.id, skill.name, skill.category.value, skill.description,
            skill.difficulty.value, json.dumps(skill.tags), json.dumps(skill.prerequisites),
            json.dumps(skill.related_skills), json.dumps(skill.industry_relevance),
            skill.average_salary_impact, json.dumps(skill.learning_path),
            skill.updated_at
        )
        
        return skill
    
    def _row_to_skill(self, row) -> Skill:
        """Convert database row to Skill entity"""
        return Skill(
            id=row['id'],
            name=row['name'],
            category=SkillCategory(row['category']),
            description=row['description'] or '',
            difficulty=DifficultyLevel(row['difficulty']),
            tags=json.loads(row['tags']) if row['tags'] else [],
            prerequisites=json.loads(row['prerequisites']) if row['prerequisites'] else [],
            related_skills=json.loads(row['related_skills']) if row['related_skills'] else [],
            industry_relevance=json.loads(row['industry_relevance']) if row['industry_relevance'] else {},
            average_salary_impact=row['average_salary_impact'],
            learning_path=json.loads(row['learning_path']) if row['learning_path'] else [],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )


class PostgreSQLRoadmapRepository(RoadmapRepository):
    """PostgreSQL roadmap repository implementation"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager.db
    
    async def create(self, roadmap: Roadmap) -> Roadmap:
        """Create a new roadmap"""
        roadmap_id = await self.db.fetchval(
            """
            INSERT INTO roadmaps (user_id, title, description, target_role, duration_weeks,
                                difficulty, status, progress_percentage, total_topics,
                                completed_topics, ai_generated, generation_prompt, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING id
            """,
            roadmap.user_id, roadmap.title, roadmap.description, roadmap.target_role,
            roadmap.duration_weeks, roadmap.difficulty, roadmap.status.value,
            roadmap.progress_percentage, roadmap.total_topics, roadmap.completed_topics,
            roadmap.ai_generated, roadmap.generation_prompt, roadmap.created_at, roadmap.updated_at
        )
        
        roadmap.id = roadmap_id
        return roadmap
    
    async def get_by_id(self, roadmap_id: UUID) -> Optional[Roadmap]:
        """Get roadmap by ID"""
        row = await self.db.fetchrow(
            "SELECT * FROM roadmaps WHERE id = $1",
            roadmap_id
        )
        
        if not row:
            return None
        
        return self._row_to_roadmap(row)
    
    async def list_by_user(self, user_id: UUID) -> List[Roadmap]:
        """List roadmaps by user"""
        rows = await self.db.fetch(
            "SELECT * FROM roadmaps WHERE user_id = $1 ORDER BY created_at DESC",
            user_id
        )
        
        return [self._row_to_roadmap(row) for row in rows]
    
    def _row_to_roadmap(self, row) -> Roadmap:
        """Convert database row to Roadmap entity"""
        return Roadmap(
            id=row['id'],
            user_id=row['user_id'],
            title=row['title'],
            description=row['description'] or '',
            target_role=row['target_role'],
            duration_weeks=row['duration_weeks'],
            difficulty=row['difficulty'],
            status=RoadmapStatus(row['status']),
            progress_percentage=row['progress_percentage'],
            total_topics=row['total_topics'],
            completed_topics=row['completed_topics'],
            ai_generated=row['ai_generated'],
            generation_prompt=row['generation_prompt'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at']
        )


class PostgreSQLAssessmentRepository(AssessmentRepository):
    """PostgreSQL assessment repository implementation"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager.db
    
    async def create(self, assessment: Assessment) -> Assessment:
        """Create a new assessment"""
        assessment_id = await self.db.fetchval(
            """
            INSERT INTO assessments (title, assessment_type, skill_ids, difficulty, duration_minutes,
                                  user_id, roadmap_id, status, adaptive_difficulty, allow_hints,
                                  allow_review, randomize_questions, passing_score, max_attempts,
                                  time_limit_per_question, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            RETURNING id
            """,
            assessment.title, assessment.assessment_type.value,
            json.dumps(assessment.skill_ids), assessment.difficulty,
            assessment.duration_minutes, assessment.user_id, assessment.roadmap_id,
            assessment.status.value, assessment.adaptive_difficulty, assessment.allow_hints,
            assessment.allow_review, assessment.randomize_questions, assessment.passing_score,
            assessment.max_attempts, assessment.time_limit_per_question,
            assessment.created_at, assessment.updated_at
        )
        
        assessment.id = assessment_id
        return assessment
    
    async def get_by_id(self, assessment_id: UUID) -> Optional[Assessment]:
        """Get assessment by ID"""
        row = await self.db.fetchrow(
            "SELECT * FROM assessments WHERE id = $1",
            assessment_id
        )
        
        if not row:
            return None
        
        return self._row_to_assessment(row)
    
    def _row_to_assessment(self, row) -> Assessment:
        """Convert database row to Assessment entity"""
        return Assessment(
            id=row['id'],
            title=row['title'],
            assessment_type=AssessmentType(row['assessment_type']),
            skill_ids=json.loads(row['skill_ids']) if row['skill_ids'] else [],
            difficulty=row['difficulty'],
            duration_minutes=row['duration_minutes'],
            user_id=row['user_id'],
            roadmap_id=row['roadmap_id'],
            status=AssessmentStatus(row['status']),
            adaptive_difficulty=row['adaptive_difficulty'],
            allow_hints=row['allow_hints'],
            allow_review=row['allow_review'],
            randomize_questions=row['randomize_questions'],
            passing_score=row['passing_score'],
            max_attempts=row['max_attempts'],
            time_limit_per_question=row['time_limit_per_question'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at'],
            expires_at=row['expires_at'],
            last_activity_at=row['last_activity_at']
        )


class PostgreSQLAnalyticsRepository(AnalyticsRepository):
    """PostgreSQL analytics repository implementation"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager.db
    
    async def create(self, analytics: Analytics) -> Analytics:
        """Create new analytics record"""
        analytics_id = await self.db.fetchval(
            """
            INSERT INTO analytics (user_id, skill_progress, readiness_trends, assessment_history,
                                 topic_coverage, study_time, leaderboards, summary, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id
            """,
            analytics.user_id, json.dumps(analytics.skill_progress),
            json.dumps(analytics.readiness_trends), json.dumps(analytics.assessment_history),
            json.dumps(analytics.topic_coverage), json.dumps(analytics.study_time),
            json.dumps(analytics.leaderboards), json.dumps(analytics.get_overall_summary()),
            analytics.created_at, analytics.updated_at
        )
        
        analytics.id = analytics_id
        return analytics
    
    async def get_by_user(self, user_id: UUID) -> Optional[Analytics]:
        """Get analytics by user"""
        row = await self.db.fetchrow(
            "SELECT * FROM analytics WHERE user_id = $1",
            user_id
        )
        
        if not row:
            return None
        
        return self._row_to_analytics(row)
    
    def _row_to_analytics(self, row) -> Analytics:
        """Convert database row to Analytics entity"""
        return Analytics(
            id=row['id'],
            user_id=row['user_id'],
            skill_progress=json.loads(row['skill_progress']) if row['skill_progress'] else {},
            readiness_trends=json.loads(row['readiness_trends']) if row['readiness_trends'] else {},
            assessment_history=json.loads(row['assessment_history']) if row['assessment_history'] else {},
            topic_coverage=json.loads(row['topic_coverage']) if row['topic_coverage'] else {},
            study_time=json.loads(row['study_time']) if row['study_time'] else {},
            leaderboards=json.loads(row['leaderboards']) if row['leaderboards'] else {},
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
