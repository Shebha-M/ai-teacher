"""Comprehensive tests for document-grounded general topics, relevance safeguards, and neutral fallbacks."""
import pytest
from ai_engine.schemas.learner import LearnerProfileSchema, LearnerLevel, TeachingStyle
from ai_engine.schemas.grounding import (
    KnowledgeMode,
    DocumentChunkSchema,
    RetrievedChunkSchema,
    CitationSchema,
    GroundedContextSchema,
)
from ai_engine.schemas.question import QuestionType
from ai_engine.schemas.evaluation import CorrectnessLevel
from ai_engine.modules.lesson_planner import LessonPlanner
from ai_engine.modules.teaching_agent import TeachingAgent
from ai_engine.modules.question_generator import QuestionGenerator
from ai_engine.modules.answer_evaluator import AnswerEvaluator
from ai_engine.modules.visual_planner import VisualPlanner
from ai_engine.schemas.question import StudentResponseSchema
from ai_engine.schemas.assessment import FinalAssessmentSchema
from ai_engine.rag.concept_extractor import extract_document_curriculum_concepts
from ai_engine.rag.vector_store import LocalVectorStore
from ai_engine.rag.retriever import HybridRetriever
from ai_engine.providers.mock_provider import DeterministicTeachingProvider


@pytest.fixture
def learner_profile():
    return LearnerProfileSchema(
        learner_id="test-learner-1",
        name="Alex",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=15,
        preferred_teaching_style=TeachingStyle.ANALOGY_DRIVEN,
        preferred_language="en",
        learning_objective="Master attendance logging and leave policies",
    )


@pytest.fixture
def attendance_grounded_context():
    chunks = [
        RetrievedChunkSchema(
            chunk_id="chk-att-1",
            document_id="doc-att",
            filename="Shebha_–_Attendance_&_Time-Off_task.txt",
            chunk_index=0,
            text_content=(
                "Check-in and check-out tracking: Employees can clock in and out with a live clock and active work timer.\n"
                "Work-hours calculation: System automatically calculates daily and weekly work hours.\n"
                "Time-off balances: Employees can view their leave balances (vacation, sick leave, personal).\n"
                "Leave request and approval workflow: Employees submit requests with date range and reason. "
                "HR dashboard allows managers to review, approve, or reject requests with immediate status transitions."
            ),
            hybrid_score=0.88,
            citation="Source: Shebha_–_Attendance_&_Time-Off_task.txt, Sec. 1",
        ),
        RetrievedChunkSchema(
            chunk_id="chk-att-2",
            document_id="doc-att",
            filename="Shebha_–_Attendance_&_Time-Off_task.txt",
            chunk_index=1,
            text_content=(
                "Attendance.jsx: Main dashboard for attendance logging and weekly summary grid.\n"
                "CheckInWidget.jsx: Active timer and punch card widget storing records in localStorage.\n"
                "TimeOff.jsx: Leave request modal and category balance cards.\n"
                "Remaining limitations: Graphical leave calendar view and medical attachment inputs."
            ),
            hybrid_score=0.74,
            citation="Source: Shebha_–_Attendance_&_Time-Off_task.txt, Sec. 2",
        ),
    ]
    citations = [
        CitationSchema(
            source_id="chk-att-1",
            filename="Shebha_–_Attendance_&_Time-Off_task.txt",
            location="Sec. 1",
            excerpt="Check-in and check-out tracking with live clock and active work timer.",
        ),
        CitationSchema(
            source_id="chk-att-2",
            filename="Shebha_–_Attendance_&_Time-Off_task.txt",
            location="Sec. 2",
            excerpt="Attendance.jsx and CheckInWidget.jsx component architecture.",
        ),
    ]
    return GroundedContextSchema(
        query="Attendance & Time-Off",
        knowledge_mode=KnowledgeMode.DOCUMENT,
        retrieved_chunks=chunks,
        source_documents=["doc-att"],
        citations=citations,
        confidence_score=0.88,
        insufficient_grounding=False,
        document_relevance="HIGH",
        synthesized_context=f"[{chunks[0].citation}]\n{chunks[0].text_content}\n\n[{chunks[1].citation}]\n{chunks[1].text_content}",
    )


