"""Evaluation schemas for student responses."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CorrectnessLevel(str, Enum):
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT_LACK_OF_KNOWLEDGE = "incorrect_lack_of_knowledge"
    INCORRECT_MISCONCEPTION = "incorrect_misconception"


class EvaluationResultSchema(BaseModel):
    evaluation_id: str = Field(..., description="Unique evaluation ID")
    question_id: str = Field(..., description="ID of evaluated question")
    correctness: CorrectnessLevel = Field(..., description="Categorization of answer correctness")
    score: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized score between 0.0 (wrong) and 1.0 (perfect)"
    )
    strengths: List[str] = Field(
        default_factory=list, description="What the student accurately understood or articulated"
    )
    error_summary: Optional[str] = Field(
        None, description="Summary of where the response went wrong or fell short"
    )
    missing_concepts: List[str] = Field(
        default_factory=list, description="Required concepts omitted from the answer"
    )
    misconception_suspected: bool = Field(
        False, description="Whether the answer suggests a specific flawed mental model"
    )
    detected_misconception_id: Optional[str] = Field(
        None, description="Reference to detected misconception if applicable"
    )
    rubric_feedback: str = Field(
        ..., description="Constructive, encouraging educational feedback tailored to the learner"
    )
    recommended_teacher_action: str = Field(
        ..., description="Direct advice to teaching agent on next pedagogical move"
    )
