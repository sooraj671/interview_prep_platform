"""
Assessment Domain Entity
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from dataclasses import dataclass, field


class AssessmentType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PROBLEM_SOLVING = "problem_solving"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    SITUATIONAL = "situational"
    MIXED = "mixed"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    THEORETICAL = "theoretical"
    CODING = "coding"
    DESIGN = "design"
    ESSAY = "essay"
    PRACTICAL = "practical"


class AssessmentStatus(str, Enum):
    CREATED = "created"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


class QuestionDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class QuestionOption:
    """Multiple choice question option"""
    id: str
    text: str
    is_correct: bool = False
    explanation: str = ""


@dataclass
class QuestionHint:
    """Question hint for adaptive assessment"""
    level: int  # 1-3, where 1 is most basic
    hint: str
    points_penalty: int = 5


@dataclass
class EvaluationCriteria:
    """Question evaluation criteria"""
    aspect: str
    weight: int  # percentage
    description: str


@dataclass
class AssessmentQuestion:
    """Assessment question"""
    id: UUID
    type: QuestionType
    title: str
    description: str
    difficulty: QuestionDifficulty
    estimated_time: int  # minutes
    points: int
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    question: str = ""
    options: List[QuestionOption] = field(default_factory=list)
    correct_answer: str = ""
    expected_answer_format: str = ""
    code_template: str = ""
    constraints: List[str] = field(default_factory=list)
    evaluation_criteria: List[EvaluationCriteria] = field(default_factory=list)
    hints: List[QuestionHint] = field(default_factory=list)
    explanation: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()


@dataclass
class QuestionResponse:
    """User's response to a question"""
    question_id: UUID
    answer: str
    time_taken: int  # seconds
    hints_used: List[int] = field(default_factory=list)
    attempts: int = 1
    submitted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QuestionEvaluation:
    """Evaluation of a question response"""
    question_id: UUID
    score: int  # 0-100
    correctness: int  # 0-100
    efficiency: int  # 0-100
    style: int  # 0-100
    completeness: int  # 0-100
    is_correct: bool = False
    feedback: str = ""
    detailed_analysis: Dict[str, str] = field(default_factory=dict)
    improvement_areas: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    encouragement: str = ""


@dataclass
class SkillAssessment:
    """Skill assessment result"""
    skill: str
    current_level: int  # 1-10
    target_level: int  # 1-10
    demonstrated_level: int  # 1-10
    confidence_level: str  # low, medium, high
    recommendations: List[str] = field(default_factory=list)


