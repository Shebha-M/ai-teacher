"""Adaptation Engine module: determines pedagogical actions based on evaluation and cognitive states."""
from typing import Optional
from ai_engine.providers.base import LLMProvider
from ai_engine.providers import get_default_llm_provider
from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.question import QuestionSchema
from ai_engine.schemas.evaluation import EvaluationResultSchema, CorrectnessLevel
from ai_engine.schemas.misconception import MisconceptionReportSchema
from ai_engine.schemas.adaptation import (
    AdaptationDecisionSchema,
    AdaptationAction,
    DifficultyAdjustment,
)


class AdaptationEngine:
    """
    Pedagogical decision engine. Integrates learner profile, lesson history,
    answer evaluation, and cognitive misconception diagnostics to select the optimal
    pedagogical intervention (RE_EXPLAIN, CHANGE_ANALOGY, SIMPLIFY, MOVE_TO_NEXT_CONCEPT, etc.).
    Combines LLM structured reasoning with educational safeguard rules.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_default_llm_provider()

    async def decide_adaptation(
        self,
        profile: LearnerProfileSchema,
        question: QuestionSchema,
        evaluation: EvaluationResultSchema,
        misconception: Optional[MisconceptionReportSchema] = None,
        recent_performance_score: Optional[float] = None,
    ) -> AdaptationDecisionSchema:
        """
        Produce a structured AdaptationDecisionSchema with educational rationale and strategy.
        """
        system_prompt = (
            "You are a master pedagogical strategist. Decide the exact teaching action to take next. "
            "Available Actions: continue, move_to_next_concept, re_explain, simplify, change_analogy, "
            "give_another_example, reduce_difficulty, increase_difficulty, ask_another_question, "
            "provide_guided_practice, revisit_prerequisite. "
            "CRITICAL SAFEGUARD RULES:\n"
            "- If an active misconception is detected, prioritize CHANGE_ANALOGY or RE_EXPLAIN with counter-analogy.\n"
            "- If answer is incorrect due to lack of knowledge, prioritize SIMPLIFY or PROVIDE_GUIDED_PRACTICE.\n"
            "- If answer is partially correct, prioritize GIVE_ANOTHER_EXAMPLE.\n"
            "- If answer is fully correct, prioritize MOVE_TO_NEXT_CONCEPT or INCREASE_DIFFICULTY.\n"
            "Return valid JSON matching the AdaptationDecisionSchema."
        )

        prompt = (
            f"Concept: {question.concept}\n"
            f"Evaluation Correctness: {evaluation.correctness.value} (Score: {evaluation.score})\n"
            f"Strengths: {', '.join(evaluation.strengths)}\n"
            f"Errors: {evaluation.error_summary or 'None'}\n"
            f"Missing Concepts: {', '.join(evaluation.missing_concepts)}\n"
            f"Misconception Present: {misconception.is_misconception if misconception else False}\n"
            f"Flawed Mental Model: {misconception.flawed_mental_model if misconception else 'N/A'}\n"
            f"Learner Level: {profile.educational_level.value}"
        )

        decision = await self.provider.generate_structured(
            prompt=prompt,
            response_schema=AdaptationDecisionSchema,
            system_prompt=system_prompt,
            evaluation=evaluation,
            misconception=misconception,
            profile=profile,
        )

        # Enforce safeguard: If misconception is true, do not allow plain continue without addressing it
        if misconception and misconception.is_misconception:
            if decision.action in [AdaptationAction.CONTINUE, AdaptationAction.MOVE_TO_NEXT_CONCEPT]:
                decision.action = AdaptationAction.CHANGE_ANALOGY
                decision.reason = (
                    f"Pedagogical Safeguard: Overrode action to address active misconception: "
                    f"{misconception.flawed_mental_model}"
                )
                decision.strategy = misconception.recommended_counter_analogy or "Deploy targeted counter-analogy."
                decision.suggested_analogy = misconception.recommended_counter_analogy

        return decision
