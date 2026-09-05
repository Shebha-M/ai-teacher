"""Automated unit and integration tests for Phase 6: Multilingual Teaching and Voice Engine."""
import pytest
import os
from httpx import AsyncClient, ASGITransport

from backend.main import app
from ai_engine.schemas.language import (
    LanguageCode,
    LanguageMode,
    VoiceMetadata,
    LanguageDecision,
)
from ai_engine.schemas.scene import TeachingScene, VisualSpecification, VisualType, TeacherEmotion
from ai_engine.schemas.question import QuestionSchema, QuestionType
from ai_engine.schemas.grounding import CitationSchema
from ai_engine.modules.language_controller import LanguageController
from ai_engine.modules.session_orchestrator import TeachingSessionOrchestrator
from ai_engine.providers.speech_provider import MockSpeechProvider, EdgeTTSProvider


@pytest.mark.asyncio
async def test_language_resolution_and_fallbacks():
    """Verify supported language codes resolve correctly and unsupported fall back to English."""
    # Direct codes
    for code in ["en", "hi", "ta", "te", "ml", "kn"]:
        dec = LanguageController.resolve_language(code)
        assert dec.resolved_language == LanguageCode(code)
        assert not dec.fallback_used

    # Aliases
    dec_hi = LanguageController.resolve_language("Hindi")
    assert dec_hi.resolved_language == LanguageCode.HI
    dec_ta = LanguageController.resolve_language("tamil")
    assert dec_ta.resolved_language == LanguageCode.TA

    # Unsupported fallback
    dec_unknown = LanguageController.resolve_language("klingon", fallback_code="en")
    assert dec_unknown.resolved_language == LanguageCode.EN
    assert dec_unknown.fallback_used is True


@pytest.mark.asyncio
async def test_voice_catalog_filtering():
    """Verify voice catalog provides default voices and filters by language."""
    voices = LanguageController.get_available_voices()
    assert len(voices) >= 12

    hi_voices = LanguageController.get_available_voices("hi")
    assert len(hi_voices) >= 2
    assert all(v.language_code == LanguageCode.HI for v in hi_voices)

    ta_default = LanguageController.get_default_voice("ta")
    assert "ta-IN" in ta_default


@pytest.mark.asyncio
async def test_bilingual_mode_preserves_technical_terms():
    """Verify that in bilingual mode, critical CS/engineering technical terms remain in English."""
    scene = TeachingScene(
        scene_id="test-scn",
        section_id="test-sec",
        concept="Binary Tree",
        scene_type="visual_explanation",
        narration="In a Binary Tree, each node has a Root Node, Left Child and Right Child.",
        onscreen_text="Binary Tree basics",
        teacher_emotion=TeacherEmotion.EXPLAINING,
        visual_specification=VisualSpecification(
            visual_type=VisualType.TREE_DIAGRAM,
            title="Binary Tree",
            description="Test tree",
        ),
    )

    # Hindi Bilingual
    hi_loc = LanguageController.localize_scene_narration(scene, target_lang="hi", mode="bilingual")
    assert "Root Node" in hi_loc["narration"]
    assert "Left Child" in hi_loc["narration"]
    assert "Right Child" in hi_loc["narration"]
    assert hi_loc["language"] == "hi"

    # Tamil Bilingual
    ta_loc = LanguageController.localize_scene_narration(scene, target_lang="ta", mode="bilingual")
    assert "Root Node" in ta_loc["narration"]
    assert "Binary Tree" in ta_loc["narration"]
    assert ta_loc["language"] == "ta"


@pytest.mark.asyncio
async def test_rag_source_metadata_preservation_across_languages():
    """Verify that translating a scene does not corrupt or alter underlying RAG document citations."""
    orchestrator = TeachingSessionOrchestrator()
    profile = orchestrator.profiler.create_profile(name="Kavya", preferred_language="en")
    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)
    await orchestrator.plan_session(session)
    await orchestrator.teach_current_section(session)

    plan = await orchestrator.generate_scene_plan(session)
    # Add a mock citation
    plan.scenes[1].source_references = [
        CitationSchema(
            source_id="doc-btree",
            filename="Binary_Trees_Lecture.md",
            location="Page 3",
            excerpt="In a binary tree, maximum out-degree is 2.",
        )
    ]

    # Switch language to Tamil
    await orchestrator.switch_session_language(session, new_language="ta")
    switched_plan = await orchestrator.generate_scene_plan(session)

    # Verify citation remains identical
    cites = switched_plan.scenes[1].source_references
    assert len(cites) == 1
    assert cites[0].filename == "Binary_Trees_Lecture.md"
    assert cites[0].location == "Page 3"
    assert cites[0].excerpt == "In a binary tree, maximum out-degree is 2."
    assert switched_plan.scenes[1].language == "ta"


@pytest.mark.asyncio
async def test_context_preserving_language_switch():
    """
    CRITICAL TEST: Switching language mid-lesson must NOT reset section index,
    concept mastery, topic, or lesson plan.
    """
    orchestrator = TeachingSessionOrchestrator()
    profile = orchestrator.profiler.create_profile(name="Arjun", preferred_language="en")
    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)

    await orchestrator.plan_session(session)
    await orchestrator.teach_current_section(session)

    # Initial state
    initial_topic = session.current_topic
    initial_sec_idx = session.current_section_index
    initial_sec_id = session.current_section_id
    initial_plan_len = len(session.lesson_plan.sections)

    # 1. Switch to Tamil
    await orchestrator.switch_session_language(session, new_language="ta")
    assert session.teaching_language == "ta"
    assert session.current_topic == initial_topic
    assert session.current_section_index == initial_sec_idx
    assert session.current_section_id == initial_sec_id
    assert len(session.lesson_plan.sections) == initial_plan_len

    # 2. Switch to Hindi
    await orchestrator.switch_session_language(session, new_language="hi")
    assert session.teaching_language == "hi"
    assert session.current_topic == initial_topic
    assert session.current_section_index == initial_sec_idx
    assert session.current_section_id == initial_sec_id
    assert len(session.lesson_plan.sections) == initial_plan_len


