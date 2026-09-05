"""Tests for Misconception Detector module."""
import pytest
from ai_engine.modules.misconception_detector import MisconceptionDetector
from ai_engine.schemas.question import QuestionSchema, QuestionType, StudentResponseSchema


@pytest.mark.asyncio
async def test_detects_inverse_relationship_misconception():
    detector = MisconceptionDetector()
    q = QuestionSchema(
        question_id="q-ohm-1",
        section_id="sec-1",
        concept="Ohm's Law",
        question_type=QuestionType.SHORT_ANSWER,
        prompt="What happens to current if resistance increases at fixed voltage?",
        expected_answer="Current decreases",
        difficulty="intermediate",
        rubric="Current is inversely proportional to resistance.",
    )
    # Student incorrectly claims current increases
    response = StudentResponseSchema(
        response_id="r1",
        question_id=q.question_id,
        student_answer="Current increases when resistance goes up.",
    )

    report = await detector.detect_misconception(q, response)

    assert report.is_misconception is True
    assert len(report.flawed_mental_model) > 0
    assert len(report.correct_mental_model) > 0
    assert report.recommended_counter_analogy is not None
    assert "water" in report.recommended_counter_analogy.lower() or "hose" in report.recommended_counter_analogy.lower()


@pytest.mark.asyncio
async def test_detects_no_misconception_on_neutral_answer():
    detector = MisconceptionDetector()
    q = QuestionSchema(
        question_id="q-gen-1",
        section_id="sec-1",
        concept="Data Structures",
        question_type=QuestionType.SHORT_ANSWER,
        prompt="What is a data structure?",
        expected_answer="A format for organizing data.",
        difficulty="beginner",
        rubric="Explain format and access.",
    )
    response = StudentResponseSchema(
        response_id="r2",
        question_id=q.question_id,
        student_answer="I don't remember exactly.",
    )

    report = await detector.detect_misconception(q, response)
    assert report.is_misconception is False