@pytest.mark.asyncio
async def test_document_grounded_curriculum_concept_extraction(attendance_grounded_context, learner_profile):
    """Verify document extractor creates authentic, grounded sections from document text."""
    sections = extract_document_curriculum_concepts(
        grounded_context=attendance_grounded_context,
        time_limit=15,
        topic="Attendance & Time-Off",
        level=learner_profile.educational_level,
    )
    assert len(sections) >= 2
    full_text = " ".join([f"{s.concept} {s.title} {s.objective} {s.explanation_outline}" for s in sections]).lower()

    # Must contain authentic attendance concepts
    assert any(w in full_text for w in ["check-in", "work timer", "time-off", "leave", "attendance"])

    # Must NOT contain any data structure terms
    forbidden = ["traversal", "binary tree", "left child", "right child", "heap", "alternative data structures", "binary search"]
    for word in forbidden:
        assert word not in full_text, f"Forbidden term '{word}' leaked into document curriculum!"


@pytest.mark.asyncio
async def test_lesson_planner_in_document_mode(attendance_grounded_context, learner_profile):
    """Verify LessonPlanner generates document-grounded title and objectives without tree leakage."""
    planner = LessonPlanner()
    plan = await planner.plan_lesson(
        topic="Attendance & Time-Off",
        profile=learner_profile,
        grounded_context=attendance_grounded_context,
    )

    assert "Grounded in Shebha_–_Attendance_&_Time-Off_task.txt" in plan.lesson_title
    assert len(plan.sections) >= 2

    for sec in plan.sections:
        sec_text = f"{sec.concept} {sec.title} {sec.objective} {sec.explanation_outline}".lower()
        assert "binary tree" not in sec_text
        assert "traversal & operations" not in sec_text
        assert "alternative data structures" not in sec_text


@pytest.mark.asyncio
async def test_teaching_response_grounding(attendance_grounded_context, learner_profile):
    """Verify Teaching Agent produces document-grounded explanation, analogy, and visual."""
    planner = LessonPlanner()
    plan = await planner.plan_lesson(
        topic="Attendance & Time-Off",
        profile=learner_profile,
        grounded_context=attendance_grounded_context,
    )
    sec = plan.sections[0]

    agent = TeachingAgent()
    resp = await agent.explain_section(
        section=sec,
        profile=learner_profile,
        grounded_context=attendance_grounded_context,
    )

    resp_text = f"{resp.explanation} {resp.analogy} {resp.example} {resp.key_takeaway}".lower()
    assert "binary tree" not in resp_text
    assert "traversal" not in resp_text
    assert resp.key_takeaway is not None
    assert "Rule: Nodes have at most two children" not in resp.key_takeaway


@pytest.mark.asyncio
async def test_question_generator_and_evaluator_document_mode(attendance_grounded_context, learner_profile):
    """Verify checkpoint question and answer evaluation for document-grounded concepts."""
    planner = LessonPlanner()
    plan = await planner.plan_lesson(
        topic="Attendance & Time-Off",
        profile=learner_profile,
        grounded_context=attendance_grounded_context,
    )
    sec = plan.sections[0]

    q_gen = QuestionGenerator()
    q = await q_gen.generate_checkpoint_question(section=sec, profile=learner_profile, grounded_context=attendance_grounded_context)

    assert q.question_type == QuestionType.MULTIPLE_CHOICE
    assert q.expected_answer == "B"
    assert any("Shebha" in h for h in q.hints)

    # Test Correct Evaluation
    evaluator = AnswerEvaluator()
    student_resp_correct = StudentResponseSchema(
        response_id="resp-correct",
        question_id=q.question_id,
        student_answer="Option B: structured validation",
    )
    eval_res = await evaluator.evaluate_response(
        question=q,
        student_response=student_resp_correct,
        profile=learner_profile,
    )
    assert eval_res.correctness == CorrectnessLevel.CORRECT
    assert eval_res.score == 1.0

    # Test Misconception Evaluation
    student_resp_misc = StudentResponseSchema(
        response_id="resp-misc",
        question_id=q.question_id,
        student_answer="Option A: bypass authorization",
    )
    eval_misc = await evaluator.evaluate_response(
        question=q,
        student_response=student_resp_misc,
        profile=learner_profile,
    )
    assert eval_misc.correctness == CorrectnessLevel.INCORRECT_MISCONCEPTION
    assert "binary tree" not in (eval_misc.rubric_feedback or "").lower()


