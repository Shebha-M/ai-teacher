"""Tests for Answer Evaluator module."""
import pytest
from ai_engine.modules.answer_evaluator import AnswerEvaluator
from ai_engine.modules.learner_profiler import LearnerProfiler
from ai_engine.schemas.learner import LearnerLevel
from ai_engine.schemas.question import QuestionSchema, QuestionType, QuestionOptionSchema, StudentResponseSchema
from ai_engine.schemas.evaluation import CorrectnessLevel


@pytest.fixture
def sample_question():
    return QuestionSchema(
        question_id="q-tree-1",
        section_id="sec-1",
        concept="Binary Tree Node Rules",
        question_type=QuestionType.MULTIPLE_CHOICE,
        prompt="What is the maximum number of children a binary tree node can have?",
        options=[
            QuestionOptionSchema(key="A", text="1"),
            QuestionOptionSchema(key="B", text="At most 2"),
            QuestionOptionSchema(key="C", text="Must always have 2"),
            QuestionOptionSchema(key="D", text="Unlimited"),
        ],
        expected_answer="B",
        difficulty="beginner",
        rubric="Must recognize that binary means 0, 1, or 2 children.",
    )


@pytest.fixture
def learner_profile():
    return LearnerProfiler.create_profile("Casey", LearnerLevel.BEGINNER)


@pytest.mark.asyncio
async def test_evaluate_correct_answer(sample_question, learner_profile):
    evaluator = AnswerEvaluator()
    response = StudentResponseSchema(
        response_id="r1",
        question_id=sample_question.question_id,
        student_answer="B",
    )
    result = await evaluator.evaluate_response(sample_question, response, learner_profile)

    assert result.correctness == CorrectnessLevel.CORRECT
    assert result.score == 1.0
    assert len(result.strengths) > 0
    assert result.misconception_suspected is False


@pytest.mark.asyncio
async def test_evaluate_misconception_answer(sample_question, learner_profile):
    evaluator = AnswerEvaluator()
    response = StudentResponseSchema(
        response_id="r2",
        question_id=sample_question.question_id,
        student_answer="C",  # "Must always have 2" -> classic misconception overlooking leaves
    )
    result = await evaluator.evaluate_response(sample_question, response, learner_profile)

    assert result.correctness == CorrectnessLevel.INCORRECT_MISCONCEPTION
    assert result.score < 0.5
    assert result.misconception_suspected is True
    assert "leaf" in result.rubric_feedback.lower() or "two" in result.error_summary.lower()


@pytest.mark.asyncio
async def test_evaluate_partial_answer():
    evaluator = AnswerEvaluator()
    profile = LearnerProfiler.create_profile("Casey", LearnerLevel.INTERMEDIATE)
    ohm_q = QuestionSchema(
        question_id="q-ohm-1",
        section_id="sec-1",
        concept="Ohm's Law",
        question_type=QuestionType.SHORT_ANSWER,
        prompt="What happens to current if resistance increases at fixed voltage?",
        expected_answer="Current decreases according to I = V / R",
        difficulty="intermediate",
        rubric="State that current decreases because I is inversely proportional to R.",
    )
    # Student states current decreases, but omits mathematical justification
    response = StudentResponseSchema(
        response_id="r3",
        question_id=ohm_q.question_id,
        student_answer="The current decreases and drops down.",
    )
    result = await evaluator.evaluate_response(ohm_q, response, profile)

    assert result.correctness == CorrectnessLevel.PARTIALLY_CORRECT
    assert 0.5 <= result.score < 1.0
    assert len(result.strengths) > 0
    assert len(result.missing_concepts) > 0
