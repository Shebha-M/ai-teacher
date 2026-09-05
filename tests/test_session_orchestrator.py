"""Tests for Teaching Session Orchestrator coordinating the complete educational teaching loop."""
import pytest
from ai_engine.modules.session_orchestrator import TeachingSessionOrchestrator
from ai_engine.modules.learner_profiler import LearnerProfiler
from ai_engine.schemas.learner import LearnerLevel
from ai_engine.schemas.session import SessionStatus
from ai_engine.schemas.evaluation import CorrectnessLevel
from ai_engine.schemas.adaptation import AdaptationAction


@pytest.mark.asyncio
async def test_full_teaching_loop_progression():
    """
    Simulates a full teaching loop:
    1. Initialize session & profile
    2. Plan lesson (20 mins)
    3. Teach section 1
    4. Fetch checkpoint question
    5. Submit student answer (correct)
    6. Evaluate and diagnose
    7. Adapt and advance to next section
    """
    orchestrator = TeachingSessionOrchestrator()
    profile = LearnerProfiler.create_profile(
        name="Taylor",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=20,
    )

    # 1. Initialize
    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)
    assert session.status == SessionStatus.INITIALIZED
    assert session.current_topic == "Binary Trees"

    # 2. Plan
    session = await orchestrator.plan_session(session)
    assert session.status == SessionStatus.TEACHING
    assert session.lesson_plan is not None
    assert len(session.lesson_plan.sections) == 3

    # 3. Teach section 1
    teaching = await orchestrator.teach_current_section(session)
    assert teaching.section_id == session.lesson_plan.sections[0].section_id
    assert len(teaching.explanation) > 0
    assert len(teaching.analogy) > 0
    assert teaching.visual_instruction is not None

    # 4. Checkpoint question
    question = await orchestrator.get_checkpoint_question(session)
    assert question.section_id == session.lesson_plan.sections[0].section_id
    assert len(question.prompt) > 0

    # 5 & 6. Submit correct answer ("B" - At most 2 children)
    outcome = await orchestrator.process_student_response(session, student_answer="B")
    evaluation = outcome["evaluation"]
    adaptation = outcome["adaptation"]

    assert evaluation.correctness == CorrectnessLevel.CORRECT
    assert evaluation.score == 1.0
    assert len(session.history) == 1
    assert session.concept_mastery_map[question.concept].status == "mastered"
    assert question.concept in session.concepts_mastered

    # 7. Advance
    advance_res = await orchestrator.advance_or_adapt(session)
    assert advance_res["action_taken"] == "advanced_to_next_section"
    assert session.current_section_index == 1
    assert session.current_section_id == session.lesson_plan.sections[1].section_id


@pytest.mark.asyncio
async def test_teaching_loop_misconception_intervention():
    """
    Tests that a student response with an active misconception triggers an educational intervention
    (re-explaining with a counter-analogy) rather than blindly advancing.
    """
    orchestrator = TeachingSessionOrchestrator()
    profile = LearnerProfiler.create_profile(
        name="Morgan",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=20,
    )

    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)
    session = await orchestrator.plan_session(session)
    await orchestrator.teach_current_section(session)
    await orchestrator.get_checkpoint_question(session)

    # Student provides misconception answer "C" (thinks every node must have 2 children, overlooking leaf nodes)
    outcome = await orchestrator.process_student_response(session, student_answer="C")
    evaluation = outcome["evaluation"]
    misconception = outcome["misconception"]
    adaptation = outcome["adaptation"]

    assert evaluation.correctness == CorrectnessLevel.INCORRECT_MISCONCEPTION
    assert misconception.is_misconception is True
    assert adaptation.action in [AdaptationAction.CHANGE_ANALOGY, AdaptationAction.RE_EXPLAIN]
    assert adaptation.suggested_analogy is not None

    # Advance or adapt should NOT advance to section 2, it should re-explain section 1 with the new analogy!
    advance_res = await orchestrator.advance_or_adapt(session)
    assert advance_res["action_taken"] == "re_explained_with_analogy"
    assert session.current_section_index == 0  # Stayed in section 1 to ensure mastery
