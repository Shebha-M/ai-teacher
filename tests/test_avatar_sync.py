"""Unit and integration tests for Phase 7: Human-Like AI Teacher Avatar & Voice Synchronization."""
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from ai_engine.schemas.scene import TeachingScene, TeacherEmotion, VisualSpecification, VisualType
from ai_engine.schemas.avatar import (
    AvatarState,
    MouthState,
    EyeState,
    AvatarGesture,
    HeadMotion,
    TimingMode,
)
from ai_engine.schemas.language import AudioAsset, SubtitleSegment
from ai_engine.modules.avatar_controller import AvatarController
from ai_engine.modules.session_orchestrator import TeachingSessionOrchestrator
from ai_engine.modules.learner_profiler import LearnerProfiler


@pytest.fixture
def sample_teaching_scene():
    """Create a sample TeachingScene for avatar testing."""
    return TeachingScene(
        scene_id="scn-test-01",
        section_id="sec-1",
        scene_index=1,
        concept="Binary Search Trees",
        scene_type="visual_explanation",
        narration="Look closely at the Root Node 50 of the Binary Tree.",
        onscreen_text="Root Node: 50",
        teacher_action="point_to_visual",
        teacher_emotion=TeacherEmotion.EXPLAINING,
        visual_specification=VisualSpecification(
            visual_type=VisualType.TREE_DIAGRAM,
            is_deterministic=True,
            render_engine="svg",
            title="Binary Search Tree",
            description="Root Node 50 with left child 25 and right child 75",
        ),
        estimated_duration=6.0,
    )


def test_avatar_state_schema():
    """Test 1: AvatarState schema validation and defaults."""
    state = AvatarState(
        emotion=TeacherEmotion.WELCOMING,
        speaking=True,
        mouth_state=MouthState.OPEN,
        eye_state=EyeState.OPEN,
        head_motion=HeadMotion.NOD,
        gesture=AvatarGesture.WELCOME,
        speaking_progress=0.45,
        scene_action="welcome",
        timing_mode=TimingMode.WORD_CUES,
        reduced_motion=False,
        active_word="welcome",
    )
    assert state.emotion == TeacherEmotion.WELCOMING
    assert state.speaking is True
    assert state.mouth_state == MouthState.OPEN
    assert state.gesture == AvatarGesture.WELCOME
    assert state.active_word == "welcome"
    dump = state.model_dump()
    assert dump["timing_mode"] == "word_cues"


def test_emotion_mapping():
    """Test 2: TeacherEmotion produces correct presentation profile and head posture."""
    # Welcoming
    wel = AvatarController.map_emotion_profile(TeacherEmotion.WELCOMING)
    assert wel["emotion"] == TeacherEmotion.WELCOMING
    assert wel["gesture"] == AvatarGesture.WELCOME
    assert wel["head_motion"] == HeadMotion.NOD

    # Thoughtful
    thk = AvatarController.map_emotion_profile(TeacherEmotion.THOUGHTFUL)
    assert thk["emotion"] == TeacherEmotion.THOUGHTFUL
    assert thk["gesture"] == AvatarGesture.THINK
    assert thk["head_motion"] == HeadMotion.TILT_THOUGHTFUL

    # Celebrating
    cel = AvatarController.map_emotion_profile(TeacherEmotion.CELEBRATING)
    assert cel["emotion"] == TeacherEmotion.CELEBRATING
    assert cel["gesture"] == AvatarGesture.CELEBRATE
    assert cel["head_motion"] == HeadMotion.NOD


def test_teacher_action_mapping():
    """Test 3: Scene actions map to appropriate directional body gestures."""
    assert AvatarController.map_action_to_gesture("welcome") == AvatarGesture.WELCOME
    assert AvatarController.map_action_to_gesture("point_to_visual") == AvatarGesture.POINT_VISUAL
    assert AvatarController.map_action_to_gesture("trace_tree") == AvatarGesture.POINT_VISUAL
    assert AvatarController.map_action_to_gesture("point_left") == AvatarGesture.POINT_LEFT
    assert AvatarController.map_action_to_gesture("point_right") == AvatarGesture.POINT_RIGHT
    assert AvatarController.map_action_to_gesture("ask_question") == AvatarGesture.THINK
    assert AvatarController.map_action_to_gesture("encourage") == AvatarGesture.ENCOURAGE
    assert AvatarController.map_action_to_gesture("celebrate") == AvatarGesture.CELEBRATE


def test_word_cue_mouth_synchronization():
    """Test 4: High-precision word cues map timestamps to viseme states."""
    word_cues = [
        {"text": "Look", "start": 0.0, "end": 0.5},
        {"text": "closely", "start": 0.6, "end": 1.2},
    ]

    # At t=0.1s (progress 20% into "Look") -> OPEN
    vis_open = AvatarController.calculate_mouth_state(0.1, is_playing=True, word_cues=word_cues)
    assert vis_open["mouth_state"] == MouthState.OPEN
    assert vis_open["active_word"] == "Look"
    assert vis_open["timing_mode"] == TimingMode.WORD_CUES

    # At t=0.25s (progress 50% into "Look") -> HALF_OPEN
    vis_half = AvatarController.calculate_mouth_state(0.25, is_playing=True, word_cues=word_cues)
    assert vis_half["mouth_state"] == MouthState.HALF_OPEN

    # At t=0.42s (progress 84% into "Look") -> NARROW
    vis_narrow = AvatarController.calculate_mouth_state(0.42, is_playing=True, word_cues=word_cues)
    assert vis_narrow["mouth_state"] == MouthState.NARROW

    # At t=0.55s (in gap between words) -> REST
    vis_gap = AvatarController.calculate_mouth_state(0.55, is_playing=True, word_cues=word_cues)
    assert vis_gap["mouth_state"] == MouthState.REST
    assert vis_gap["active_word"] is None