@pytest.mark.asyncio
async def test_visual_planner_neutrality(attendance_grounded_context, learner_profile):
    """Verify VisualPlanner produces no binary tree artifacts for attendance document."""
    planner = LessonPlanner()
    plan = await planner.plan_lesson(
        topic="Attendance & Time-Off",
        profile=learner_profile,
        grounded_context=attendance_grounded_context,
    )
    sec = plan.sections[0]

    agent = TeachingAgent()
    resp = await agent.explain_section(section=sec, profile=learner_profile, grounded_context=attendance_grounded_context)

    scene_plan = VisualPlanner.create_scene_plan(
        section=sec,
        teaching=resp,
        profile=learner_profile,
        grounded_context=attendance_grounded_context,
    )

    assert len(scene_plan.scenes) == 4
    # Scene 2 must not have hardcoded binary tree rule
    assert "Rule: Nodes have at most two children" not in scene_plan.scenes[1].onscreen_text

    # Scene 4 checkpoint must not have hardcoded binary tree prompt
    s4_prompt = scene_plan.scenes[3].visual_specification.data.get("checkpoint_prompt", "")
    assert "maximum number of children a node can possess in a Binary Tree" not in s4_prompt


@pytest.mark.asyncio
async def test_mismatched_topic_grounding_safeguard(attendance_grounded_context, learner_profile):
    """Verify system detects mismatch (Binary Trees + Attendance doc) and falls back safely."""
    # When topic is Binary Trees and document is Attendance, relevance is LOW
    mismatched_context = GroundedContextSchema(
        query="Binary Trees",
        knowledge_mode=KnowledgeMode.DOCUMENT,
        retrieved_chunks=attendance_grounded_context.retrieved_chunks,
        source_documents=["doc-att"],
        citations=attendance_grounded_context.citations,
        confidence_score=0.12,
        insufficient_grounding=True,
        document_relevance="LOW",
        synthesized_context="",
    )

    planner = LessonPlanner()
    plan = await planner.plan_lesson(
        topic="Binary Trees",
        profile=learner_profile,
        grounded_context=mismatched_context,
    )

    # Should retain Binary Tree curriculum and NOT hallucinate attendance concepts into trees
    full_text = " ".join([f"{s.concept} {s.title}" for s in plan.sections]).lower()
    assert "binary tree" in plan.topic.lower()
    assert "attendance" not in full_text


@pytest.mark.asyncio
async def test_general_topic_without_document(learner_profile):
    """Verify general topic without document (Agile Project Management) has zero data structure leakage."""
    planner = LessonPlanner()
    plan = await planner.plan_lesson(
        topic="Agile Project Management",
        profile=learner_profile,
        grounded_context=None,
    )

    full_text = " ".join([f"{s.concept} {s.title} {s.objective} {s.explanation_outline}" for s in plan.sections]).lower()
    forbidden = ["traversal", "binary tree", "left child", "right child", "heap", "alternative data structures"]
    for word in forbidden:
        assert word not in full_text, f"Forbidden word '{word}' found in general topic curriculum!"


@pytest.mark.asyncio
async def test_final_assessment_neutrality(learner_profile):
    """Verify final assessment produces domain-neutral options for general topics."""
    provider = DeterministicTeachingProvider()
    asmt = await provider.generate_structured(
        prompt="Generate final assessment for topic 'Agile Project Management'.",
        response_schema=FinalAssessmentSchema,
        topic="Agile Project Management",
        profile=learner_profile,
        session_id="sess-test",
    )

    assert len(asmt.questions) >= 2
    for q in asmt.questions:
        for opt in q.options:
            opt_text = opt.text.lower()
            assert "hierarchical" not in opt_text
            assert "sequential search only" not in opt_text


@pytest.mark.asyncio
async def test_vector_store_sqlite_hydration():
    """Verify LocalVectorStore automatically hydrates chunks from SQLite if in-memory store is empty."""
    store = LocalVectorStore()
    # Ensure memory is empty initially
    store._entries = {}

    # Query existing document doc-bb138b9b
    chunks = await store.get_document_chunks("doc-bb138b9b")
    assert len(chunks) >= 1, "Expected at least 1 chunk hydrated from SQLite database"
    assert chunks[0].document_id == "doc-bb138b9b"
