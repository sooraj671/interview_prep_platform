"""
Assessment Generation Use Case
Generates adaptive assessment questions for skills
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from domain.entities.assessment import Assessment, AssessmentType, QuestionType, QuestionDifficulty, AssessmentQuestion
from domain.entities.skill import Skill
from domain.services.prompt_service import PromptService
from application.interfaces.repositories import AssessmentRepository, SkillRepository


class AssessmentGenerationRequest:
    """Assessment generation request data"""
    def __init__(
        self,
        user_id: UUID,
        skill_ids: List[str],
        assessment_type: str = "technical",
        difficulty: str = "intermediate",
        question_count: int = 20,
        time_limit_minutes: int = 60,
        question_types: Optional[List[str]] = None
    ):
        self.user_id = user_id
        self.skill_ids = skill_ids
        self.assessment_type = assessment_type
        self.difficulty = difficulty
        self.question_count = question_count
        self.time_limit_minutes = time_limit_minutes
        self.question_types = question_types or ["multiple_choice", "theoretical", "coding"]


class AssessmentGenerationResponse:
    """Assessment generation response data"""
    def __init__(
        self,
        assessment: Assessment,
        total_questions: int,
        estimated_time: int,
        difficulty_distribution: Dict[str, int]
    ):
        self.assessment = assessment
        self.total_questions = total_questions
        self.estimated_time = estimated_time
        self.difficulty_distribution = difficulty_distribution
        self.generated_at = datetime.utcnow()


class AssessmentGenerationUseCase:
    """Use case for generating adaptive assessments"""
    
    def __init__(
        self,
        assessment_repository: AssessmentRepository,
        skill_repository: SkillRepository,
        prompt_service: PromptService,
        llm_client: Any
    ):
        self.assessment_repository = assessment_repository
        self.skill_repository = skill_repository
        self.prompt_service = prompt_service
        self.llm_client = llm_client
    
    async def execute(self, request: AssessmentGenerationRequest) -> AssessmentGenerationResponse:
        """Execute assessment generation use case"""
        try:
            # Get skills information
            skills = await self._get_skills(request.skill_ids)
            
            # Determine user's current level for these skills
            user_levels = await self._get_user_skill_levels(request.user_id, skills)
            
            # Generate questions using AI
            questions = await self._generate_questions(request, skills, user_levels)
            
            # Create assessment entity
            assessment = await self._create_assessment(request, questions)
            
            # Calculate statistics
            stats = await self._calculate_assessment_stats(questions)
            
            # Save assessment
            saved_assessment = await self.assessment_repository.create(assessment)
            
            return AssessmentGenerationResponse(
                assessment=saved_assessment,
                total_questions=len(questions),
                estimated_time=stats['estimated_time'],
                difficulty_distribution=stats['difficulty_distribution']
            )
            
        except Exception as e:
            raise ValueError(f"Failed to generate assessment: {str(e)}")
    
    async def _get_skills(self, skill_ids: List[str]) -> List[Skill]:
        """Get skill information"""
        skills = []
        for skill_id in skill_ids:
            skill = await self.skill_repository.get_by_id(UUID(skill_id))
            if skill:
                skills.append(skill)
        return skills
    
    async def _get_user_skill_levels(self, user_id: UUID, skills: List[Skill]) -> Dict[str, int]:
        """Get user's current levels for the skills"""
        # This would typically query user's assessment history or self-assessments
        # For now, return mock data
        user_levels = {}
        for skill in skills:
            # Mock user level - in real implementation, this would come from user's profile
            user_levels[skill.name] = 5  # Mid-level on 1-10 scale
        return user_levels
    
    async def _generate_questions(
        self, 
        request: AssessmentGenerationRequest, 
        skills: List[Skill], 
        user_levels: Dict[str, int]
    ) -> List[AssessmentQuestion]:
        """Generate questions using AI service"""
        all_questions = []
        
        for skill in skills:
            # Generate questions for this skill
            skill_questions = await self._generate_skill_questions(
                request, skill, user_levels.get(skill.name, 5)
            )
            all_questions.extend(skill_questions)
        
        # Limit to requested question count
        if len(all_questions) > request.question_count:
            all_questions = all_questions[:request.question_count]
        
        return all_questions
    
    async def _generate_skill_questions(
        self, 
        request: AssessmentGenerationRequest, 
        skill: Skill, 
        user_level: int
    ) -> List[AssessmentQuestion]:
        """Generate questions for a specific skill"""
        # Calculate questions per skill
        questions_per_skill = max(1, request.question_count // len(request.skill_ids))
        
        # Render prompt
        prompt_data = self.prompt_service.render_assessment_generation_prompt(
            question_count=questions_per_skill,
            skill_name=skill.name,
            skill_category=skill.category.value,
            difficulty_level=request.difficulty,
            user_level=user_level,
            target_level=8,  # Target level for assessment
            target_role="",  # Would come from user's roadmap
            experience_level="intermediate",
            time_limit=request.time_limit_minutes,
            question_types=", ".join(request.question_types),
            avg_time_per_question=request.time_limit_minutes * 60 // questions_per_skill
        )
        
        # Generate questions using LLM
        from src.infrastructure.ai.llm_client import LLMRequest
        llm_request = LLMRequest(
            system_prompt=prompt_data['system_prompt'],
            user_prompt=prompt_data['user_prompt'],
            max_tokens=2000,
            temperature=0.3  # Lower temperature for assessments
        )
        
        response = await self.llm_client.generate_structured(
            request=llm_request,
            schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "difficulty": {"type": "string"},
                        "estimated_time": {"type": "integer"},
                        "points": {"type": "integer"},
                        "prerequisites": {"type": "array", "items": {"type": "string"}},
                        "learning_objectives": {"type": "array", "items": {"type": "string"}},
                        "question": {"type": "string"},
                        "options": {"type": "array", "items": {"type": "string"}},
                        "correct_answer": {"type": "string"},
                        "expected_answer_format": {"type": "string"},
                        "code_template": {"type": "string"},
                        "constraints": {"type": "array", "items": {"type": "string"}},
                        "evaluation_criteria": {"type": "array", "items": {"type": "object"}},
                        "hints": {"type": "array", "items": {"type": "object"}},
                        "explanation": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        )
        
        # Convert to AssessmentQuestion entities
        questions = []
        for question_data in response:
            question = AssessmentQuestion(
                type=QuestionType(question_data['type']),
                title=question_data['title'],
                description=question_data['description'],
                difficulty=QuestionDifficulty(question_data['difficulty']),
                estimated_time=question_data['estimated_time'],
                points=question_data['points'],
                prerequisites=question_data.get('prerequisites', []),
                learning_objectives=question_data.get('learning_objectives', []),
                question=question_data['question'],
                options=[
                    {"id": str(i), "text": opt, "is_correct": False, "explanation": ""}
                    for i, opt in enumerate(question_data.get('options', []))
                ],
                correct_answer=question_data.get('correct_answer', ''),
                expected_answer_format=question_data.get('expected_answer_format', ''),
                code_template=question_data.get('code_template', ''),
                constraints=question_data.get('constraints', []),
                evaluation_criteria=[
                    {
                        "aspect": criteria.get('aspect', 'correctness'),
                        "weight": criteria.get('weight', 100),
                        "description": criteria.get('description', '')
                    }
                    for criteria in question_data.get('evaluation_criteria', [])
                ],
                hints=[
                    {
                        "level": hint.get('level', 1),
                        "hint": hint.get('hint', ''),
                        "points_penalty": hint.get('points_penalty', 5)
                    }
                    for hint in question_data.get('hints', [])
                ],
                explanation=question_data.get('explanation', ''),
                tags=question_data.get('tags', [])
            )
            questions.append(question)
        
        return questions
    
    async def _create_assessment(self, request: AssessmentGenerationRequest, questions: List[AssessmentQuestion]) -> Assessment:
        """Create assessment entity"""
        assessment = Assessment(
            title=f"{request.assessment_type.title()} Assessment",
            assessment_type=AssessmentType(request.assessment_type),
            skill_ids=request.skill_ids,
            difficulty=request.difficulty,
            duration_minutes=request.time_limit_minutes,
            questions=questions,
            user_id=request.user_id,
            adaptive_difficulty=True,
            allow_hints=True,
            allow_review=True,
            randomize_questions=True,
            passing_score=70,
            max_attempts=3
        )
        
        return assessment
    
    async def _calculate_assessment_stats(self, questions: List[AssessmentQuestion]) -> Dict[str, Any]:
        """Calculate assessment statistics"""
        difficulty_distribution = {
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0,
            "expert": 0
        }
        
        total_time = 0
        for question in questions:
            difficulty_distribution[question.difficulty.value] += 1
            total_time += question.estimated_time
        
        return {
            "difficulty_distribution": difficulty_distribution,
            "estimated_time": total_time
        }


class AdaptiveAssessmentUseCase:
    """Use case for adaptive assessment during test taking"""
    
    def __init__(
        self,
        assessment_repository: AssessmentRepository,
        prompt_service: PromptService,
        llm_client: Any
    ):
        self.assessment_repository = assessment_repository
        self.prompt_service = prompt_service
        self.llm_client = llm_client
    
    async def get_next_question(
        self, 
        assessment_id: UUID, 
        previous_answers: List[Dict[str, Any]]
    ) -> Optional[AssessmentQuestion]:
        """Get next adaptive question based on previous answers"""
        assessment = await self.assessment_repository.get_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment not found: {assessment_id}")
        
        # Analyze performance
        performance_analysis = await self._analyze_performance(previous_answers)
        
        # Select next question
        next_question = await self._select_next_question(assessment, performance_analysis)
        
        return next_question
    
    async def _analyze_performance(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's performance on previous answers"""
        if not answers:
            return {"score": 0, "trend": "stable", "weak_areas": []}
        
        # Calculate average score
        scores = [answer.get('score', 0) for answer in answers]
        average_score = sum(scores) / len(scores)
        
        # Determine trend
        if len(scores) >= 3:
            recent_scores = scores[-3:]
            if recent_scores[-1] > recent_scores[0] + 10:
                trend = "improving"
            elif recent_scores[-1] < recent_scores[0] - 10:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Identify weak areas
        weak_areas = []
        for answer in answers:
            if answer.get('score', 0) < 60:
                weak_areas.append(answer.get('topic', 'general'))
        
        return {
            "score": average_score,
            "trend": trend,
            "weak_areas": weak_areas
        }
    
    async def _select_next_question(
        self, 
        assessment: Assessment, 
        performance: Dict[str, Any]
    ) -> Optional[AssessmentQuestion]:
        """Select next question based on performance"""
        unanswered_questions = assessment.get_unanswered_questions()
        
        if not unanswered_questions:
            return None
        
        # Simple adaptive logic - in real implementation, this would be more sophisticated
        if performance["score"] < 50:
            # User is struggling, provide easier question
            easier_questions = [
                q for q in unanswered_questions 
                if q.difficulty in [QuestionDifficulty.BEGINNER, QuestionDifficulty.INTERMEDIATE]
            ]
            return easier_questions[0] if easier_questions else unanswered_questions[0]
        elif performance["score"] > 80:
            # User is doing well, provide harder question
            harder_questions = [
                q for q in unanswered_questions 
                if q.difficulty in [QuestionDifficulty.ADVANCED, QuestionDifficulty.EXPERT]
            ]
            return harder_questions[0] if harder_questions else unanswered_questions[0]
        else:
            # User is doing moderately, provide similar difficulty
            return unanswered_questions[0]