@pytest.mark.asyncio
async def test_multilingual_question_and_remediation():
    """Verify questions localize and student misconceptions trigger localized remediation scenes."""
    orchestrator = TeachingSessionOrchestrator()
    profile = orchestrator.profiler.create_profile(name="Meera", preferred_language="ta")
    session = orchestrator.initialize_session(topic="Binary Trees", learner_profile=profile)

    await orchestrator.plan_session(session)
    await orchestrator.teach_current_section(session)
    await orchestrator.generate_scene_plan(session)

    # Get checkpoint question in Tamil
    q = await orchestrator.get_checkpoint_question(session)
    assert q is not None
    # Verify prompt is in Tamil
    assert any("\u0b80" <= ch <= "\u0bff" for ch in q.prompt)

    # Student submits misconception answer
    wrong_answer = "நான்கு கிளைகள் இருக்கலாம்"  # "Can have 4 branches"
    outcome = await orchestrator.process_student_response(session, wrong_answer)
    assert outcome["evaluation"] is not None

    # Generate adaptive remediation scene
    rem = await orchestrator.create_adaptive_remediation_scene(session)
    assert rem.scene_type == "adaptive_remediation"
    assert rem.language == "ta"
    # Verify Tamil characters in remediation narration
    assert any("\u0b80" <= ch <= "\u0bff" for ch in rem.narration)


@pytest.mark.asyncio
async def test_speech_providers():
    """Verify MockSpeechProvider and EdgeTTSProvider synthesize audio and subtitles."""
    mock = MockSpeechProvider()
    asset = await mock.synthesize_speech_asset(
        text="Welcome to our lesson on Binary Trees. Let us explore the root node.",
        language="en",
    )
    assert asset.asset_id.startswith("audio-mock-")
    assert asset.duration_seconds > 0
    assert len(asset.subtitles) >= 1
    assert asset.provider_type == "mock"

    # Test EdgeTTSProvider (either online or fallback to mock)
    edge = EdgeTTSProvider()
    edge_asset = await edge.synthesize_speech_asset(
        text="नमस्ते! बाइनरी ट्री में आपका स्वागत है।",
        language="hi",
    )
    assert edge_asset.duration_seconds > 0
    assert len(edge_asset.subtitles) >= 1


@pytest.mark.asyncio
async def test_multilingual_rest_api():
    """Verify REST endpoints for language catalog, voice catalog, language switching, and speech."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Languages
        resp_lang = await client.get("/api/v1/media/languages")
        assert resp_lang.status_code == 200
        langs = resp_lang.json()
        assert len(langs) >= 6
        codes = [l["code"] for l in langs]
        assert "hi" in codes and "ta" in codes and "en" in codes

        # 2. Voices
        resp_voices = await client.get("/api/v1/media/voices?language=ta")
        assert resp_voices.status_code == 200
        voices = resp_voices.json()
        assert len(voices) >= 2

        # 3. Create session & switch language
        create_resp = await client.post(
            "/api/v1/teaching/sessions",
            json={
                "topic": "Binary Trees",
                "learner_name": "Test Student",
                "educational_level": "beginner",
                "available_learning_time": 15,
                "preferred_language": "en",
            },
        )
        assert create_resp.status_code == 201
        sess_id = create_resp.json()["session_id"]

        await client.post(f"/api/v1/teaching/sessions/{sess_id}/plan")
        await client.post(f"/api/v1/teaching/sessions/{sess_id}/explain")
        await client.post(f"/api/v1/teaching/sessions/{sess_id}/scenes")

        # Switch language to Hindi mid-lesson
        switch_resp = await client.post(
            f"/api/v1/teaching/sessions/{sess_id}/language",
            json={"language": "hi", "mode": "bilingual"},
        )
        assert switch_resp.status_code == 200
        switched_sess = switch_resp.json()
        assert switched_sess["teaching_language"] == "hi"

        # Verify active scene is now localized in Hindi
        scenes_resp = await client.get(f"/api/v1/teaching/sessions/{sess_id}/scenes")
        assert scenes_resp.status_code == 200
        scene_data = scenes_resp.json()
        scene_1 = scene_data["scenes"][0]
        assert scene_1["language"] == "hi"
        assert any("\u0900" <= ch <= "\u097f" for ch in scene_1["narration"])

        # 4. Generate speech asset for scene 1
        speech_resp = await client.post(
            f"/api/v1/teaching/sessions/{sess_id}/scenes/{scene_1['scene_id']}/speech",
            json={"force_mock": True},
        )
        assert speech_resp.status_code == 200
        audio_asset = speech_resp.json()
        assert "audio_url" in audio_asset
        assert len(audio_asset["subtitles"]) >= 1

        # 5. Stream audio file
        audio_get = await client.get(audio_asset["audio_url"])
        assert audio_get.status_code == 200
