"""Misconception detection schemas."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class MisconceptionCategory(str, Enum):
    INVERSE_RELATION_CONFUSION = "inverse_relation_confusion"
    OVERGENERALIZATION = "overgeneralization"
    CATEGORY_ERROR = "category_error"
    MECHANICAL_MISAPPLICATION = "mechanical_misapplication"
    INTUITIVE_HEURISTIC_TRAP = "intuitive_heuristic_trap"
    TERMINOLOGY_CONFUSION = "terminology_confusion"
    OTHER = "other"


class MisconceptionReportSchema(BaseModel):
    misconception_id: str = Field(..., description="Unique ID for detected misconception")
    concept: str = Field(..., description="Target concept where confusion occurred")
    category: MisconceptionCategory = Field(
        MisconceptionCategory.OTHER, description="Classification of the cognitive error"
    )
    is_misconception: bool = Field(
        ..., description="True if a flawed mental model is present; False if purely lack of knowledge"
    )
    flawed_mental_model: str = Field(
        ..., description="Description of the student's erroneous internal reasoning model"
    )
    correct_mental_model: str = Field(
        ..., description="The scientifically/computationally accurate mental model"
    )
    evidence_from_response: str = Field(
        ..., description="Quote or reasoning artifact from student's answer indicating the misconception"
    )
    recommended_counter_analogy: Optional[str] = Field(
        None, description="Targeted cognitive counter-example or analogy to dismantle the misconception"
    )
    prerequisite_to_review: Optional[str] = Field(
        None, description="Foundational prerequisite that may need brief revisit"
    )
