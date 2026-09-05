"""Misconception Detector module: identifies cognitive flaws and erroneous internal mental models."""
from typing import Optional
from ai_engine.providers.base import LLMProvider
from ai_engine.providers import get_default_llm_provider
from ai_engine.schemas.question import QuestionSchema, StudentResponseSchema
from ai_engine.schemas.misconception import MisconceptionReportSchema


class MisconceptionDetector:
    """
    Distinguishes between mere lack of knowledge vs. an active contradictory mental model.
    Pinpoints the exact flawed reasoning, articulates the correct scientific model,
    and formulates targeted counter-analogies.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_default_llm_provider()

    async def detect_misconception(
        self,
        question: QuestionSchema,
        student_response: StudentResponseSchema,
    ) -> MisconceptionReportSchema:
        """
        Analyze student response to diagnose whether a misconception is present.
        """
        system_prompt = (
            "You are a cognitive science and educational diagnostic expert. "
            "Analyze the student's answer to identify if they hold a specific flawed mental model (misconception) "
            "or merely lack information. "
            "If it is an active misconception, clearly articulate both the flawed model and the correct model, "
            "cite evidence from their answer, and provide a counter-analogy. "
            "Return valid JSON matching the MisconceptionReportSchema."
        )

        prompt = (
            f"Concept: {question.concept}\n"
            f"Question Prompt: {question.prompt}\n"
            f"Expected Answer: {question.expected_answer}\n"
            f"Student Answer: {student_response.student_answer}"
        )

        report = await self.provider.generate_structured(
            prompt=prompt,
            response_schema=MisconceptionReportSchema,
            system_prompt=system_prompt,
            question=question,
            student_answer=student_response.student_answer,
        )

        return report
