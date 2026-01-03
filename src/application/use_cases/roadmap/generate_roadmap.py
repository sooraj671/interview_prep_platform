"""
Roadmap Generation Use Case
Generates personalized learning roadmaps based on user profile and target role
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from domain.entities.user import User
from domain.entities.roadmap import Roadmap, RoadmapStatus, RoadmapTopic, RoadmapMilestone, SkillGap
from domain.services.prompt_service import PromptService
from application.interfaces.repositories import UserRepository, RoadmapRepository


class RoadmapGenerationRequest:
    """Roadmap generation request data"""
    def __init__(
        self,
        user_id: UUID,
        target_role: str,
        job_description: Optional[str] = None,
        current_skills: Optional[List[str]] = None,
        experience_level: Optional[str] = None,
        custom_requirements: Optional[Dict[str, Any]] = None,
        preserve_progress: Optional[List[UUID]] = None
    ):
        self.user_id = user_id
        self.target_role = target_role
        self.job_description = job_description
        self.current_skills = current_skills or []
        self.experience_level = experience_level
        self.custom_requirements = custom_requirements or {}
        self.preserve_progress = preserve_progress or []


class RoadmapGenerationResponse:
    """Roadmap generation response data"""
    def __init__(
        self,
        roadmap: Roadmap,
        skill_gaps: List[SkillGap],
        readiness_score: int,
        estimated_completion_weeks: int
    ):
        self.roadmap = roadmap
        self.skill_gaps = skill_gaps
        self.readiness_score = readiness_score
        self.estimated_completion_weeks = estimated_completion_weeks
        self.generated_at = datetime.utcnow()


class RoadmapGenerationUseCase:
    """Use case for generating personalized learning roadmaps"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        roadmap_repository: RoadmapRepository,
        prompt_service: PromptService,
        llm_client: Any  # Will be injected from infrastructure
    ):
        self.user_repository = user_repository
        self.roadmap_repository = roadmap_repository
        self.prompt_service = prompt_service
        self.llm_client = llm_client
    
    async def execute(self, request: RoadmapGenerationRequest) -> RoadmapGenerationResponse:
        """Execute roadmap generation use case"""
        try:
            # Get user information
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise ValueError(f"User not found: {request.user_id}")
            
            # Analyze user's current skills and experience
            user_profile = await self._analyze_user_profile(user, request)
            
            # Generate roadmap using AI
            roadmap_data = await self._generate_ai_roadmap(user_profile, request)
            
            # Create roadmap entity
            roadmap = await self._create_roadmap_entity(roadmap_data, request.user_id)
            
            # Handle progress preservation
            if request.preserve_progress:
                roadmap = await self._preserve_completed_topics(roadmap, request.preserve_progress)
            
            # Calculate skill gaps
            skill_gaps = await self._calculate_skill_gaps(user_profile, roadmap_data)
            
            # Calculate readiness score
            readiness_score = await self._calculate_readiness_score(user_profile, roadmap_data)
            
            # Save roadmap
            saved_roadmap = await self.roadmap_repository.create(roadmap)
            
            return RoadmapGenerationResponse(
                roadmap=saved_roadmap,
                skill_gaps=skill_gaps,
                readiness_score=readiness_score,
                estimated_completion_weeks=roadmap.estimated_duration_weeks
            )
            
        except Exception as e:
            raise ValueError(f"Failed to generate roadmap: {str(e)}")
    
    async def _analyze_user_profile(self, user: User, request: RoadmapGenerationRequest) -> Dict[str, Any]:
        """Analyze user's current profile and skills"""
        profile = {
            'user_id': str(user.id),
            'email': user.email,
            'first_name': user.profile.first_name,
            'last_name': user.profile.last_name,
            'years_of_experience': user.profile.years_of_experience or 0,
            'domain': user.profile.domain or '',
            'current_skills': request.current_skills,
            'experience_level': request.experience_level or 'intermediate',
            'resume_url': user.profile.resume_url,
            'contact_number': user.profile.phone,
            'profile_picture': user.profile.profile_picture_url
        }
        
        # Add skills from user's resume if available
        if user.profile.resume_url:
            # This would extract skills from stored resume data
            profile['resume_skills'] = []  # Would be populated from resume parsing
        
        return profile
    
    async def _generate_ai_roadmap(self, user_profile: Dict[str, Any], request: RoadmapGenerationRequest) -> Dict[str, Any]:
        """Generate roadmap using AI service"""
        # Prepare current skills text
        current_skills_text = ""
        if user_profile['current_skills']:
            current_skills_text = "\n".join([
                f"- {skill}" for skill in user_profile['current_skills']
            ])
        
        # Prepare additional information
        additional_info = ""
        if request.job_description:
            additional_info += f"\nJob Description:\n{request.job_description}"
        
        if request.custom_requirements:
            additional_info += f"\nCustom Requirements:\n{request.custom_requirements}"
        
        # Render prompt
        prompt_data = self.prompt_service.render_roadmap_generation_prompt(
            target_role=request.target_role,
            experience_level=user_profile['experience_level'],
            current_skills=current_skills_text,
            additional_info=additional_info
        )
        
        # Generate roadmap using LLM
        from src.infrastructure.ai.llm_client import LLMRequest
        llm_request = LLMRequest(
            system_prompt=prompt_data['system_prompt'],
            user_prompt=prompt_data['user_prompt'],
            max_tokens=2000,
            temperature=0.7
        )
        
        response = await self.llm_client.generate_structured(
            request=llm_request,
            schema={
                "title": "string",
                "description": "string",
                "estimated_duration_weeks": "integer",
                "difficulty_level": "string",
                "skill_gaps": [
                    {
                        "skill": "string",
                        "current_level": "integer",
                        "target_level": "integer",
                        "priority": "string",
                        "reasoning": "string"
                    }
                ],
                "topics": [
                    {
                        "title": "string",
                        "description": "string",
                        "difficulty": "string",
                        "estimated_hours": "integer",
                        "prerequisites": ["string"],
                        "learning_objectives": ["string"],
                        "content": "string",
                        "skills_covered": ["string"],
                        "practice_exercises": [
                            {
                                "type": "string",
                                "description": "string",
                                "estimated_time": "integer"
                            }
                        ],
                        "assessment_criteria": ["string"]
                    }
                ],
                "milestones": [
                    {
                        "title": "string",
                        "description": "string",
                        "week_number": "integer",
                        "skills_to_master": ["string"],
                        "assessment_type": "string"
                    }
                ],
                "resources": [
                    {
                        "type": "string",
                        "title": "string",
                        "url": "string",
                        "description": "string",
                        "difficulty": "string"
                    }
                ]
            }
        )
        
        return response
    
    async def _create_roadmap_entity(self, roadmap_data: Dict[str, Any], user_id: UUID) -> Roadmap:
        """Create roadmap entity from AI-generated data"""
        # Create topics
        topics = []
        for topic_data in roadmap_data.get('topics', []):
            topic = RoadmapTopic(
                title=topic_data['title'],
                description=topic_data['description'],
                difficulty=topic_data['difficulty'],
                estimated_hours=topic_data['estimated_hours'],
                prerequisites=topic_data.get('prerequisites', []),
                learning_objectives=topic_data.get('learning_objectives', []),
                content=topic_data.get('content', ''),
                skills_covered=topic_data.get('skills_covered', []),
                practice_exercises=[
                    {
                        'type': exercise['type'],
                        'title': exercise['description'],
                        'description': exercise['description'],
                        'estimated_time': exercise['estimated_time']
                    }
                    for exercise in topic_data.get('practice_exercises', [])
                ],
                assessment_criteria=topic_data.get('assessment_criteria', [])
            )
            topics.append(topic)
        
        # Create milestones
        milestones = []
        for milestone_data in roadmap_data.get('milestones', []):
            milestone = RoadmapMilestone(
                title=milestone_data['title'],
                description=milestone_data['description'],
                week_number=milestone_data['week_number'],
                skills_to_master=milestone_data.get('skills_to_master', []),
                assessment_type=milestone_data.get('assessment_type', 'quiz')
            )
            milestones.append(milestone)
        
        # Create skill gaps
        skill_gaps = []
        for gap_data in roadmap_data.get('skill_gaps', []):
            skill_gap = SkillGap(
                skill=gap_data['skill'],
                current_level=gap_data['current_level'],
                target_level=gap_data['target_level'],
                priority=gap_data['priority'],
                reasoning=gap_data.get('reasoning', '')
            )
            skill_gaps.append(skill_gap)
        
        # Create roadmap
        roadmap = Roadmap(
            title=roadmap_data['title'],
            target_role=request.target_role,
            description=roadmap_data['description'],
            estimated_duration_weeks=roadmap_data['estimated_duration_weeks'],
            difficulty_level=roadmap_data['difficulty_level'],
            topics=topics,
            milestones=milestones,
            skill_gaps=skill_gaps,
            resources=roadmap_data.get('resources', []),
            user_id=user_id,
            status=RoadmapStatus.NOT_STARTED
        )
        
        return roadmap
    
    async def _preserve_completed_topics(self, roadmap: Roadmap, completed_topic_ids: List[UUID]) -> Roadmap:
        """Preserve progress for completed topics when regenerating roadmap"""
        # This would check if the new roadmap contains topics that were completed
        # in the previous roadmap and mark them as completed
        
        for topic in roadmap.topics:
            if topic.id in completed_topic_ids:
                topic.status = RoadmapTopic.Status.COMPLETED
                topic.progress_percentage = 100
                topic.completed_at = datetime.utcnow()
        
        return roadmap
    
    async def _calculate_skill_gaps(self, user_profile: Dict[str, Any], roadmap_data: Dict[str, Any]) -> List[SkillGap]:
        """Calculate skill gaps between user profile and target role"""
        skill_gaps = []
        
        for gap_data in roadmap_data.get('skill_gaps', []):
            skill_gap = SkillGap(
                skill=gap_data['skill'],
                current_level=gap_data['current_level'],
                target_level=gap_data['target_level'],
                priority=gap_data['priority'],
                reasoning=gap_data.get('reasoning', '')
            )
            skill_gaps.append(skill_gap)
        
        return skill_gaps
    
    async def _calculate_readiness_score(self, user_profile: Dict[str, Any], roadmap_data: Dict[str, Any]) -> int:
        """Calculate readiness score for target role"""
        # Base score from experience
        experience_score = min(user_profile['years_of_experience'] * 10, 50)
        
        # Score from current skills
        skills_score = 0
        total_skills = len(roadmap_data.get('skill_gaps', []))
        if total_skills > 0:
            covered_skills = len(user_profile.get('current_skills', []))
            skills_score = (covered_skills / total_skills) * 30
        
        # Score from education and projects
        education_score = 20  # Base score for having education
        
        # Total readiness score
        readiness_score = min(experience_score + skills_score + education_score, 100)
        
        return int(readiness_score)


