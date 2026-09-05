"""Assessment and Learning Report schemas for final evaluation and personalized recommendations."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AssessmentQuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    CONCEPTUAL = "conceptual"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"


class AssessmentOption(BaseModel):
    key: str = Field(..., description="Option key, e.g. 'A', 'B'")
    text: str = Field(..., description="Option text")


class AssessmentQuestion(BaseModel):
    question_id: str = Field(..., description="Unique ID of question")
    concept: str = Field(..., description="Concept tested")
    question_type: AssessmentQuestionType = Field(AssessmentQuestionType.MULTIPLE_CHOICE)
    prompt: str = Field(..., description="Question statement")
    options: List[AssessmentOption] = Field(default_factory=list, description="Options for MCQ/TF")
    expected_answer: str = Field(..., description="Expected answer key or text")
    difficulty: str = Field("beginner", description="Difficulty: beginner, intermediate, advanced")
    explanation: str = Field("", description="Explanation of the correct answer")


class FinalAssessmentSchema(BaseModel):
    assessment_id: str = Field(..., description="Unique ID for assessment")
    session_id: str = Field(..., description="Associated teaching session ID")
    topic: str = Field(..., description="Overall topic of the assessment")
    learner_level: str = Field("beginner", description="Learner educational level")
    estimated_time_minutes: int = Field(5, description="Estimated completion time in minutes")
    questions: List[AssessmentQuestion] = Field(..., description="2-4 assessment questions covering taught concepts")


class AssessmentAnswerItem(BaseModel):
    question_id: str = Field(..., description="ID of question being answered")
    student_answer: str = Field(..., description="Student response text or option key")


class SubmitAssessmentRequest(BaseModel):
    answers: List[AssessmentAnswerItem] = Field(..., description="Submitted answers for assessment")


class QuestionGradingResult(BaseModel):
    question_id: str
    concept: str
    is_correct: bool
    score: float
    student_answer: str
    expected_answer: str
    feedback: str


class LearningReportSchema(BaseModel):
    report_id: str = Field(..., description="Unique ID for learning report")
    session_id: str = Field(..., description="Teaching session ID")
    topic: str = Field(..., description="Topic studied")
    learner_name: str = Field(..., description="Student name")
    overall_score_percent: int = Field(..., description="Overall score percentage (0-100)")
    status: str = Field("completed", description="Status: 'mastered', 'completed', 'needs_revision'")
    concepts_understood: List[str] = Field(default_factory=list, description="Concepts mastered during session")
    concepts_needing_improvement: List[str] = Field(default_factory=list, description="Concepts that need further practice")
    misconceptions_identified: List[str] = Field(default_factory=list, description="Misconceptions diagnosed during session")
    misconceptions_resolved: List[str] = Field(default_factory=list, description="Misconceptions successfully remediated")
    progress_percent: int = Field(100, description="Curriculum progress percentage")
    recommended_revision: str = Field(..., description="Specific concept or topic to revise")
    revision_reason: str = Field(..., description="Traceable rationale based on checkpoint & assessment errors")
    next_topic_recommendation: str = Field(..., description="Suggested next educational topic")
    next_topic_reason: str = Field(..., description="Pedagogical justification for next topic progression")
    total_questions_answered: int = Field(0, description="Total checkpoint + assessment questions answered")
    question_results: List[QuestionGradingResult] = Field(default_factory=list, description="Individual question results")
    created_at: str = Field(..., description="ISO timestamp")
