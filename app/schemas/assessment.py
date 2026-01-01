from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class QuestionBase(BaseModel):
    question_text: str
    question_type: str  # mcq, theoretical, coding, behavioral
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty_level: Optional[str] = None
    time_limit_seconds: Optional[int] = None
    skill_id: Optional[uuid.UUID] = None
    topic_id: Optional[uuid.UUID] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(QuestionBase):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    correct_answer: Optional[str] = None

class QuestionResponse(QuestionBase):
    id: uuid.UUID
    is_active: bool
    created_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AssessmentBase(BaseModel):
    assessment_type: str
    total_questions: Optional[int] = None

class AssessmentCreate(AssessmentBase):
    skill_id: Optional[uuid.UUID] = None
    topic_id: Optional[uuid.UUID] = None
    difficulty: Optional[str] = None
    question_count: Optional[int] = 10

class AssessmentUpdate(AssessmentBase):
    pass

class AssessmentResponse(AssessmentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    skill_id: Optional[uuid.UUID]
    topic_id: Optional[uuid.UUID]
    status: str
    correct_answers: Optional[int]
    score_percentage: Optional[float]
    time_taken_seconds: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AssessmentAnswerBase(BaseModel):
    question_id: uuid.UUID
    user_answer: str
    time_taken_seconds: Optional[int] = None

class AssessmentAnswerCreate(AssessmentAnswerBase):
    pass

class AssessmentAnswerResponse(AssessmentAnswerBase):
    id: uuid.UUID
    assessment_id: uuid.UUID
    is_correct: Optional[bool]
    feedback: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AssessmentWithAnswersResponse(AssessmentResponse):
    answers: List[AssessmentAnswerResponse] = []

class AssessmentSubmissionRequest(BaseModel):
    assessment_id: uuid.UUID
    answers: List[AssessmentAnswerCreate]

class AssessmentResultResponse(BaseModel):
    assessment: AssessmentResponse
    answers: List[AssessmentAnswerResponse]
    skill_improvements: List[Dict[str, Any]]
    recommendations: List[str]

class SkillAssessmentRequest(BaseModel):
    skill_id: uuid.UUID
    difficulty: Optional[str] = "adaptive"
    question_count: int = 20

class TopicAssessmentRequest(BaseModel):
    topic_id: uuid.UUID
    question_count: int = 15