class Assessment:
    """Assessment domain entity"""
    
    def __init__(
        self,
        title: str,
        assessment_type: AssessmentType,
        skill_ids: List[str],
        difficulty: str = "intermediate",
        duration_minutes: int = 60,
        questions: Optional[List[AssessmentQuestion]] = None,
        user_id: Optional[UUID] = None,
        roadmap_id: Optional[UUID] = None,
        status: AssessmentStatus = AssessmentStatus.CREATED,
        responses: Optional[List[QuestionResponse]] = None,
        evaluations: Optional[List[QuestionEvaluation]] = None,
        skill_assessments: Optional[List[SkillAssessment]] = None,
        adaptive_difficulty: bool = True,
        allow_hints: bool = True,
        allow_review: bool = True,
        randomize_questions: bool = True,
        passing_score: int = 70,
        max_attempts: int = 3,
        time_limit_per_question: Optional[int] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        last_activity_at: Optional[datetime] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.title = title.strip()
        self.assessment_type = assessment_type
        self.skill_ids = skill_ids
        self.difficulty = difficulty
        self.duration_minutes = duration_minutes
        self.questions = questions or []
        self.user_id = user_id
        self.roadmap_id = roadmap_id
        self.status = status
        self.responses = responses or []
        self.evaluations = evaluations or []
        self.skill_assessments = skill_assessments or []
        self.adaptive_difficulty = adaptive_difficulty
        self.allow_hints = allow_hints
        self.allow_review = allow_review
        self.randomize_questions = randomize_questions
        self.passing_score = passing_score
        self.max_attempts = max_attempts
        self.time_limit_per_question = time_limit_per_question
        self.started_at = started_at
        self.completed_at = completed_at
        self.expires_at = expires_at
        self.last_activity_at = last_activity_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def start_assessment(self) -> None:
        """Start the assessment"""
        if self.status == AssessmentStatus.CREATED:
            self.status = AssessmentStatus.STARTED
            self.started_at = datetime.utcnow()
            self.last_activity_at = datetime.utcnow()
            
            # Set expiration if not already set
            if not self.expires_at:
                self.expires_at = self.started_at + timedelta(minutes=self.duration_minutes)
            
            self.updated_at = datetime.utcnow()
    
    def submit_response(self, question_id: UUID, answer: str, time_taken: int) -> None:
        """Submit a response to a question"""
        if self.status not in [AssessmentStatus.STARTED, AssessmentStatus.IN_PROGRESS]:
            raise ValueError("Assessment must be started to submit responses")
        
        # Check if assessment has expired
        if self.expires_at and datetime.utcnow() > self.expires_at:
            self.status = AssessmentStatus.EXPIRED
            raise ValueError("Assessment has expired")
        
        # Remove any existing response for this question
        self.responses = [r for r in self.responses if r.question_id != question_id]
        
        # Add new response
        response = QuestionResponse(
            question_id=question_id,
            answer=answer,
            time_taken=time_taken
        )
        self.responses.append(response)
        
        self.status = AssessmentStatus.IN_PROGRESS
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def use_hint(self, question_id: UUID, hint_level: int) -> None:
        """Use a hint for a question"""
        if not self.allow_hints:
            raise ValueError("Hints are not allowed for this assessment")
        
        # Find the question
        question = next((q for q in self.questions if q.id == question_id), None)
        if not question:
            raise ValueError("Question not found")
        
        # Find the hint
        hint = next((h for h in question.hints if h.level == hint_level), None)
        if not hint:
            raise ValueError("Hint not found")
        
        # Add hint to response
        for response in self.responses:
            if response.question_id == question_id:
                if hint_level not in response.hints_used:
                    response.hints_used.append(hint_level)
                break
        
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def complete_assessment(self) -> None:
        """Complete the assessment and trigger evaluation"""
        if self.status not in [AssessmentStatus.STARTED, AssessmentStatus.IN_PROGRESS]:
            raise ValueError("Assessment must be started to complete")
        
        self.status = AssessmentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def abandon_assessment(self) -> None:
        """Abandon the assessment"""
        self.status = AssessmentStatus.ABANDONED
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_question(self, question: AssessmentQuestion) -> None:
        """Add a question to the assessment"""
        if self.status != AssessmentStatus.CREATED:
            raise ValueError("Cannot add questions to started assessment")
        
        self.questions.append(question)
        self.updated_at = datetime.utcnow()
    
    def remove_question(self, question_id: UUID) -> None:
        """Remove a question from the assessment"""
        if self.status != AssessmentStatus.CREATED:
            raise ValueError("Cannot remove questions from started assessment")
        
        self.questions = [q for q in self.questions if q.id != question_id]
        self.updated_at = datetime.utcnow()
    
    def add_evaluation(self, evaluation: QuestionEvaluation) -> None:
        """Add an evaluation for a question"""
        # Remove any existing evaluation for this question
        self.evaluations = [e for e in self.evaluations if e.question_id != evaluation.question_id]
        self.evaluations.append(evaluation)
        self.updated_at = datetime.utcnow()
    
    def add_skill_assessment(self, skill_assessment: SkillAssessment) -> None:
        """Add a skill assessment result"""
        # Remove any existing assessment for this skill
        self.skill_assessments = [sa for sa in self.skill_assessments if sa.skill != skill_assessment.skill]
        self.skill_assessments.append(skill_assessment)
        self.updated_at = datetime.utcnow()
    
    def get_question_by_id(self, question_id: UUID) -> Optional[AssessmentQuestion]:
        """Get a question by ID"""
        return next((q for q in self.questions if q.id == question_id), None)
    
    def get_response_for_question(self, question_id: UUID) -> Optional[QuestionResponse]:
        """Get the response for a specific question"""
        return next((r for r in self.responses if r.question_id == question_id), None)
    
    def get_evaluation_for_question(self, question_id: UUID) -> Optional[QuestionEvaluation]:
        """Get the evaluation for a specific question"""
        return next((e for e in self.evaluations if e.question_id == question_id), None)
    
    def calculate_total_score(self) -> int:
        """Calculate the total score for the assessment"""
        if not self.evaluations:
            return 0
        
        total_points = sum(q.points for q in self.questions)
        earned_points = sum(e.score * q.points // 100 for q, e in zip(self.questions, self.evaluations))
        
        return (earned_points * 100) // total_points if total_points > 0 else 0
    
    def calculate_time_spent(self) -> int:
        """Calculate total time spent in seconds"""
        return sum(r.time_taken for r in self.responses)
    
    def get_average_question_time(self) -> float:
        """Get average time per question in seconds"""
        if not self.responses:
            return 0.0
        return self.calculate_time_spent() / len(self.responses)
    
    def get_hints_usage(self) -> Dict[str, int]:
        """Get hints usage statistics"""
        hints_count = {}
        for response in self.responses:
            for hint_level in response.hints_used:
                key = f"level_{hint_level}"
                hints_count[key] = hints_count.get(key, 0) + 1
        return hints_count
    
    def get_difficulty_distribution(self) -> Dict[str, int]:
        """Get distribution of questions by difficulty"""
        distribution = {difficulty.value: 0 for difficulty in QuestionDifficulty}
        for question in self.questions:
            distribution[question.difficulty.value] += 1
        return distribution
    
    def get_question_type_distribution(self) -> Dict[str, int]:
        """Get distribution of questions by type"""
        distribution = {qtype.value: 0 for qtype in QuestionType}
        for question in self.questions:
            distribution[question.type.value] += 1
        return distribution
    
    def is_passed(self) -> bool:
        """Check if the assessment is passed"""
        return self.calculate_total_score() >= self.passing_score
    
    def get_completion_percentage(self) -> int:
        """Get completion percentage based on responses"""
        if not self.questions:
            return 0
        return (len(self.responses) * 100) // len(self.questions)
    
    def is_expired(self) -> bool:
        """Check if the assessment has expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    def get_remaining_time(self) -> Optional[int]:
        """Get remaining time in seconds"""
        if not self.expires_at:
            return None
        
        remaining = self.expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))
    
    def get_next_question(self, current_question_id: Optional[UUID] = None) -> Optional[AssessmentQuestion]:
        """Get the next question in sequence"""
        if not self.questions:
            return None
        
        if current_question_id is None:
            return self.questions[0]
        
        try:
            current_index = next(i for i, q in enumerate(self.questions) if q.id == current_question_id)
            if current_index + 1 < len(self.questions):
                return self.questions[current_index + 1]
        except StopIteration:
            pass
        
        return None
    
    def get_unanswered_questions(self) -> List[AssessmentQuestion]:
        """Get questions that haven't been answered"""
        answered_question_ids = {r.question_id for r in self.responses}
        return [q for q in self.questions if q.id not in answered_question_ids]
    
    def get_answered_questions(self) -> List[AssessmentQuestion]:
        """Get questions that have been answered"""
        answered_question_ids = {r.question_id for r in self.responses}
        return [q for q in self.questions if q.id in answered_question_ids]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "assessment_type": self.assessment_type.value,
            "skill_ids": self.skill_ids,
            "difficulty": self.difficulty,
            "duration_minutes": self.duration_minutes,
            "status": self.status.value,
            "adaptive_difficulty": self.adaptive_difficulty,
            "allow_hints": self.allow_hints,
            "allow_review": self.allow_review,
            "randomize_questions": self.randomize_questions,
            "passing_score": self.passing_score,
            "max_attempts": self.max_attempts,
            "time_limit_per_question": self.time_limit_per_question,
            "user_id": str(self.user_id) if self.user_id else None,
            "roadmap_id": str(self.roadmap_id) if self.roadmap_id else None,
            "questions": [
                {
                    "id": str(question.id),
                    "type": question.type.value,
                    "title": question.title,
                    "description": question.description,
                    "difficulty": question.difficulty.value,
                    "estimated_time": question.estimated_time,
                    "points": question.points,
                    "prerequisites": question.prerequisites,
                    "learning_objectives": question.learning_objectives,
                    "question": question.question,
                    "options": [
                        {
                            "id": opt.id,
                            "text": opt.text,
                            "is_correct": opt.is_correct,
                            "explanation": opt.explanation
                        }
                        for opt in question.options
                    ],
                    "correct_answer": question.correct_answer,
                    "expected_answer_format": question.expected_answer_format,
                    "code_template": question.code_template,
                    "constraints": question.constraints,
                    "evaluation_criteria": [
                        {
                            "aspect": criteria.aspect,
                            "weight": criteria.weight,
                            "description": criteria.description
                        }
                        for criteria in question.evaluation_criteria
                    ],
                    "hints": [
                        {
                            "level": hint.level,
                            "hint": hint.hint,
                            "points_penalty": hint.points_penalty
                        }
                        for hint in question.hints
                    ],
                    "explanation": question.explanation,
                    "tags": question.tags,
                    "dependencies": question.dependencies
                }
                for question in self.questions
            ],
            "responses": [
                {
                    "question_id": str(response.question_id),
                    "answer": response.answer,
                    "time_taken": response.time_taken,
                    "hints_used": response.hints_used,
                    "attempts": response.attempts,
                    "submitted_at": response.submitted_at.isoformat()
                }
                for response in self.responses
            ],
            "evaluations": [
                {
                    "question_id": str(evaluation.question_id),
                    "score": evaluation.score,
                    "correctness": evaluation.correctness,
                    "efficiency": evaluation.efficiency,
                    "style": evaluation.style,
                    "completeness": evaluation.completeness,
                    "is_correct": evaluation.is_correct,
                    "feedback": evaluation.feedback,
                    "detailed_analysis": evaluation.detailed_analysis,
                    "improvement_areas": evaluation.improvement_areas,
                    "next_steps": evaluation.next_steps,
                    "encouragement": evaluation.encouragement
                }
                for evaluation in self.evaluations
            ],
            "skill_assessments": [
                {
                    "skill": assessment.skill,
                    "current_level": assessment.current_level,
                    "target_level": assessment.target_level,
                    "demonstrated_level": assessment.demonstrated_level,
                    "confidence_level": assessment.confidence_level,
                    "recommendations": assessment.recommendations
                }
                for assessment in self.skill_assessments
            ],
            "statistics": {
                "total_score": self.calculate_total_score(),
                "is_passed": self.is_passed(),
                "time_spent_seconds": self.calculate_time_spent(),
                "average_question_time": self.get_average_question_time(),
                "completion_percentage": self.get_completion_percentage(),
                "hints_usage": self.get_hints_usage(),
                "difficulty_distribution": self.get_difficulty_distribution(),
                "question_type_distribution": self.get_question_type_distribution(),
                "questions_answered": len(self.responses),
                "total_questions": len(self.questions),
                "remaining_time": self.get_remaining_time(),
                "is_expired": self.is_expired()
            },
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
