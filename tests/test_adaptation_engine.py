"""Tests for Adaptation Engine module."""
import pytest
from ai_engine.modules.adaptation_engine import AdaptationEngine
from ai_engine.modules.learner_profiler import LearnerProfiler
from ai_engine.schemas.learner import LearnerLevel
from ai_engine.schemas.question import QuestionSchema, QuestionType
from ai_engine.schemas.evaluation import EvaluationResultSchema, CorrectnessLevel
from ai_engine.schemas.misconception import MisconceptionReportSchema, MisconceptionCategory
from ai_engine.schemas.adaptation import AdaptationAction, DifficultyAdjustment


@pytest.fixture
def profile():
    return LearnerProfiler.create_profile("Jordan", LearnerLevel.BEGINNER)


@pytest.fixture
def question():
    return QuestionSchema(
        question_id="q1",
        section_id="sec-1",
        concept="Resistance",
        question_type=QuestionType.SHORT_ANSWER,
        prompt="Describe resistance.",
        expected_answer="Opposition to flow.",
        difficulty="beginner",
        rubric="Opposition to electrical current.",
    )


@pytest.mark.asyncio
async def test_adaptation_on_misconception_triggers_analogy_change(profile, question):
    adapter = AdaptationEngine()
    evaluation = EvaluationResultSchema(
        evaluation_id="ev1",
        question_id=question.question_id,
        correctness=CorrectnessLevel.INCORRECT_MISCONCEPTION,
        score=0.2,
        strengths=["Addressed the question"],
        error_summary="Confused inverse relationship",
        missing_concepts=["Current decreases"],
        misconception_suspected=True,
        rubric_feedback="Remember resistance opposes current.",
        recommended_teacher_action="Use water-flow counter-analogy",
    )
    misconception = MisconceptionReportSchema(
        misconception_id="m1",
        concept="Resistance",
        category=MisconceptionCategory.INVERSE_RELATION_CONFUSION,
        is_misconception=True,
        flawed_mental_model="Believes resistance amplifies current.",
        correct_mental_model="Resistance chokes current.",
        evidence_from_response="Current increases.",
        recommended_counter_analogy="Water pipe narrowing",
    )

    decision = await adapter.decide_adaptation(profile, question, evaluation, misconception)

    assert decision.action in [AdaptationAction.CHANGE_ANALOGY, AdaptationAction.RE_EXPLAIN]
    assert "misconception" in decision.reason.lower() or "model" in decision.reason.lower()
    assert decision.suggested_analogy is not None


@pytest.mark.asyncio
async def test_adaptation_on_mastery_advances_concept(profile, question):
    adapter = AdaptationEngine()
    evaluation = EvaluationResultSchema(
        evaluation_id="ev2",
        question_id=question.question_id,
        correctness=CorrectnessLevel.CORRECT,
        score=1.0,
        strengths=["Clear articulation of opposition to flow"],
        error_summary=None,
        missing_concepts=[],
        misconception_suspected=False,
        rubric_feedback="Perfect understanding.",
        recommended_teacher_action="Advance to next concept",
    )

    decision = await adapter.decide_adaptation(profile, question, evaluation, None)

    assert decision.action in [AdaptationAction.MOVE_TO_NEXT_CONCEPT, AdaptationAction.CONTINUE]
    assert "master" in decision.reason.lower() or "clear" in decision.reason.lower()