def test_sentence_cue_fallback_synchronization():
    """Test 5: Fallback to sentence-level cues when word cues are absent."""
    subtitles = [
        SubtitleSegment(id=1, start_time=0.0, end_time=3.0, text="A Binary Tree has at most two children.")
    ]

    # During sentence speech
    vis_sentence = AvatarController.calculate_mouth_state(
        0.05, is_playing=True, word_cues=[], subtitles=subtitles, total_duration=3.0
    )
    assert vis_sentence["timing_mode"] == TimingMode.SENTENCE_CUES
    assert vis_sentence["mouth_state"] in [MouthState.OPEN, MouthState.HALF_OPEN, MouthState.NARROW]


def test_pause_and_idle_behavior(sample_teaching_scene):
    """Test 6: When audio is paused, avatar instantly returns to REST and speaking=False."""
    # Playing at t=1.0s
    state_playing = AvatarController.get_avatar_state_for_scene(
        scene=sample_teaching_scene, playback_time=1.0, is_playing=True
    )
    assert state_playing.speaking is True

    # Paused at t=1.0s
    state_paused = AvatarController.get_avatar_state_for_scene(
        scene=sample_teaching_scene, playback_time=1.0, is_playing=False
    )
    assert state_paused.speaking is False
    assert state_paused.mouth_state == MouthState.REST


def test_checkpoint_thinking_behavior(sample_teaching_scene):
    """Test 7: Checkpoint scenes override avatar into thoughtful thinking posture with halted audio."""
    sample_teaching_scene.is_checkpoint = True
    sample_teaching_scene.teacher_action = "ask_question"

    state_checkpoint = AvatarController.get_avatar_state_for_scene(
        scene=sample_teaching_scene, playback_time=0.0, is_playing=True, is_checkpoint=True
    )
    assert state_checkpoint.speaking is False
    assert state_checkpoint.mouth_state == MouthState.REST
    assert state_checkpoint.emotion == TeacherEmotion.THOUGHTFUL
    assert state_checkpoint.gesture == AvatarGesture.THINK
    assert state_checkpoint.head_motion == HeadMotion.TILT_THOUGHTFUL


def test_adaptive_remediation_presentation(sample_teaching_scene):
    """Test 8: Remediation scenes switch avatar to encouraging posture with supportive head nod."""
    sample_teaching_scene.scene_type = "adaptive_remediation"
    sample_teaching_scene.teacher_action = "remediate"

    state_remed = AvatarController.get_avatar_state_for_scene(
        scene=sample_teaching_scene, playback_time=0.5, is_playing=True, is_remediation=True
    )
    assert state_remed.emotion == TeacherEmotion.ENCOURAGING
    assert state_remed.gesture == AvatarGesture.ENCOURAGE
    assert state_remed.head_motion == HeadMotion.NOD


def test_reduced_motion_accessibility(sample_teaching_scene):
    """Test 9: Reduced-motion accessibility mode stabilizes head motion and blinks."""
    state_normal = AvatarController.get_avatar_state_for_scene(
        scene=sample_teaching_scene, playback_time=3.4, is_playing=True, reduced_motion=False
    )
    # At t=3.4s normal eye blinks
    assert state_normal.eye_state == EyeState.BLINK

    state_reduced = AvatarController.get_avatar_state_for_scene(
        scene=sample_teaching_scene, playback_time=3.4, is_playing=True, reduced_motion=True
    )
    # Reduced motion keeps eyes steady open and head motion neutral
    assert state_reduced.reduced_motion is True
    assert state_reduced.eye_state == EyeState.OPEN
    assert state_reduced.head_motion == HeadMotion.NEUTRAL


@pytest.mark.asyncio
async def test_api_avatar_state_endpoint():
    """Test 10: GET /api/v1/teaching/sessions/{id}/scenes/{scene_id}/avatar-state returns valid AvatarState."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Create session
        c_res = await client.post(
            "/api/v1/teaching/sessions",
            json={
                "topic": "Binary Trees",
                "learner_name": "Maya Lin",
                "educational_level": "intermediate",
                "available_learning_time": 15,
                "preferred_teaching_style": "analogy_driven",
                "preferred_language": "en",
            },
        )
        assert c_res.status_code == 201
        session_id = c_res.json()["session_id"]

        # Plan & generate scenes
        await client.post(f"/api/v1/teaching/sessions/{session_id}/plan")
        await client.post(f"/api/v1/teaching/sessions/{session_id}/explain")
        s_res = await client.post(f"/api/v1/teaching/sessions/{session_id}/scenes")
        assert s_res.status_code == 200
        plan_data = s_res.json()
        scene_1_id = plan_data["scenes"][0]["scene_id"]

        # Request avatar state
        av_res = await client.get(
            f"/api/v1/teaching/sessions/{session_id}/scenes/{scene_1_id}/avatar-state?playback_time=1.5&is_playing=true"
        )
        assert av_res.status_code == 200
        av_state = av_res.json()
        assert "emotion" in av_state
        assert "mouth_state" in av_state
        assert "gesture" in av_state
        assert av_state["speaking"] is True
