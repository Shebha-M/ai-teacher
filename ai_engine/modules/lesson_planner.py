"""Lesson Planner module: synthesizes structured, time-adapted pedagogical roadmaps."""
from typing import Optional
from ai_engine.providers.base import LLMProvider
from ai_engine.providers import get_default_llm_provider
from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.lesson import LessonPlanSchema


class LessonPlanner:
    """
    Generates structured lesson plans that dynamically alter their structural depth,
    section counts, checkpoint frequencies, and visual modalities according to available time and learner profile.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_default_llm_provider()

    async def plan_lesson(
        self,
        topic: str,
        profile: LearnerProfileSchema,
        knowledge_context: Optional[str] = None,
        grounded_context: Optional[object] = None,
    ) -> LessonPlanSchema:
        """
        Generate a fully structured LessonPlanSchema adapting to time, level, and goals.
        """
        grounding_prompt = ""
        if grounded_context and getattr(grounded_context, "synthesized_context", None):
            grounding_prompt = f"\nVERIFIED SOURCE MATERIAL GROUNDING:\n{grounded_context.synthesized_context}\n"

        system_prompt = (
            f"You are a master curriculum architect. Create a structured lesson plan for '{topic}'. "
            f"Learner Level: {profile.educational_level.value}. Available Time: {profile.available_learning_time} minutes. "
            f"Teaching Style: {profile.preferred_teaching_style.value}. Language: {profile.preferred_language}. "
            "CRITICAL TIME RULES:\n"
            "- If available time <= 10 min: exactly 1-2 rapid essential concept sections.\n"
            "- If available time <= 30 min: exactly 3 balanced sections (Intuition -> Mechanics -> Application).\n"
            "- If available time >= 45 min: exactly 4-5 deep dive sections with code/math, edge cases, and architectural synthesis.\n"
            "If verified source material grounding is provided, prioritize teaching concepts, definitions, and examples from that source.\n"
            "Return valid JSON matching the LessonPlanSchema."
        )

        prompt = (
            f"Topic: {topic}\n"
            f"Learning Objective: {profile.learning_objective}\n"
            f"Prior Knowledge: {', '.join(profile.prior_knowledge) if profile.prior_knowledge else 'None reported'}\n"
            f"Context: {knowledge_context or 'Standard educational curriculum'}\n"
            f"{grounding_prompt}"
        )

        plan = await self.provider.generate_structured(
            prompt=prompt,
            response_schema=LessonPlanSchema,
            system_prompt=system_prompt,
            topic=topic,
            profile=profile,
            context=knowledge_context,
            grounded_context=grounded_context,
        )

        # Enforce consistent section ordering
        if not plan.section_ordering or len(plan.section_ordering) != len(plan.sections):
            plan.section_ordering = [s.section_id for s in plan.sections]

        return plan
