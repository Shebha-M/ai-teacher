"""Automated tests for Phase 5: AI Teaching Video and Subject-Aware Visuals."""
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from ai_engine.schemas.learner import LearnerLevel, TeachingStyle
from ai_engine.schemas.scene import VisualType, TeacherEmotion, TeachingScenePlan, TeachingScene
from ai_engine.schemas.grounding import CitationSchema, GroundedContextSchema
from ai_engine.modules.visual_planner import VisualPlanner
from ai_engine.modules.learner_profiler import LearnerProfiler
from ai_engine.modules.session_orchestrator import TeachingSessionOrchestrator


@pytest.mark.asyncio
async def test_visual_planner_subject_awareness():
    """Verify that VisualPlanner infers academic domain and assigns appropriate visual representation."""
    # Data Structures / CS -> TREE_DIAGRAM
    spec_tree = VisualPlanner.determine_visual_specification("Binary Trees", "Computer Science")
    assert spec_tree.visual_type == VisualType.TREE_DIAGRAM
    assert spec_tree.is_deterministic is True
    assert "root" in spec_tree.data
    assert spec_tree.data["root"]["val"] == 50

    # Physics -> CIRCUIT_DIAGRAM
    spec_phys = VisualPlanner.determine_visual_specification("Ohm's Law", "Electronics")
    assert spec_phys.visual_type == VisualType.CIRCUIT_DIAGRAM
    assert spec_phys.is_deterministic is True
    assert "formula" in spec_phys.data
    assert "I = V / R" in spec_phys.data["formula"]

    # Programming -> CODE
    spec_prog = VisualPlanner.determine_visual_specification("Recursion Depth", "Python Programming")
    assert spec_prog.visual_type == VisualType.CODE
    assert spec_prog.is_deterministic is True
    assert "language" in spec_prog.data
    assert spec_prog.data["language"] == "python"

    # Mathematics -> EQUATION
    spec_math = VisualPlanner.determine_visual_specification("Balance Factor Derivation", "Calculus and Algebra")
    assert spec_math.visual_type == VisualType.EQUATION
    assert spec_math.is_deterministic is True
    assert "latex_equation" in spec_math.data

    # General -> FLOWCHART
    spec_gen = VisualPlanner.determine_visual_specification("General Study Strategy", "Study Skills")
    assert spec_gen.visual_type == VisualType.FLOWCHART
    assert spec_gen.is_deterministic is True


@pytest.mark.asyncio
async def test_scene_plan_generation_structure():
    """Verify that a teaching response produces a valid, 4-scene video plan with synchronized assets."""
    orchestrator = TeachingSessionOrchestrator()
    profile = orchestrator.profiler.create_profile(
        name="Alex",
        educational_level=LearnerLevel.BEGINNER,
        available_learning_time=15,
        preferred_teaching_style=TeachingStyle.ANALOGY_DRIVEN,
    )

    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)
    await orchestrator.plan_session(session)
    await orchestrator.teach_current_section(session)

    scene_plan = await orchestrator.generate_scene_plan(session)

    assert isinstance(scene_plan, TeachingScenePlan)
    assert len(scene_plan.scenes) == 4
    assert scene_plan.total_duration_estimate > 40.0

    # Scene 1: Intro
    assert scene_plan.scenes[0].scene_type == "intro"
    assert scene_plan.scenes[0].teacher_emotion == TeacherEmotion.WELCOMING
    assert scene_plan.scenes[0].is_checkpoint is False

    # Scene 2: Core Visual Diagram
    assert scene_plan.scenes[1].scene_type == "visual_explanation"
    assert scene_plan.scenes[1].visual_specification.visual_type == VisualType.TREE_DIAGRAM

    # Scene 3: Analogy Walkthrough
    assert scene_plan.scenes[2].scene_type == "analogy_walkthrough"
    assert scene_plan.scenes[2].teacher_action in ["trace_visual", "point_to_visual"]

    # Scene 4: Question Checkpoint
    assert scene_plan.scenes[3].scene_type == "checkpoint_prompt"
    assert scene_plan.scenes[3].is_checkpoint is True
    assert scene_plan.scenes[3].branch_target_if_struggling is not None


