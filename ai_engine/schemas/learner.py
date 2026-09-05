"""Learner profile schemas and data types."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class LearnerLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TeachingStyle(str, Enum):
    VISUAL = "visual"
    ANALOGY_DRIVEN = "analogy_driven"
    FIRST_PRINCIPLES = "first_principles"
    PRACTICAL_CODE = "practical_code"
    SOCRATIC = "socratic"


class LearningGoal(str, Enum):
    CONCEPT_MASTERY = "concept_mastery"
    EXAM_PREPARATION = "exam_preparation"
    QUICK_REVIEW = "quick_review"
    INTERVIEW_PREP = "interview_prep"
    PRACTICAL_APPLICATION = "practical_application"


class LearnerProfileSchema(BaseModel):
    learner_id: str = Field(..., description="Unique identifier for the learner")
    name: Optional[str] = Field("Learner", description="Learner name")
    educational_level: LearnerLevel = Field(
        LearnerLevel.BEGINNER, description="Student's background knowledge level"
    )
    prior_knowledge: List[str] = Field(
        default_factory=list, description="Concepts already familiar to the student"
    )
    learning_objective: str = Field(
        "Master the fundamentals and gain practical intuition",
        description="The primary objective for this learning session",
    )
    preferred_teaching_style: TeachingStyle = Field(
        TeachingStyle.ANALOGY_DRIVEN, description="Preferred style of explanation"
    )
    preferred_language: str = Field(
        "en", description="ISO language code, e.g., 'en', 'hi', 'ta', 'te', 'ml', 'kn'"
    )
    fallback_language: str = Field(
        "en", description="Fallback language if translation or voice unavailable"
    )
    language_mode: str = Field(
        "bilingual", description="Presentation mode: 'full', 'bilingual', 'mixed'"
    )
    preferred_voice_id: Optional[str] = Field(
        None, description="Preferred TTS voice model ID"
    )
    available_learning_time: int = Field(
        15, description="Available session duration in minutes (e.g., 5, 15, 30, 60)"
    )
    desired_depth: str = Field(
        "intermediate", description="Depth level: 'high_level', 'intermediate', 'deep_dive'"
    )
    strengths: List[str] = Field(
        default_factory=list, description="Verified concepts and skills"
    )
    weaknesses: List[str] = Field(
        default_factory=list, description="Concepts needing reinforcement"
    )
    known_misconceptions: List[str] = Field(
        default_factory=list, description="Specific identified flawed mental models"
    )
    current_topic: Optional[str] = Field(None, description="Topic currently being studied")
    current_session_id: Optional[str] = Field(None, description="Active session ID")
