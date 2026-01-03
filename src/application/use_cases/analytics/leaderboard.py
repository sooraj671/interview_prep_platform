"""
Leaderboard Use Case
Handles rankings and user discovery based on various criteria
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from domain.entities.user import User, UserRole
from domain.entities.analytics import Analytics, LeaderboardType, LeaderboardEntry
from application.interfaces.repositories import UserRepository, AnalyticsRepository


class LeaderboardRequest:
    """Leaderboard request data"""
    def __init__(
        self,
        leaderboard_type: str = "assessment_scores",
        category: str = "overall",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ):
        self.leaderboard_type = leaderboard_type
        self.category = category
        self.filters = filters or {}
        self.limit = limit
        self.skip = skip


class LeaderboardResponse:
    """Leaderboard response data"""
    def __init__(
        self,
        entries: List[Dict[str, Any]],
        total_participants: int,
        category: str,
        leaderboard_type: str,
        last_updated: datetime
    ):
        self.entries = entries
        self.total_participants = total_participants
        self.category = category
        self.leaderboard_type = leaderboard_type
        self.last_updated = last_updated


class UserDiscoveryRequest:
    """User discovery request data"""
    def __init__(
        self,
        user_type: str = "candidate",  # candidate or interviewer
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ):
        self.user_type = user_type
        self.filters = filters or {}
        self.search = search
        self.limit = limit
        self.skip = skip


class UserDiscoveryResponse:
    """User discovery response data"""
    def __init__(
        self,
        users: List[Dict[str, Any]],
        total_count: int,
        user_type: str,
        filters_applied: Dict[str, Any]
    ):
        self.users = users
        self.total_count = total_count
        self.user_type = user_type
        self.filters_applied = filters_applied


class LeaderboardUseCase:
    """Use case for generating leaderboards and rankings"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        analytics_repository: AnalyticsRepository
    ):
        self.user_repository = user_repository
        self.analytics_repository = analytics_repository
    
    async def get_leaderboard(self, request: LeaderboardRequest) -> LeaderboardResponse:
        """Get leaderboard based on specified criteria"""
        try:
            # Validate leaderboard type
            leaderboard_type = self._validate_leaderboard_type(request.leaderboard_type)
            
            # Get users based on filters
            users = await self._get_filtered_users(request.filters, request.user_type)
            
            # Calculate scores based on leaderboard type
            scored_users = await self._calculate_scores(users, leaderboard_type)
            
            # Sort and paginate
            sorted_users = sorted(scored_users, key=lambda x: x['score'], reverse=True)
            paginated_users = sorted_users[request.skip:request.skip + request.limit]
            
            # Create leaderboard entries
            entries = []
            for i, user_data in enumerate(paginated_users, start=request.skip + 1):
                entry = {
                    "rank": i,
                    "user_id": user_data['user_id'],
                    "display_name": user_data['display_name'],
                    "score": user_data['score'],
                    "profile_picture": user_data.get('profile_picture_url'),
                    "metadata": user_data.get('metadata', {}),
                    "change_in_rank": user_data.get('change_in_rank', 0)
                }
                entries.append(entry)
            
            return LeaderboardResponse(
                entries=entries,
                total_participants=len(users),
                category=request.category,
                leaderboard_type=request.leaderboard_type,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            raise ValueError(f"Failed to generate leaderboard: {str(e)}")
    
    def _validate_leaderboard_type(self, leaderboard_type: str) -> LeaderboardType:
        """Validate leaderboard type"""
        try:
            return LeaderboardType(leaderboard_type)
        except ValueError:
            raise ValueError(f"Invalid leaderboard type: {leaderboard_type}")
    
    async def _get_filtered_users(self, filters: Dict[str, Any], user_type: str = "candidate") -> List[User]:
        """Get users based on filters"""
        # Convert filters to user repository query
        query_params = {}
        
        # Handle different filter types
        if 'skills' in filters:
            query_params['skills'] = filters['skills']
        if 'domain' in filters:
            query_params['domain'] = filters['domain']
        if 'role' in filters:
            query_params['role'] = filters['role']
        if 'city' in filters:
            query_params['city'] = filters['city']
        if 'country' in filters:
            query_params['country'] = filters['country']
        if 'years_of_experience' in filters:
            query_params['years_of_experience'] = filters['years_of_experience']
        
        # Get users by role
        if user_type == "candidate":
            users = await self.user_repository.list_by_role(UserRole.CANDIDATE, **query_params)
        elif user_type == "interviewer":
            users = await self.user_repository.list_by_role(UserRole.INTERVIEWER, **query_params)
        else:
            users = await self.user_repository.list_by_role(UserRole.CANDIDATE, **query_params)
        
        return users
    
    async def _calculate_scores(self, users: List[User], leaderboard_type: LeaderboardType) -> List[Dict[str, Any]]:
        """Calculate scores for users based on leaderboard type"""
        scored_users = []
        
        for user in users:
            score = 0
            metadata = {}
            
            if leaderboard_type == LeaderboardType.ASSESSMENT_SCORES:
                score = await self._get_assessment_score(user.id)
                metadata['assessment_count'] = await self._get_assessment_count(user.id)
                metadata['average_score'] = await self._get_average_assessment_score(user.id)
                
            elif leaderboard_type == LeaderboardType.SKILL_MASTERY:
                score = await self._get_skill_mastery_score(user.id)
                metadata['skills_mastered'] = await self._get_skills_mastered_count(user.id)
                metadata['total_skills'] = await self._get_total_skills_count(user.id)
                
            elif leaderboard_type == LeaderboardType.READINESS_SCORE:
                score = await self._get_readiness_score(user.id)
                metadata['target_roles'] = await self._get_target_roles(user.id)
                
            elif leaderboard_type == LeaderboardType.STUDY_TIME:
                score = await self._get_study_time_score(user.id)
                metadata['total_study_hours'] = await self._get_total_study_hours(user.id)
                metadata['current_streak'] = await self._get_current_streak(user.id)
                
            elif leaderboard_type == LeaderboardType.COMPLETION_RATE:
                score = await self._get_completion_rate_score(user.id)
                metadata['roadmap_completion'] = await self._get_roadmap_completion(user.id)
                metadata['assessments_completed'] = await self._get_assessments_completed(user.id)
            
            scored_users.append({
                'user_id': str(user.id),
                'display_name': user.get_full_name(),
                'score': score,
                'metadata': metadata,
                'profile_picture_url': user.profile.profile_picture_url
            })
        
        return scored_users
    
    async def _get_assessment_score(self, user_id: UUID) -> float:
        """Get assessment-based score for user"""
        # This would calculate based on assessment performance
        # For now, return mock data
        return 75.0
    
    async def _get_assessment_count(self, user_id: UUID) -> int:
        """Get number of assessments taken by user"""
        # This would query assessment repository
        return 10  # Mock data
    
    async def _get_average_assessment_score(self, user_id: UUID) -> float:
        """Get average assessment score for user"""
        return 78.5  # Mock data
    
    async def _get_skill_mastery_score(self, user_id: UUID) -> float:
        """Get skill mastery score for user"""
        # Calculate based on skills mastered and their levels
        return 65.0  # Mock data
    
    async def _get_skills_mastered_count(self, user_id: UUID) -> int:
        """Get count of skills mastered by user"""
        return 8  # Mock data
    
    async def _get_total_skills_count(self, user_id: UUID) -> int:
        """Get total skills count for user"""
        return 12  # Mock data
    
    async def _get_readiness_score(self, user_id: UUID) -> float:
        """Get readiness score for user"""
        # This would calculate based on target roles
        return 82.0  # Mock data
    
    async def _get_target_roles(self, user_id: UUID) -> List[str]:
        """Get target roles for user"""
        return ["Full Stack Developer", "Data Scientist"]  # Mock data
    
    async def _get_study_time_score(self, user_id: UUID) -> float:
        """Get study time-based score for user"""
        # Score based on total study hours
        return 70.0  # Mock data
    
    async def _get_total_study_hours(self, user_id: UUID) -> int:
        """Get total study hours for user"""
        return 120  # Mock data
    
    async def _get_current_streak(self, user_id: UUID) -> int:
        """Get current study streak for user"""
        return 15  # Mock data
    
    async def _get_completion_rate_score(self, user_id: UUID) -> float:
        """Get completion rate score for user"""
        return 85.0  # Mock data
    
    async def _get_roadmap_completion(self, user_id: UUID) -> float:
        """Get roadmap completion percentage for user"""
        return 75.0  # Mock data
    
    async def _get_assessments_completed(self, user_id: UUID) -> int:
        """Get number of assessments completed by user"""
        return 8  # Mock data


class UserDiscoveryUseCase:
    """Use case for user discovery and filtering"""
    
    def __init__(
        self,
        user_repository: UserRepository
    ):
        self.user_repository = user_repository
    
    async def discover_users(self, request: UserDiscoveryRequest) -> UserDiscoveryResponse:
        """Discover users based on criteria"""
        try:
            # Get users based on type and filters
            users = await self._get_filtered_users(request.filters, request.user_type)
            
            # Apply search if provided
            if request.search:
                users = await self._search_users(users, request.search)
            
            # Paginate results
            total_count = len(users)
            paginated_users = users[request.skip:request.skip + request.limit]
            
            # Convert to response format
            user_list = []
            for user in paginated_users:
                user_data = {
                    "user_id": str(user.id),
                    "display_name": user.get_full_name(),
                    "email": user.email,
                    "profile_picture_url": user.profile.profile_picture_url,
                    "role": user.role.value,
                    "profile": {
                        "years_of_experience": user.profile.years_of_experience,
                        "domain": user.profile.domain,
                        "city": user.profile.city,
                        "country": user.profile.country,
                        "bio": user.profile.bio,
                        "linkedin_url": user.profile.linkedin_url,
                        "github_url": user.profile.github_url
                    }
                }
                
                # Add interviewer-specific data if applicable
                if user.is_interviewer() and user.interviewer_profile:
                    user_data["interviewer_profile"] = {
                        "company": user.interviewer_profile.company,
                        "industry": user.interviewer_profile.industry,
                        "current_role": user.interviewer_profile.current_role,
                        "experience_years": user.interviewer_profile.experience_years,
                        "interview_experience_years": user.interviewer_profile.interview_experience_years,
                        "specializations": user.interviewer_profile.specializations,
                        "availability": user.interviewer_profile.availability,
                        "rating": user.interviewer_profile.rating,
                        "total_interviews": user.interviewer_profile.total_interviews
                    }
                
                user_list.append(user_data)
            
            return UserDiscoveryResponse(
                users=user_list,
                total_count=total_count,
                user_type=request.user_type,
                filters_applied=request.filters
            )
            
        except Exception as e:
            raise ValueError(f"Failed to discover users: {str(e)}")
    
    async def _get_filtered_users(self, filters: Dict[str, Any], user_type: str = "candidate") -> List[User]:
        """Get users based on filters"""
        query_params = {}
        
        # Apply filters
        if 'skills' in filters:
            query_params['skills'] = filters['skills']
        if 'domain' in filters:
            query_params['domain'] = filters['domain']
        if 'role' in filters:
            query_params['role'] = filters['role']
        if 'city' in filters:
            query_params['city'] = filters['city']
        if 'country' in filters:
            query_params['country'] = filters['country']
        if 'years_of_experience' in filters:
            query_params['years_of_experience'] = filters['years_of_experience']
        if 'min_rating' in filters:
            query_params['min_rating'] = filters['min_rating']
        
        # Get users by role
        if user_type == "candidate":
            users = await self.user_repository.list_by_role(UserRole.CANDIDATE, **query_params)
        elif user_type == "interviewer":
            users = await self.user_repository.list_by_role(UserRole.INTERVIEWER, **query_params)
        else:
            users = await self.user_repository.list_by_role(UserRole.CANDIDATE, **query_params)
        
        return users
    
    async def _search_users(self, users: List[User], search_term: str) -> List[User]:
        """Search users by name or skills"""
        search_term_lower = search_term.lower()
        filtered_users = []
        
        for user in users:
            # Search in name
            if search_term_lower in user.get_full_name().lower():
                filtered_users.append(user)
                continue
            
            # Search in skills (this would need to query user's skills)
            # For now, skip skill search
            # if search_term_lower in user.skills:
            #     filtered_users.append(user)
        
        return filtered_users


class DynamicFilterUseCase:
    """Use case for dynamic filter management"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        analytics_repository: AnalyticsRepository
    ):
        self.user_repository = user_repository
        self.analytics_repository = analytics_repository
    
    async def get_available_filters(self, user_type: str = "candidate") -> Dict[str, List[str]]:
        """Get available filter options based on existing data"""
        try:
            filters = {
                "skills": await self._get_available_skills(),
                "domains": await self._get_available_domains(),
                "roles": await self._get_available_roles(),
                "cities": await self._get_available_cities(),
                "countries": await self._get_available_countries(),
                "experience_levels": ["0-1", "1-3", "3-5", "5-10", "10+"]
            }
            
            # Add interviewer-specific filters
            if user_type == "interviewer":
                filters.update({
                    "industries": await self._get_available_industries(),
                    "companies": await self._get_available_companies(),
                    "availability": ["immediate", "this_week", "next_week", "this_month"]
                })
            
            return filters
            
        except Exception as e:
            raise ValueError(f"Failed to get available filters: {str(e)}")
    
    async def _get_available_skills(self) -> List[str]:
        """Get list of available skills from user data"""
        # This would query all unique skills from user profiles
        return [
            "Python", "JavaScript", "React", "Node.js", "SQL", "MongoDB",
            "AWS", "Docker", "Kubernetes", "Git", "TypeScript",
            "Java", "Spring Boot", "Microservices", "DevOps",
            "Machine Learning", "Data Science", "Analytics"
        ]
    
    async def _get_available_domains(self) -> List[str]:
        """Get list of available domains"""
        return [
            "Technology", "Finance", "Healthcare", "E-commerce",
            "Education", "Manufacturing", "Retail", "Consulting",
            "Government", "Non-profit", "Startup"
        ]
    
    async def _get_available_roles(self) -> List[str]:
        """Get list of available roles"""
        return [
            "Full Stack Developer", "Frontend Developer", "Backend Developer",
            "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
            "Software Architect", "Technical Lead", "Engineering Manager",
            "Product Manager", "UX Designer", "UI Designer"
        ]
    
    async def _get_available_cities(self) -> List[str]:
        """Get list of available cities"""
        return [
            "New York", "San Francisco", "London", "Paris", "Tokyo",
            "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai",
            "Singapore", "Sydney", "Melbourne", "Toronto", "Vancouver"
        ]
    
    async def _get_available_countries(self) -> List[str]:
        """Get list of available countries"""
        return [
            "United States", "United Kingdom", "Canada", "Australia",
            "India", "Singapore", "Germany", "France",
            "Japan", "China", "Brazil", "Mexico"
        ]
    
    async def _get_available_industries(self) -> List[str]:
        """Get list of available industries for interviewers"""
        return [
            "Technology", "Finance", "Healthcare", "E-commerce",
            "Education", "Manufacturing", "Retail", "Consulting",
            "Government", "Non-profit", "Startup"
        ]
    
    async def _get_available_companies(self) -> List[str]:
        """Get list of available companies for interviewers"""
        return [
            "Google", "Microsoft", "Amazon", "Apple", "Meta",
            "Netflix", "Tesla", "Spotify", "Airbnb", "Uber"
        ]
