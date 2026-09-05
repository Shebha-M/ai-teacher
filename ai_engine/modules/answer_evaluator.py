"""Answer Evaluator module: multi-dimensional pedagogical evaluation of student responses."""
from typing import Optional
from ai_engine.providers.base import LLMProvider
from ai_engine.providers import get_default_llm_provider
from ai_engine.schemas.learner import LearnerProfileSchema
from ai_engine.schemas.question import QuestionSchema, StudentResponseSchema
from ai_engine.schemas.evaluation import EvaluationResultSchema


class AnswerEvaluator:
    """
    Evaluates student answers across multiple pedagogical dimensions:
    identifies strengths, categorizes correctness (correct, partial, lack of knowledge, misconception),
    computes a normalized score, pinpoints missing concepts, and provides constructive rubric feedback.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_default_llm_provider()

    async def evaluate_response(
        self,
        question: QuestionSchema,
        student_response: StudentResponseSchema,
        profile: LearnerProfileSchema,
        context: Optional[str] = None,
    ) -> EvaluationResultSchema:
        """
        Evaluate student response and produce a structured EvaluationResultSchema.
        """
        system_prompt = (
            f"You are a master teacher evaluating a student's answer. Target Concept: '{question.concept}'. "
            f"Expected Answer: '{question.expected_answer}'. Rubric: '{question.rubric}'. "
            f"Learner Level: {profile.educational_level.value}. "
            "Evaluate constructively. Support partially correct answers (score 0.1 to 0.9). "
            "Distinguish clearly between lack of knowledge and an active misconception. "
            "Return valid JSON matching the EvaluationResultSchema."
        )

        prompt = (
            f"Question Prompt: {question.prompt}\n"
            f"Student Answer: {student_response.student_answer}\n"
            f"Question Rubric: {question.rubric}\n"
            f"Context: {context or 'N/A'}"
        )

        evaluation = await self.provider.generate_structured(
            prompt=prompt,
            response_schema=EvaluationResultSchema,
            system_prompt=system_prompt,
            question=question,
            student_answer=student_response.student_answer,
            profile=profile,
        )

        return evaluation
