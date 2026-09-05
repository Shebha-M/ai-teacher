"""Tests for Question Generator module."""
import pytest
from ai_engine.modules.question_generator import QuestionGenerator
from ai_engine.modules.learner_profiler import LearnerProfiler
from ai_engine.schemas.learner import LearnerLevel
from ai_engine.schemas.lesson import LessonSectionSchema, VisualRecommendation, VisualType, CheckpointSchema


@pytest.mark.asyncio
async def test_question_generator_produces_structured_question():
    profiler = LearnerProfiler()
    profile = profiler.create_profile(name="Sam", educational_level=LearnerLevel.BEGINNER)
    section = LessonSectionSchema(
        section_id="sec-1",
        section_number=1,
        concept="Binary Tree Node Rules",
        title="Intro to Binary Trees",
        objective="Understand node hierarchy",
        difficulty="beginner",
        estimated_time_minutes=5,
        explanation_outline="Nodes and left/right children",
        example_context="Family tree analogy",
        visual_recommendation=VisualRecommendation(
            visual_type=VisualType.LABELED_DIAGRAM,
            description="Binary tree schematic",
            suggested_elements=["Root", "Left", "Right"],
        ),
        question_checkpoint=CheckpointSchema(
            checkpoint_id="chk-1",
            core_concept="Maximum child nodes",
            trigger_condition="after_section_explanation",
        ),
        expected_understanding="A node can have at most 2 children.",
    )

    q_gen = QuestionGenerator()
    question = await q_gen.generate_checkpoint_question(section=section, profile=profile)

    assert question.question_id is not None
    assert question.section_id == "sec-1"
    assert len(question.prompt) > 0
    assert len(question.expected_answer) > 0
    assert len(question.rubric) > 0
    if question.options:
        assert len(question.options) >= 2
