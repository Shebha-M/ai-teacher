"""Tests for Phase 8 Final Integration: Assessment, Learning Report, Dashboard, and Readiness."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from ai_engine.modules.session_orchestrator import TeachingSessionOrchestrator
from ai_engine.schemas.learner import LearnerProfileSchema, LearnerLevel, TeachingStyle
from ai_engine.schemas.assessment import AssessmentAnswerItem, FinalAssessmentSchema, LearningReportSchema


@pytest.mark.asyncio
async def test_readiness_endpoint():
    """Verify judge readiness endpoint returns operational status for all subsystems."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/readiness")
        assert res.status_code == 200
        data = res.json()
        assert data["system_ready"] is True
        assert data["overall_status"] == "OPERATIONAL"
        services = data["services"]
        assert "backend" in services and services["backend"]["status"] == "ready"
        assert "ai_engine" in services and services["ai_engine"]["status"] == "ready"
        assert "rag_engine" in services and services["rag_engine"]["status"] == "ready"
        assert "speech_provider" in services and services["speech_provider"]["status"] == "ready"
        assert "avatar_engine" in services and services["avatar_engine"]["status"] == "ready"


@pytest.mark.asyncio
async def test_final_assessment_generation_and_grading():
    """Verify final assessment generates 2-3 questions and grades answers accurately."""
    orchestrator = TeachingSessionOrchestrator()
    profile = orchestrator.profiler.create_profile(
        name="Alex Rivera",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=15,
        preferred_teaching_style=TeachingStyle.ANALOGY_DRIVEN,
        learning_objective="Master binary tree invariants",
    )

    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)
    session = await orchestrator.plan_session(session)

    # 1. Generate final assessment
    assessment = await orchestrator.generate_final_assessment(session)
    assert isinstance(assessment, FinalAssessmentSchema)
    assert len(assessment.questions) >= 2
    assert assessment.topic == "Binary Trees"

    # 2. Grade final assessment answers
    # Provide correct answers
    answers = [
        AssessmentAnswerItem(question_id=q.question_id, student_answer=q.expected_answer)
        for q in assessment.questions
    ]
    report = await orchestrator.evaluate_final_assessment(session, answers)

    assert isinstance(report, LearningReportSchema)
    assert report.overall_score_percent >= 80
    assert report.status in ["mastered", "completed"]
    assert len(report.concepts_understood) > 0
    assert report.recommended_revision != ""
    assert report.revision_reason != ""
    assert "Binary Search Tree" in report.next_topic_recommendation or "BST" in report.next_topic_recommendation
    assert report.next_topic_reason != ""


@pytest.mark.asyncio
async def test_learner_progress_dashboard():
    """Verify learner progress dashboard aggregates mastery, strengths, and recommendations."""
    orchestrator = TeachingSessionOrchestrator()
    profile = orchestrator.profiler.create_profile(
        name="Alex Rivera",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=15,
    )
    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)
    session = await orchestrator.plan_session(session)

    dashboard = orchestrator.get_learner_progress_dashboard(session)
    assert dashboard["learner_name"] == "Alex Rivera"
    assert dashboard["current_topic"] == "Binary Trees"
    assert "overall_mastery_percent" in dashboard
    assert "recommended_revision" in dashboard
    assert "next_topic" in dashboard
    assert isinstance(dashboard["recent_sessions"], list)