class RoadmapRegenerationUseCase:
    """Use case for regenerating existing roadmaps"""
    
    def __init__(
        self,
        roadmap_repository: RoadmapRepository,
        generation_use_case: RoadmapGenerationUseCase
    ):
        self.roadmap_repository = roadmap_repository
        self.generation_use_case = generation_use_case
    
    async def execute(self, user_id: UUID, roadmap_id: UUID, updates: Dict[str, Any]) -> RoadmapGenerationResponse:
        """Execute roadmap regeneration with progress preservation"""
        # Get existing roadmap
        existing_roadmap = await self.roadmap_repository.get_by_id(roadmap_id)
        if not existing_roadmap:
            raise ValueError(f"Roadmap not found: {roadmap_id}")
        
        # Get completed topics
        completed_topics = [
            topic.id for topic in existing_roadmap.topics 
            if topic.status == RoadmapTopic.Status.COMPLETED
        ]
        
        # Create regeneration request
        request = RoadmapGenerationRequest(
            user_id=user_id,
            target_role=updates.get('target_role', existing_roadmap.target_role),
            job_description=updates.get('job_description'),
            current_skills=updates.get('current_skills'),
            experience_level=updates.get('experience_level'),
            custom_requirements=updates.get('custom_requirements'),
            preserve_progress=completed_topics
        )
        
        # Generate new roadmap
        response = await self.generation_use_case.execute(request)
        
        # Archive old roadmap
        existing_roadmap.archive_roadmap()
        await self.roadmap_repository.update(existing_roadmap)
        
        return response
