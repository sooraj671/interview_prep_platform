"""
Interview Simulation Use Case
Handles interactive interview simulation with stress mode
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from domain.entities.assessment import Assessment, AssessmentStatus
from domain.services.prompt_service import PromptService
from application.interfaces.repositories import AssessmentRepository, UserRepository
from shared.exceptions.domain_exceptions import AssessmentTimeoutException


class InterviewSimulationRequest:
    """Interview simulation request data"""
    def __init__(
        self,
        user_id: UUID,
        roadmap_id: UUID,
        simulation_type: str = "technical",
        stress_mode: bool = False,
        duration_minutes: int = 60,
        follow_up_depth: str = "medium"
    ):
        self.user_id = user_id
        self.roadmap_id = roadmap_id
        self.simulation_type = simulation_type
        self.stress_mode = stress_mode
        self.duration_minutes = duration_minutes
        self.follow_up_depth = follow_up_depth


class InterviewSimulationResponse:
    """Interview simulation response data"""
    def __init__(
        self,
        simulation_id: UUID,
        questions: List[Dict[str, Any]],
        time_limit: int,
        stress_mode_enabled: bool,
        started_at: datetime
    ):
        self.simulation_id = simulation_id
        self.questions = questions
        self.time_limit = time_limit
        self.stress_mode_enabled = stress_mode_enabled
        self.started_at = started_at


class SimulationQuestion:
    """Simulation question with follow-up capabilities"""
    def __init__(
        self,
        id: UUID,
        question: str,
        question_type: str,
        difficulty: str,
        time_limit: int,
        follow_ups: List[Dict[str, Any]],
        stress_elements: List[str]
    ):
        self.id = id
        self.question = question
        self.question_type = question_type
        self.difficulty = difficulty
        self.time_limit = time_limit
        self.follow_ups = follow_ups
        self.stress_elements = stress_elements
        self.current_follow_up_index = 0
        self.responses = []


class InterviewSimulationUseCase:
    """Use case for interview simulation"""
    
    def __init__(
        self,
        assessment_repository: AssessmentRepository,
        user_repository: UserRepository,
        prompt_service: PromptService,
        llm_client: Any
    ):
        self.assessment_repository = assessment_repository
        self.user_repository = user_repository
        self.prompt_service = prompt_service
        self.llm_client = llm_client
    
    async def execute(self, request: InterviewSimulationRequest) -> InterviewSimulationResponse:
        """Execute interview simulation use case"""
        try:
            # Check user's roadmap completion percentage
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise ValueError(f"User not found: {request.user_id}")
            
            # Check if user has sufficient roadmap completion
            completion_percentage = await self._get_roadmap_completion(request.user_id, request.roadmap_id)
            if completion_percentage < 30:
                raise ValueError("User must complete at least 30% of roadmap to access simulation")
            
            # Generate simulation questions
            questions = await self._generate_simulation_questions(request)
            
            # Create simulation assessment
            simulation = await self._create_simulation_assessment(request, questions)
            
            return InterviewSimulationResponse(
                simulation_id=simulation.id,
                questions=[
                    {
                        "id": str(q.id),
                        "question": q.question,
                        "type": q.question_type,
                        "difficulty": q.difficulty,
                        "time_limit": q.time_limit,
                        "follow_ups": q.follow_ups,
                        "stress_elements": q.stress_elements
                    }
                    for q in questions
                ],
                time_limit=request.duration_minutes * 60,
                stress_mode_enabled=request.stress_mode,
                started_at=datetime.utcnow()
            )
            
        except Exception as e:
            raise ValueError(f"Failed to start interview simulation: {str(e)}")
    
    async def _get_roadmap_completion(self, user_id: UUID, roadmap_id: UUID) -> float:
        """Get user's roadmap completion percentage"""
        # This would query the user's roadmap completion
        # For now, return mock data
        return 50.0  # Assume 50% completion for demo
    
    async def _generate_simulation_questions(self, request: InterviewSimulationRequest) -> List[SimulationQuestion]:
        """Generate interview simulation questions"""
        # Get user's skills and experience
        user_skills = await self._get_user_skills(request.user_id)
        user_experience = await self._get_user_experience(request.user_id)
        
        # Generate questions using AI
        questions_data = await self._generate_ai_simulation_questions(
            request, user_skills, user_experience
        )
        
        # Convert to SimulationQuestion entities
        questions = []
        for i, question_data in enumerate(questions_data):
            question = SimulationQuestion(
                id=UUID(),
                question=question_data['question'],
                question_type=question_data['question_type'],
                difficulty=question_data['difficulty'],
                time_limit=question_data.get('time_limit', 300),  # 5 minutes default
                follow_ups=question_data.get('follow_up_questions', []),
                stress_elements=question_data.get('stress_elements', [])
            )
            questions.append(question)
        
        return questions
    
    async def _get_user_skills(self, user_id: UUID) -> List[str]:
        """Get user's skills"""
        # This would query user's skill assessments
        return ["Python", "JavaScript", "React", "SQL"]  # Mock data
    
    async def _get_user_experience(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's experience information"""
        user = await self.user_repository.get_by_id(user_id)
        return {
            "years_of_experience": user.profile.years_of_experience or 0,
            "level": "intermediate",
            "domain": user.profile.domain or "technology"
        }
    
    async def _generate_ai_simulation_questions(
        self, 
        request: InterviewSimulationRequest, 
        user_skills: List[str], 
        user_experience: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate simulation questions using AI"""
        # Render prompt
        prompt_data = self.prompt_service.render_interview_simulation_prompt(
            target_role="",  # Would come from user's roadmap
            experience_level=user_experience.get('level', 'intermediate'),
            candidate_skills=", ".join(user_skills),
            company_type="technology",
            interview_focus=request.simulation_type,
            duration=request.duration_minutes,
            difficulty_level="intermediate",
            stress_mode=request.stress_mode,
            follow_up_depth=request.follow_up_depth,
            interview_structure="technical_behavioral"
        )
        
        # Generate questions using LLM
        from src.infrastructure.ai.llm_client import LLMRequest
        llm_request = LLMRequest(
            system_prompt=prompt_data['system_prompt'],
            user_prompt=prompt_data['user_prompt'],
            max_tokens=1500,
            temperature=0.8 if request.stress_mode else 0.6
        )
        
        response = await self.llm_client.generate_structured(
            request=llm_request,
            schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "question_type": {"type": "string"},
                        "difficulty": {"type": "string"},
                        "time_limit": {"type": "integer"},
                        "follow_up_questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "purpose": {"type": "string"},
                                    "difficulty": {"type": "string"}
                                }
                            }
                        },
                        "stress_elements": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        )
        
        return response
    
    async def _create_simulation_assessment(self, request: InterviewSimulationRequest, questions: List[SimulationQuestion]) -> Assessment:
        """Create assessment for simulation"""
        # Convert SimulationQuestion to AssessmentQuestion
        assessment_questions = []
        for sim_question in questions:
            # This would convert to proper AssessmentQuestion entities
            # For now, create a basic structure
            assessment_questions.append({
                "id": sim_question.id,
                "type": sim_question.question_type,
                "title": f"Interview Question",
                "description": sim_question.question,
                "difficulty": sim_question.difficulty,
                "estimated_time": sim_question.time_limit // 60,  # Convert to minutes
                "points": 100,
                "question": sim_question.question
            })
        
        # Create assessment
        assessment = Assessment(
            title=f"Interview Simulation - {request.simulation_type.title()}",
            assessment_type=AssessmentType.SIMULATION,
            skill_ids=[],  # Would be derived from roadmap
            difficulty="intermediate",
            duration_minutes=request.duration_minutes,
            questions=assessment_questions,
            user_id=request.user_id,
            roadmap_id=request.roadmap_id,
            adaptive_difficulty=True,
            allow_hints=False,  # No hints in simulation
            allow_review=False,
            randomize_questions=True,
            passing_score=70,
            max_attempts=1,  # Single attempt for simulation
            time_limit_per_question=None
        )
        
        return assessment


class SimulationInteractionUseCase:
    """Use case for handling simulation interactions"""
    
    def __init__(
        self,
        assessment_repository: AssessmentRepository,
        prompt_service: PromptService,
        llm_client: Any
    ):
        self.assessment_repository = assessment_repository
        self.prompt_service = prompt_service
        self.llm_client = llm_client
    
    async def submit_answer(
        self, 
        assessment_id: UUID, 
        question_id: UUID, 
        answer: str, 
        time_taken: int
    ) -> Dict[str, Any]:
        """Submit answer to simulation question"""
        try:
            # Get assessment
            assessment = await self.assessment_repository.get_by_id(assessment_id)
            if not assessment:
                raise ValueError(f"Assessment not found: {assessment_id}")
            
            # Check if assessment is still active
            if assessment.status != AssessmentStatus.IN_PROGRESS:
                raise ValueError("Simulation is not active")
            
            # Check if assessment has expired
            if assessment.is_expired():
                assessment.status = AssessmentStatus.EXPIRED
                await self.assessment_repository.update(assessment)
                raise AssessmentTimeoutException(assessment_id, assessment.duration_minutes)
            
            # Submit response
            assessment.submit_response(question_id, answer, time_taken)
            await self.assessment_repository.update(assessment)
            
            # Generate AI feedback
            feedback = await self._generate_feedback(assessment, question_id, answer)
            
            # Check if stress mode requires follow-up
            follow_up = await self._check_follow_up_needed(assessment, question_id, answer)
            
            return {
                "feedback": feedback,
                "follow_up_question": follow_up,
                "question_completed": not follow_up,
                "assessment_progress": assessment.get_completion_percentage()
            }
            
        except Exception as e:
            raise ValueError(f"Failed to submit answer: {str(e)}")
    
    async def _generate_feedback(self, assessment: Assessment, question_id: UUID, answer: str) -> Dict[str, Any]:
        """Generate AI feedback for answer"""
        # Get question details
        question = assessment.get_question_by_id(question_id)
        if not question:
            raise ValueError(f"Question not found: {question_id}")
        
        # Render feedback prompt
        prompt_data = self.prompt_service.render_prompt(
            category="simulation",
            name="interview_feedback",
            question_details=question.to_dict(),
            user_answer=answer,
            time_spent=assessment.calculate_time_spent()
        )
        
        # Generate feedback using LLM
        from src.infrastructure.ai.llm_client import LLMRequest
        llm_request = LLMRequest(
            system_prompt=prompt_data['system_prompt'],
            user_prompt=prompt_data['user_prompt'],
            max_tokens=1000,
            temperature=0.7
        )
        
        response = await self.llm_client.generate_text(llm_request)
        
        return {
            "feedback": response.content,
            "score": self._calculate_answer_score(response.content),
            "improvement_suggestions": self._extract_improvements(response.content)
        }
    
    async def _check_follow_up_needed(self, assessment: Assessment, question_id: UUID, answer: str) -> Optional[Dict[str, Any]]:
        """Check if follow-up question is needed"""
        # This would analyze the answer and determine if a follow-up is needed
        # For now, return mock data
        return {
            "question": "Why do you think this answer is correct?",
            "reason": "Answer was too brief, needs more depth"
        }
    
    def _calculate_answer_score(self, feedback: str) -> int:
        """Calculate score from feedback"""
        # This would parse the AI feedback to extract a score
        # For now, return a mock score
        return 75
    
    def _extract_improvements(self, feedback: str) -> List[str]:
        """Extract improvement suggestions from feedback"""
        # This would parse the AI feedback to extract suggestions
        # For now, return mock suggestions
        return [
            "Provide more specific examples",
            "Consider edge cases",
            "Explain your reasoning process"
        ]


class StudyModeUseCase:
    """Use case for chat-based study mode"""
    
    def __init__(
        self,
        prompt_service: PromptService,
        llm_client: Any
    ):
        self.prompt_service = prompt_service
        self.llm_client = llm_client
    
    async def start_study_session(
        self,
        user_id: UUID,
        topic_name: str,
        user_level: str = "intermediate",
        target_role: str = "",
        prior_knowledge: str = "",
        learning_goals: str = "",
        time_available: str = ""
    ) -> Dict[str, Any]:
        """Start a study session for a specific topic"""
        try:
            # Get topic details from roadmap or skills
            topic_details = await self._get_topic_details(topic_name)
            
            # Generate initial tutoring prompt
            prompt_data = self.prompt_service.render_study_mode_prompt(
                topic_name=topic_name,
                student_level=user_level,
                target_role=target_role,
                prior_knowledge=prior_knowledge,
                learning_goals=learning_goals,
                time_available=time_available,
                topic_details=topic_details
            )
            
            # Generate AI response
            from src.infrastructure.ai.llm_client import LLMRequest
            llm_request = LLMRequest(
                system_prompt=prompt_data['system_prompt'],
                user_prompt=prompt_data['user_prompt'],
                max_tokens=1000,
                temperature=0.6
            )
            
            response = await self.llm_client.generate_text(llm_request)
            
            return {
                "session_id": UUID(),
                "topic": topic_name,
                "initial_message": response.content,
                "interaction_type": "assessment",
                "started_at": datetime.utcnow()
            }
            
        except Exception as e:
            raise ValueError(f"Failed to start study session: {str(e)}")
    
    async def continue_study_session(
        self,
        session_id: UUID,
        user_input: str
    ) -> Dict[str, Any]:
        """Continue study session with user input"""
        try:
            # Generate response to user input
            from src.infrastructure.ai.llm_client import LLMRequest
            llm_request = LLMRequest(
                system_prompt="You are a helpful tutor. Respond to the user's input appropriately.",
                user_prompt=user_input,
                max_tokens=1000,
                temperature=0.7
            )
            
            response = await self.llm_client.generate_text(llm_request)
            
            return {
                "response": response.content,
                "interaction_type": "tutoring",
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            raise ValueError(f"Failed to continue study session: {str(e)}")
    
    async def _get_topic_details(self, topic_name: str) -> str:
        """Get details about a topic"""
        # This would query the roadmap or skills database
        # For now, return mock details
        return f"Topic: {topic_name}\nDescription: This is a technical topic covering fundamental concepts and practical applications."
    
    async def generate_practice_exercises(self, topic_name: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate practice exercises for a topic"""
        # Generate exercises using AI
        prompt_data = self.prompt_service.render_prompt(
            category="simulation",
            name="practice_exercises",
            topic_name=topic_name,
            difficulty=difficulty
        )
        
        # Mock exercises
        return [
            {
                "type": "coding",
                "title": f"Implement {topic_name} concept",
                "description": "Write code to demonstrate your understanding",
                "estimated_time": 30
            },
            {
                "type": "quiz",
                "title": f"{topic_name} Quiz",
                "description": "Test your knowledge with multiple choice questions",
                "estimated_time": 15
            }
        ]
