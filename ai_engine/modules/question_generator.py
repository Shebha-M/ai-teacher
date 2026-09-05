"""Question Generator module: creates targeted diagnostic and checkpoint questions."""
from typing import Optional
from ai_engine.providers.base import LLMProvider
from ai_engine.providers import get_default_llm_provider
from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.lesson import LessonSectionSchema
from ai_engine.schemas.question import QuestionSchema, QuestionType


class QuestionGenerator:
    """
    Generates structured assessment questions (conceptual, multiple choice, short answer,
    problem solving) calibrated to the student's level and the section checkpoint.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_default_llm_provider()

    async def generate_checkpoint_question(
        self,
        section: LessonSectionSchema,
        profile: LearnerProfileSchema,
        preferred_type: Optional[QuestionType] = None,
        difficulty_override: Optional[str] = None,
        grounded_context: Optional[object] = None,
    ) -> QuestionSchema:
        """
        Produce a structured QuestionSchema to test the checkpoint concept.
        """
        target_difficulty = difficulty_override or section.difficulty
        q_type = preferred_type.value if preferred_type else "multiple_choice or conceptual"

        system_prompt = (
            f"You are an expert educational assessment author. Generate a single focused checkpoint question "
            f"for '{section.concept}'. Target level: {profile.educational_level.value}. Difficulty: {target_difficulty}. "
            f"Question style: {q_type}. "
            "The question must directly test the student's conceptual grasp without trick wording. "
            "Never expose chain of thought. Return valid JSON matching the QuestionSchema."
        )

        prompt = (
            f"Concept: {section.concept}\n"
            f"Expected Understanding: {section.expected_understanding}\n"
            f"Section Title: {section.title}"
        )

        question = await self.provider.generate_structured(
            prompt=prompt,
            response_schema=QuestionSchema,
            system_prompt=system_prompt,
            section=section,
            profile=profile,
            grounded_context=grounded_context,
        )

        return question
