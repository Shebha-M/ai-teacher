"""Lesson plan and section schemas."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from ai_engine.schemas.learner import LearnerLevel


class VisualType(str, Enum):
    EQUATION = "equation"
    GRAPH = "graph"
    TIMELINE = "timeline"
    LABELED_DIAGRAM = "labeled_diagram"
    FLOWCHART = "flowchart"
    CODE_BLOCK = "code_block"
    EXECUTION_TRACE = "execution_trace"
    ARCHITECTURE_DIAGRAM = "architecture_diagram"
    CONCEPT_MAP = "concept_map"


class VisualRecommendation(BaseModel):
    visual_type: VisualType = Field(..., description="Category of visual representation")
    description: str = Field(..., description="Detailed description of what the visual should display")
    suggested_elements: List[str] = Field(
        default_factory=list, description="Key labels, nodes, or components to highlight visually"
    )


class CheckpointSchema(BaseModel):
    checkpoint_id: str = Field(..., description="Unique ID for this checkpoint")
    core_concept: str = Field(..., description="Concept being tested before allowing progress")
    trigger_condition: str = Field(
        "after_section_explanation", description="When this checkpoint evaluates"
    )


class LessonSectionSchema(BaseModel):
    section_id: str = Field(..., description="Unique section ID e.g. 'sec-1'")
    section_number: int = Field(1, description="Sequential index in the lesson")
    concept: str = Field(..., description="Core concept covered in this section")
    title: str = Field(..., description="Student-facing section title")
    objective: str = Field(..., description="Specific educational outcome of this section")
    difficulty: str = Field("beginner", description="Section difficulty level")
    estimated_time_minutes: int = Field(5, description="Planned duration for this section")
    explanation_outline: str = Field(..., description="Summary of key talking points")
    example_context: str = Field(..., description="Concrete real-world or code example context")
    visual_recommendation: VisualRecommendation = Field(
        ..., description="Recommended visual aid for this section"
    )
    question_checkpoint: Optional[CheckpointSchema] = Field(
        None, description="Assessment checkpoint attached to this section"
    )
    expected_understanding: str = Field(
        ..., description="What the student must grasp before proceeding"
    )


class LessonPlanSchema(BaseModel):
    lesson_id: str = Field(..., description="Unique identifier for the lesson")
    topic: str = Field(..., description="Subject or topic of study")
    lesson_title: str = Field(..., description="Engaging, clear title for the lesson")
    learning_objectives: List[str] = Field(..., description="List of learning goals")
    estimated_duration: int = Field(..., description="Total planned duration in minutes")
    learner_level: LearnerLevel = Field(..., description="Target learner level")
    sections: List[LessonSectionSchema] = Field(..., description="Planned sections in order")
    section_ordering: List[str] = Field(
        default_factory=list, description="Ordered list of section_ids"
    )
    explanation_depth: str = Field("intermediate", description="Depth: conceptual, standard, deep_dive")
    examples: List[str] = Field(default_factory=list, description="Key planned examples")
    questions: List[str] = Field(default_factory=list, description="Planned question concepts")
    checkpoints: List[str] = Field(default_factory=list, description="Checkpoint concepts")
    final_assessment_direction: str = Field(
        ..., description="Summary of how final mastery will be assessed"
    )
