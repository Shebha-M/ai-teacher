"""Teaching Agent module: converts lesson sections into pedagogical explanations, analogies, and visual plans."""
from typing import Optional
from ai_engine.providers.base import LLMProvider
from ai_engine.providers import get_default_llm_provider
from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.lesson import LessonSectionSchema
from ai_engine.schemas.teaching import TeachingResponseSchema, TeachingAction


class TeachingAgent:
    """
    Transforms planned lesson sections into engaging pedagogical content tailored
    to learner background, preferred teaching style (analogy, visual, code), and known misconceptions.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_default_llm_provider()

    async def explain_section(
        self,
        section: LessonSectionSchema,
        profile: LearnerProfileSchema,
        teaching_action: TeachingAction = TeachingAction.EXPLAIN,
        custom_adaptation_strategy: Optional[str] = None,
        context: Optional[str] = None,
        grounded_context: Optional[object] = None,
    ) -> TeachingResponseSchema:
        """
        Produce a structured TeachingResponseSchema for the current section.
        """
        grounding_prompt = ""
        if grounded_context and getattr(grounded_context, "synthesized_context", None):
            grounding_prompt = f"\nVERIFIED SOURCE CITATIONS & EXCERPTS:\n{grounded_context.synthesized_context}\nGround your explanation in these cited excerpts without inventing unsupported source claims.\n"

        system_prompt = (
            f"You are a master human-like teacher. Deliver an engaging teaching block for '{section.title}'. "
            f"Learner Level: {profile.educational_level.value}. Teaching Style: {profile.preferred_teaching_style.value}. "
            f"Known Misconceptions to avoid: {', '.join(profile.known_misconceptions) if profile.known_misconceptions else 'None'}. "
            f"Action: {teaching_action.value}. "
            f"{f'Adaptation Strategy: {custom_adaptation_strategy}' if custom_adaptation_strategy else ''} "
            "Always include an intuitive analogy, a concrete example, a clear key takeaway, and an actionable visual instruction. "
            "Return valid JSON matching the TeachingResponseSchema."
        )

        prompt = (
            f"Concept: {section.concept}\n"
            f"Objective: {section.objective}\n"
            f"Outline: {section.explanation_outline}\n"
            f"Example Context: {section.example_context}\n"
            f"Visual Recommendation: {section.visual_recommendation.description}\n"
            f"Context Grounding: {context or 'General curriculum'}\n"
            f"{grounding_prompt}"
        )

        response = await self.provider.generate_structured(
            prompt=prompt,
            response_schema=TeachingResponseSchema,
            system_prompt=system_prompt,
            section=section,
            profile=profile,
            teaching_action=teaching_action,
            grounded_context=grounded_context,
        )

        return response
