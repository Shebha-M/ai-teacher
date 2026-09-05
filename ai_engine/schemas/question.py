"""Question and student response schemas."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    CONCEPTUAL = "conceptual"
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    PROBLEM_SOLVING = "problem_solving"
    APPLICATION = "application"
    EXPLAIN_IN_OWN_WORDS = "explain_in_own_words"


class QuestionOptionSchema(BaseModel):
    key: str = Field(..., description="Option identifier, e.g., 'A', 'B', 'C', 'D'")
    text: str = Field(..., description="Option description")


class QuestionSchema(BaseModel):
    question_id: str = Field(..., description="Unique question ID")
    section_id: str = Field(..., description="Related section ID")
    concept: str = Field(..., description="Target concept being assessed")
    question_type: QuestionType = Field(..., description="Type of question")
    prompt: str = Field(..., description="The student-facing question text")
    options: Optional[List[QuestionOptionSchema]] = Field(
        None, description="Choices for multiple-choice questions"
    )
    expected_answer: str = Field(..., description="Ground-truth answer or ideal response")
    difficulty: str = Field("intermediate", description="Difficulty: beginner, intermediate, advanced")
    rubric: str = Field(..., description="Evaluation criteria and key points required for correctness")
    hints: List[str] = Field(default_factory=list, description="Progressive hints if student struggles")


class StudentResponseSchema(BaseModel):
    response_id: str = Field(..., description="Unique ID for this response")
    question_id: str = Field(..., description="ID of question being answered")
    student_answer: str = Field(..., description="The raw answer provided by the student")
    time_taken_seconds: Optional[int] = Field(None, description="Time taken to submit answer")
