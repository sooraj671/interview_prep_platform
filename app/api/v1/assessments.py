from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
import uuid

from app.database import get_db
from app.models.user import User
from app.schemas.assessment import (
    AssessmentResponse, AssessmentCreate, AssessmentUpdate,
    QuestionResponse, QuestionCreate, QuestionUpdate,
    AssessmentAnswerResponse
)
from app.services.assessment_service import AssessmentService
from app.dependencies import get_current_user, require_candidate_user

router = APIRouter()

@router.get("/", response_model=List[AssessmentResponse])
async def get_my_assessments(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> Any:
    """Get current user's assessments."""
    assessment_service = AssessmentService(db)
    return assessment_service.get_user_assessments(current_user.id, skip=skip, limit=limit)

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    assessment_create: AssessmentCreate,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new assessment."""
    assessment_service = AssessmentService(db)
    return await assessment_service.create_assessment(current_user.id, assessment_create)

@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get assessment by ID."""
    assessment_service = AssessmentService(db)
    assessment = assessment_service.get_assessment(assessment_id, current_user.id)
    if not assessment:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Assessment not found")
    return assessment

@router.post("/{assessment_id}/start")
async def start_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Start an assessment session."""
    assessment_service = AssessmentService(db)
    assessment = await assessment_service.start_assessment(assessment_id, current_user.id)
    if not assessment:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Assessment not found")
    
    return {"message": "Assessment started", "assessment_id": assessment.id}

@router.post("/{assessment_id}/submit")
async def submit_assessment(
    assessment_id: uuid.UUID,
    answers: List[dict],  # List of {question_id, answer, time_taken}
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Submit assessment answers."""
    assessment_service = AssessmentService(db)
    result = await assessment_service.submit_assessment(assessment_id, current_user.id, answers)
    if not result:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Assessment not found")
    
    return result

@router.get("/{assessment_id}/results", response_model=AssessmentResponse)
async def get_assessment_results(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get assessment results with detailed feedback."""
    assessment_service = AssessmentService(db)
    assessment = assessment_service.get_assessment_with_results(assessment_id, current_user.id)
    if not assessment:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Assessment not found")
    return assessment

# Question endpoints
@router.get("/questions/", response_model=List[QuestionResponse])
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    skill_id: Optional[uuid.UUID] = Query(None),
    difficulty: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Any:
    """Get questions with optional filtering."""
    assessment_service = AssessmentService(db)
    return assessment_service.get_questions(skip=skip, limit=limit, skill_id=skill_id, difficulty=difficulty, question_type=question_type)

@router.post("/questions/", response_model=QuestionResponse)
async def create_question(
    question_create: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new question."""
    assessment_service = AssessmentService(db)
    return assessment_service.create_question(question_create, current_user.id)

@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Any:
    """Get question by ID."""
    assessment_service = AssessmentService(db)
    question = assessment_service.get_question(question_id)
    if not question:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Question not found")
    return question

@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: uuid.UUID,
    question_update: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update question."""
    assessment_service = AssessmentService(db)
    question = assessment_service.update_question(question_id, question_update, current_user.id)
    if not question:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Question not found")
    return question

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete question."""
    assessment_service = AssessmentService(db)
    assessment_service.delete_question(question_id, current_user.id)
    return {"message": "Question deleted successfully"}

# Skill assessment endpoints
@router.post("/skills/{skill_id}/assess")
async def assess_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate and start skill assessment."""
    assessment_service = AssessmentService(db)
    assessment = await assessment_service.generate_skill_assessment(current_user.id, skill_id)
    return assessment

@router.post("/topics/{topic_id}/assess")
async def assess_topic(
    topic_id: uuid.UUID,
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate and start topic assessment."""
    assessment_service = AssessmentService(db)
    assessment = await assessment_service.generate_topic_assessment(current_user.id, topic_id)
    return assessment
