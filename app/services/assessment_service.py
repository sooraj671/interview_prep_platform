from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import uuid
from datetime import datetime, timedelta

from app.models.assessment import (
    Question, Assessment, AssessmentAnswer, 
    QuestionTypeEnum, SkillLevelEnum, AssessmentStatusEnum
)
from app.models.user import UserSkill
from app.schemas.assessment import (
    QuestionCreate, QuestionUpdate, AssessmentCreate, AssessmentUpdate,
    AssessmentAnswerCreate
)
from app.core.exceptions import NotFoundError, ValidationError
from app.ai.question_generator import QuestionGenerator
from app.ai.skill_analyzer import SkillAnalyzer

class AssessmentService:
    """Service for assessment and question management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.question_generator = QuestionGenerator()
        self.skill_analyzer = SkillAnalyzer()
    
    # Question methods
    def get_questions(self, skip: int = 0, limit: int = 100, skill_id: Optional[uuid.UUID] = None, 
                      difficulty: Optional[str] = None, question_type: Optional[str] = None) -> List[Question]:
        """Get questions with optional filtering."""
        query = self.db.query(Question).filter(Question.is_active == True)
        
        if skill_id:
            query = query.filter(Question.skill_id == skill_id)
        
        if difficulty:
            query = query.filter(Question.difficulty_level == difficulty)
        
        if question_type:
            query = query.filter(Question.question_type == question_type)
        
        return query.offset(skip).limit(limit).all()
    
    def get_question(self, question_id: uuid.UUID) -> Optional[Question]:
        """Get question by ID."""
        return self.db.query(Question).filter(Question.id == question_id).first()
    
    def create_question(self, question_create: QuestionCreate, created_by: uuid.UUID) -> Question:
        """Create a new question."""
        question = Question(
            **question_create.dict(),
            created_by=created_by
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question
    
    def update_question(self, question_id: uuid.UUID, question_update: QuestionUpdate, user_id: uuid.UUID) -> Optional[Question]:
        """Update question."""
        question = self.get_question(question_id)
        if not question:
            return None
        
        # Check if user created this question or is admin
        if question.created_by != user_id:
            from app.core.exceptions import AuthorizationError
            raise AuthorizationError("You can only update questions you created")
        
        update_data = question_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)
        
        self.db.commit()
        self.db.refresh(question)
        return question
    
    def delete_question(self, question_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete question (soft delete)."""
        question = self.get_question(question_id)
        if not question:
            return False
        
        # Check if user created this question or is admin
        if question.created_by != user_id:
            from app.core.exceptions import AuthorizationError
            raise AuthorizationError("You can only delete questions you created")
        
        question.is_active = False
        self.db.commit()
        return True
    
    # Assessment methods
    def get_user_assessments(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get user's assessments."""
        return self.db.query(Assessment).filter(Assessment.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_assessment(self, assessment_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Assessment]:
        """Get assessment by ID for a specific user."""
        return self.db.query(Assessment).filter(
            and_(Assessment.id == assessment_id, Assessment.user_id == user_id)
        ).first()
    
    async def create_assessment(self, user_id: uuid.UUID, assessment_create: AssessmentCreate) -> Assessment:
        """Create a new assessment."""
        assessment = Assessment(
            user_id=user_id,
            assessment_type=assessment_create.assessment_type,
            skill_id=assessment_create.skill_id,
            topic_id=assessment_create.topic_id,
            total_questions=assessment_create.question_count or 10
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        return assessment
    
    async def start_assessment(self, assessment_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Assessment]:
        """Start an assessment session."""
        assessment = self.get_assessment(assessment_id, user_id)
        if not assessment:
            return None
        
        if assessment.status != AssessmentStatusEnum.PENDING:
            raise ValidationError("Assessment has already been started")
        
        assessment.status = AssessmentStatusEnum.IN_PROGRESS
        assessment.started_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(assessment)
        
        return assessment
    
    async def submit_assessment(self, assessment_id: uuid.UUID, user_id: uuid.UUID, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit assessment answers and calculate results."""
        assessment = self.get_assessment(assessment_id, user_id)
        if not assessment:
            return None
        
        if assessment.status != AssessmentStatusEnum.IN_PROGRESS:
            raise ValidationError("Assessment is not in progress")
        
        # Process answers
        correct_count = 0
        total_time = 0
        processed_answers = []
        
        for answer_data in answers:
            question = self.get_question(answer_data["question_id"])
            if not question:
                continue
            
            is_correct = self._evaluate_answer(question, answer_data["answer"])
            if is_correct:
                correct_count += 1
            
            # Create assessment answer record
            assessment_answer = AssessmentAnswer(
                assessment_id=assessment_id,
                question_id=answer_data["question_id"],
                user_answer=answer_data["answer"],
                is_correct=is_correct,
                time_taken_seconds=answer_data.get("time_taken", 0),
                feedback=self._generate_feedback(question, is_correct)
            )
            
            self.db.add(assessment_answer)
            processed_answers.append(assessment_answer)
            total_time += answer_data.get("time_taken", 0)
        
        # Update assessment
        assessment.status = AssessmentStatusEnum.COMPLETED
        assessment.completed_at = datetime.utcnow()
        assessment.correct_answers = correct_count
        assessment.score_percentage = (correct_count / len(answers)) * 100 if answers else 0
        assessment.time_taken_seconds = total_time
        
        # Update user skill scores if this is a skill assessment
        if assessment.skill_id:
            await self._update_user_skill_score(user_id, assessment.skill_id, assessment.score_percentage)
        
        self.db.commit()
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(user_id, assessment, processed_answers)
        
        return {
            "assessment": assessment,
            "answers": processed_answers,
            "recommendations": recommendations
        }
    
    def get_assessment_with_results(self, assessment_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Assessment]:
        """Get assessment with detailed results."""
        assessment = self.get_assessment(assessment_id, user_id)
        if not assessment:
            return None
        
        # Load answers
        assessment.answers = self.db.query(AssessmentAnswer).filter(
            AssessmentAnswer.assessment_id == assessment_id
        ).all()
        
        return assessment
    
    async def generate_skill_assessment(self, user_id: uuid.UUID, skill_id: uuid.UUID) -> Assessment:
        """Generate adaptive skill assessment."""
        # Get user's current skill level
        user_skill = self.db.query(UserSkill).filter(
            and_(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        ).first()
        
        difficulty = "beginner"
        if user_skill and user_skill.assessed_score:
            if user_skill.assessed_score > 70:
                difficulty = "advanced"
            elif user_skill.assessed_score > 40:
                difficulty = "intermediate"
        
        # Generate questions using AI
        questions = await self.question_generator.generate_skill_questions(
            skill_id=skill_id,
            difficulty=difficulty,
            count=20
        )
        
        # Create assessment
        assessment = Assessment(
            user_id=user_id,
            skill_id=skill_id,
            assessment_type="skill_assessment",
            total_questions=len(questions),
            status=AssessmentStatusEnum.PENDING
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        # Add generated questions to database
        for question_data in questions:
            question = Question(
                skill_id=skill_id,
                **question_data
            )
            self.db.add(question)
        
        self.db.commit()
        
        return assessment
    
    async def generate_topic_assessment(self, user_id: uuid.UUID, topic_id: uuid.UUID) -> Assessment:
        """Generate topic assessment."""
        # Get topic details
        from app.models.roadmap import Topic
        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise NotFoundError("Topic not found")
        
        # Generate questions based on topic
        questions = await self.question_generator.generate_topic_questions(
            topic_id=topic_id,
            difficulty=topic.difficulty_level or "intermediate",
            count=15
        )
        
        # Create assessment
        assessment = Assessment(
            user_id=user_id,
            topic_id=topic_id,
            assessment_type="topic_assessment",
            total_questions=len(questions),
            status=AssessmentStatusEnum.PENDING
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        # Add generated questions to database
        for question_data in questions:
            question = Question(
                topic_id=topic_id,
                **question_data
            )
            self.db.add(question)
        
        self.db.commit()
        
        return assessment
    
    def _evaluate_answer(self, question: Question, user_answer: str) -> bool:
        """Evaluate if user answer is correct."""
        if question.question_type == QuestionTypeEnum.MCQ:
            return user_answer.strip().lower() == question.correct_answer.strip().lower()
        elif question.question_type == QuestionTypeEnum.THEORETICAL:
            # For theoretical questions, use semantic similarity
            # For now, simple keyword matching
            correct_keywords = question.correct_answer.lower().split()
            user_keywords = user_answer.lower().split()
            
            matches = sum(1 for keyword in correct_keywords if keyword in user_keywords)
            return matches / len(correct_keywords) > 0.6  # 60% match threshold
        elif question.question_type == QuestionTypeEnum.CODING:
            # For coding questions, would need code execution
            # For now, return True if answer is not empty
            return len(user_answer.strip()) > 0
        else:
            return user_answer.strip().lower() == question.correct_answer.strip().lower()
    
    def _generate_feedback(self, question: Question, is_correct: bool) -> str:
        """Generate feedback for answer."""
        if is_correct:
            return "Correct! " + (question.explanation or "Great job!")
        else:
            return f"Incorrect. {question.explanation or 'Please review this topic and try again.'}"
    
    async def _update_user_skill_score(self, user_id: uuid.UUID, skill_id: uuid.UUID, score: float) -> None:
        """Update user's skill score based on assessment."""
        user_skill = self.db.query(UserSkill).filter(
            and_(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
        ).first()
        
        if user_skill:
            # Update with weighted average (70% new score, 30% old score)
            if user_skill.assessed_score:
                user_skill.assessed_score = (score * 0.7 + user_skill.assessed_score * 0.3)
            else:
                user_skill.assessed_score = score
            
            user_skill.last_assessed_at = datetime.utcnow()
        else:
            # Create new skill record
            user_skill = UserSkill(
                user_id=user_id,
                skill_id=skill_id,
                assessed_score=score,
                last_assessed_at=datetime.utcnow()
            )
            self.db.add(user_skill)
        
        self.db.commit()
    
    async def _generate_recommendations(self, user_id: uuid.UUID, assessment: Assessment, answers: List[AssessmentAnswer]) -> List[str]:
        """Generate personalized recommendations based on assessment results."""
        recommendations = []
        
        # Analyze weak areas
        incorrect_answers = [a for a in answers if not a.is_correct]
        
        if incorrect_answers:
            # Group by skill/topic
            weak_areas = {}
            for answer in incorrect_answers:
                if answer.question.skill_id:
                    skill_name = answer.question.skill_id  # Would need to join with Skill table
                    weak_areas[skill_name] = weak_areas.get(skill_name, 0) + 1
            
            # Generate recommendations for weak areas
            for skill_id, count in weak_areas.items():
                if count > 2:  # More than 2 mistakes in same area
                    recommendations.append(f"Focus on improving {skill_id} - you had {count} incorrect answers")
        
        # General recommendations based on score
        if assessment.score_percentage < 40:
            recommendations.append("Consider reviewing the fundamentals before attempting advanced topics")
        elif assessment.score_percentage < 70:
            recommendations.append("Good progress! Focus on the areas where you made mistakes to improve further")
        else:
            recommendations.append("Excellent work! You're ready for more advanced challenges")
        
        # Time-based recommendations
        if assessment.time_taken_seconds and assessment.total_questions:
            avg_time_per_question = assessment.time_taken_seconds / assessment.total_questions
            if avg_time_per_question > 120:  # More than 2 minutes per question
                recommendations.append("Try to improve your speed with more practice")
        
        return recommendations
