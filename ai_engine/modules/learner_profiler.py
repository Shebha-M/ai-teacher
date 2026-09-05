"""Learner Profiler module: builds and updates comprehensive student learning models."""
import uuid
from typing import Optional, List
from ai_engine.schemas.learner import (
    LearnerProfileSchema,
    LearnerLevel,
    TeachingStyle,
    LearningGoal,
)


class LearnerProfiler:
    """Manages learner pedagogical profiles, prior knowledge, strengths, and misconception tracking."""

    @staticmethod
    def create_profile(
        name: str = "Learner",
        educational_level: LearnerLevel = LearnerLevel.BEGINNER,
        learning_objective: str = "Master core concepts and practical intuition",
        preferred_teaching_style: TeachingStyle = TeachingStyle.ANALOGY_DRIVEN,
        preferred_language: str = "en",
        available_learning_time: int = 15,
        desired_depth: str = "intermediate",
        prior_knowledge: Optional[List[str]] = None,
        learner_id: Optional[str] = None,
    ) -> LearnerProfileSchema:
        """Create a new validated learner profile."""
        return LearnerProfileSchema(
            learner_id=learner_id or f"lrn-{uuid.uuid4().hex[:8]}",
            name=name,
            educational_level=educational_level,
            prior_knowledge=prior_knowledge or [],
            learning_objective=learning_objective,
            preferred_teaching_style=preferred_teaching_style,
            preferred_language=preferred_language,
            available_learning_time=available_learning_time,
            desired_depth=desired_depth,
            strengths=[],
            weaknesses=[],
            known_misconceptions=[],
        )

    @staticmethod
    def record_concept_outcome(
        profile: LearnerProfileSchema,
        concept: str,
        is_mastered: bool,
        misconception: Optional[str] = None,
    ) -> LearnerProfileSchema:
        """Update learner profile dynamically based on evaluation outcomes."""
        if is_mastered:
            if concept not in profile.strengths:
                profile.strengths.append(concept)
            if concept in profile.weaknesses:
                profile.weaknesses.remove(concept)
        else:
            if concept not in profile.weaknesses:
                profile.weaknesses.append(concept)

        if misconception and misconception not in profile.known_misconceptions:
            profile.known_misconceptions.append(misconception)

        return profile