@pytest.mark.asyncio
async def test_rag_source_attribution_preservation_in_scenes():
    """Verify that verified source citations from Phase 3 RAG are preserved in scene references."""
    orchestrator = TeachingSessionOrchestrator()
    profile = orchestrator.profiler.create_profile(name="Jordan")
    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)
    await orchestrator.plan_session(session)
    await orchestrator.teach_current_section(session)

    # Attach mock grounded context
    session.grounded_context = GroundedContextSchema(
        knowledge_mode="document",
        query="Binary Trees",
        document_id="doc-test-123",
        citations=[
            CitationSchema(
                source_id="doc-test-123",
                filename="Binary_Trees_Lecture.pdf",
                location="Page 3",
                excerpt="A binary tree node can have at most two child nodes.",
            )
        ],
        synthesized_context="A binary tree node can have at most two child nodes.",
        retrieval_confidence=0.95,
        insufficient_grounding=False,
    )

    plan = await orchestrator.generate_scene_plan(session, force_regenerate=True)
    # Check that Scene 2 has citations preserved
    assert len(plan.scenes[1].source_references) >= 1
    assert plan.scenes[1].source_references[0].filename == "Binary_Trees_Lecture.pdf"
    assert plan.scenes[1].source_references[0].location == "Page 3"


@pytest.mark.asyncio
async def test_adaptive_scene_branching_on_struggle():
    """Verify that when a learner struggles, an adaptive remediation scene is generated and inserted."""
    orchestrator = TeachingSessionOrchestrator()
    profile = orchestrator.profiler.create_profile(name="Sam")
    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)
    await orchestrator.plan_session(session)
    await orchestrator.teach_current_section(session)

    # First generate standard plan
    standard_plan = await orchestrator.generate_scene_plan(session)
    initial_scene_count = len(standard_plan.scenes)

    # Trigger evaluation with misconception
    question = await orchestrator.get_checkpoint_question(session)
    await orchestrator.process_student_response(
        session=session,
        student_answer="A binary tree node can have 4 children as long as it is balanced.",
    )

    # Generate remediation scene
    remediation_scene = await orchestrator.create_adaptive_remediation_scene(session)

    assert isinstance(remediation_scene, TeachingScene)
    assert remediation_scene.scene_type == "adaptive_remediation"
    assert remediation_scene.teacher_emotion == TeacherEmotion.ENCOURAGING
    assert "counter_analogy" in remediation_scene.visual_specification.data

    # Verify scene was inserted into active scene plan
    sec_id = session.current_section_id
    cache_key = f"{session.session_id}_{sec_id}"
    updated_plan = orchestrator.scene_plans_cache[cache_key]
    assert len(updated_plan.scenes) == initial_scene_count + 1
    assert updated_plan.is_adaptive_branch is True


@pytest.mark.asyncio
async def test_media_api_endpoints():
    """Test FastAPI REST endpoints for scene planning, rendering, and branching."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Create teaching session
        create_resp = await client.post(
            "/api/v1/teaching/sessions",
            json={
                "topic": "Binary Trees",
                "learner_name": "API Tester",
                "educational_level": "beginner",
                "available_learning_time": 15,
                "preferred_teaching_style": "analogy_driven",
            },
        )
        assert create_resp.status_code == 201
        sess_data = create_resp.json()
        session_id = sess_data["session_id"]

        # 2. Plan session
        plan_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/plan")
        assert plan_resp.status_code == 200

        # 3. Request Scene Plan
        scenes_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/scenes")
        assert scenes_resp.status_code == 200
        scene_plan = scenes_resp.json()
        assert "scenes" in scene_plan
        assert len(scene_plan["scenes"]) == 4

        scene_1_id = scene_plan["scenes"][0]["scene_id"]

        # 4. Render Scene Media
        render_resp = await client.post(
            f"/api/v1/teaching/sessions/{session_id}/scenes/{scene_1_id}/render"
        )
        assert render_resp.status_code == 200
        render_data = render_resp.json()
        assert "audio_stream_mock" in render_data
        assert "avatar_animation" in render_data
        assert "visual_specification" in render_data

        # 5. Test Branching endpoint
        branch_resp = await client.post(f"/api/v1/teaching/sessions/{session_id}/branch")
        assert branch_resp.status_code == 200
        branch_data = branch_resp.json()
        assert branch_data["scene_type"] == "adaptive_remediation"
