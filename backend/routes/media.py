"""RESTful API endpoints for AI Teaching Video, Subject-Aware Visuals, and Multilingual Audio."""
import os
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.routes.teaching import ACTIVE_SESSIONS, orchestrator
from ai_engine.schemas.scene import TeachingScenePlan, TeachingScene
from ai_engine.schemas.session import TeachingSessionStateSchema
from ai_engine.schemas.language import (
    LanguageConfig,
    VoiceMetadata,
    AudioAsset,
)
from ai_engine.schemas.avatar import AvatarState
from ai_engine.modules.language_controller import LanguageController
from ai_engine.modules.avatar_controller import AvatarController
from ai_engine.providers.speech_provider import AUDIO_STORAGE_DIR

router = APIRouter(prefix="/api/v1/teaching/sessions", tags=["Teaching Video & Visuals"])
general_media_router = APIRouter(prefix="/api/v1/media", tags=["Media, Voices & Multilingual"])


class RenderSceneResponse(BaseModel):
    scene_id: str
    concept: str
    audio_stream_mock: str = Field(..., description="Base64 or URI for mock audio stream")
    audio_duration_seconds: float
    avatar_animation: dict = Field(..., description="Avatar face and lip-sync keyframes")
    visual_specification: dict = Field(..., description="Renderable visual specification")


class SwitchLanguageRequest(BaseModel):
    language: str = Field(..., description="Target language code: 'en', 'hi', 'ta', 'te', 'ml', 'kn'")
    mode: Optional[str] = Field("bilingual", description="Mode: 'full', 'bilingual', 'mixed'")
    voice_id: Optional[str] = Field(None, description="Optional preferred voice ID")


class GenerateSpeechRequest(BaseModel):
    voice_id: Optional[str] = None
    force_mock: bool = False


# ==============================================================================
# GENERAL MEDIA & VOICE CATALOG ENDPOINTS (/api/v1/media)
# ==============================================================================

@general_media_router.get("/languages", response_model=List[LanguageConfig])
async def list_supported_languages():
    """Retrieve all supported educational languages with script and default voice metadata."""
    return list(LanguageController.LANGUAGE_REGISTRY.values())


@general_media_router.get("/voices", response_model=List[VoiceMetadata])
async def list_available_voices(language: Optional[str] = Query(None, description="Filter by language code (e.g. 'hi', 'ta')")):
    """Retrieve catalog of neural and mock voices, optionally filtered by language."""
    return LanguageController.get_available_voices(language)


@general_media_router.get("/audio/{asset_id}")
async def stream_audio_file(asset_id: str):
    """Safely stream a synthesized speech audio asset file."""
    # Sanitize asset_id to prevent directory traversal
    safe_name = os.path.basename(asset_id)
    mp3_path = AUDIO_STORAGE_DIR / f"{safe_name}.mp3"
    wav_path = AUDIO_STORAGE_DIR / f"{safe_name}.wav"

    if mp3_path.exists():
        return FileResponse(path=str(mp3_path), media_type="audio/mpeg", filename=f"{safe_name}.mp3")
    elif wav_path.exists():
        return FileResponse(path=str(wav_path), media_type="audio/wav", filename=f"{safe_name}.wav")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio asset '{asset_id}' not found.",
        )


# ==============================================================================
# SESSION-SCOPED VIDEO & MULTILINGUAL ENDPOINTS (/api/v1/teaching/sessions)
# ==============================================================================

@router.post("/{session_id}/scenes", response_model=TeachingScenePlan)
async def generate_or_get_scene_plan(session_id: str, force_regenerate: bool = False):
    """
    Generate or retrieve the structured TeachingScenePlan for the session's active section.
    Returns 4 scenes (Intro, Visual Diagram, Walkthrough, Checkpoint).
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teaching session '{session_id}' not found.",
        )
    session = ACTIVE_SESSIONS[session_id]

    try:
        plan = await orchestrator.generate_scene_plan(session, force_regenerate=force_regenerate)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate teaching scene plan: {str(e)}",
        )


@router.get("/{session_id}/scenes", response_model=TeachingScenePlan)
async def get_current_scene_plan(session_id: str):
    """
    Retrieve the current TeachingScenePlan for the active lesson section.
    """
    return await generate_or_get_scene_plan(session_id, force_regenerate=False)


@router.post("/{session_id}/scenes/{scene_id}/render", response_model=RenderSceneResponse)
async def render_scene_media(session_id: str, scene_id: str):
    """
    Synthesize mock audio, avatar animation keyframes, and visual layout for a single scene.
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teaching session '{session_id}' not found.",
        )
    session = ACTIVE_SESSIONS[session_id]

    plan = await orchestrator.generate_scene_plan(session)
    target_scene: Optional[TeachingScene] = None
    for scn in plan.scenes:
        if scn.scene_id == scene_id:
            target_scene = scn
            break

    if not target_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene '{scene_id}' not found in active scene plan.",
        )

    # Generate speech audio
    audio_bytes = await orchestrator.provider.synthesize_speech(
        text=target_scene.narration,
        voice_id=session.active_voice_id or "default_teacher",
        language=session.teaching_language,
    )

    # Generate avatar animation frames
    avatar_frames = await orchestrator.provider.generate_avatar_frames(
        audio_bytes=audio_bytes,
        avatar_id="teacher_avatar_01",
    )

    return RenderSceneResponse(
        scene_id=target_scene.scene_id,
        concept=target_scene.concept,
        audio_stream_mock=audio_bytes.decode("utf-8", errors="ignore"),
        audio_duration_seconds=target_scene.estimated_duration,
        avatar_animation=avatar_frames,
        visual_specification=target_scene.visual_specification.model_dump(),
    )


@router.post("/{session_id}/scenes/{scene_id}/speech", response_model=AudioAsset)
async def synthesize_scene_speech(
    session_id: str, scene_id: str, req: Optional[GenerateSpeechRequest] = None
):
    """
    Synthesize real TTS audio (or deterministic fallback) for a scene's narration.
    Returns complete AudioAsset with duration and synchronized subtitle timing.
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teaching session '{session_id}' not found.",
        )
    session = ACTIVE_SESSIONS[session_id]

    plan = await orchestrator.generate_scene_plan(session)
    target_scene: Optional[TeachingScene] = None
    for scn in plan.scenes:
        if scn.scene_id == scene_id:
            target_scene = scn
            break

    if not target_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene '{scene_id}' not found in active scene plan.",
        )

    voice_id = (req.voice_id if req else None) or session.active_voice_id
    if req and req.force_mock:
        from ai_engine.providers.speech_provider import MockSpeechProvider
        provider = MockSpeechProvider()
    else:
        provider = orchestrator.speech_provider

    try:
        asset = await provider.synthesize_speech_asset(
            text=target_scene.narration,
            voice_id=voice_id,
            language=session.teaching_language,
            scene_id=scene_id,
            emotion=target_scene.teacher_emotion.value,
        )

        # Attach to target scene
        target_scene.audio_asset_id = asset.asset_id
        target_scene.audio_url = asset.audio_url
        target_scene.subtitles = [s.model_dump() for s in asset.subtitles]

        return asset
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to synthesize speech: {str(e)}",
        )


@router.post("/{session_id}/language", response_model=TeachingSessionStateSchema)
async def switch_language(session_id: str, req: SwitchLanguageRequest):
    """
    Switch presentation language mid-lesson without losing progress, section position,
    concept mastery, or RAG grounding.
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teaching session '{session_id}' not found.",
        )
    session = ACTIVE_SESSIONS[session_id]

    try:
        updated_session = await orchestrator.switch_session_language(
            session=session,
            new_language=req.language,
            mode=req.mode,
            voice_id=req.voice_id,
        )
        ACTIVE_SESSIONS[session_id] = updated_session
        return updated_session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to switch language: {str(e)}",
        )


@router.post("/{session_id}/branch", response_model=TeachingScene)
async def branch_adaptive_remediation(session_id: str):
    """
    Generate an adaptive remediation scene (e.g. Scene 3-R) when a student struggles at a checkpoint.
    Inserts the remediation scene into the video timeline before retry.
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teaching session '{session_id}' not found.",
        )
    session = ACTIVE_SESSIONS[session_id]

    try:
        remediation_scene = await orchestrator.create_adaptive_remediation_scene(session)
        return remediation_scene
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create adaptive remediation scene: {str(e)}",
        )


@router.get("/{session_id}/scenes/{scene_id}/avatar-state", response_model=AvatarState)
async def get_scene_avatar_state(
    session_id: str,
    scene_id: str,
    playback_time: float = Query(0.0, description="Current audio playback time in seconds"),
    is_playing: bool = Query(False, description="Whether audio is actively playing"),
    reduced_motion: bool = Query(False, description="Accessibility reduced-motion preference"),
):
    """
    Retrieve structured instantaneous AvatarState for a teaching scene.
    Evaluates emotion, action gestures, viseme timing from word/sentence cues, and checkpoint/remediation states.
    """
    if session_id not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teaching session '{session_id}' not found.",
        )
    session = ACTIVE_SESSIONS[session_id]
    sec_id = session.current_section_id or "sec-1"
    cache_key = f"{session_id}_{sec_id}"

    if cache_key not in orchestrator.scene_plans_cache:
        # Generate scene plan if not present
        await orchestrator.generate_scene_plan(session)

    plan = orchestrator.scene_plans_cache.get(cache_key)
    target_scene: Optional[TeachingScene] = None
    if plan:
        for s in plan.scenes:
            if s.scene_id == scene_id:
                target_scene = s
                break

    if not target_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene '{scene_id}' not found in active session plan.",
        )

    # Check for synthesized AudioAsset in speech provider if available
    audio_asset = None
    if target_scene.audio_asset_id:
        pass

    avatar_state = AvatarController.get_avatar_state_for_scene(
        scene=target_scene,
        playback_time=playback_time,
        is_playing=is_playing,
        is_checkpoint=target_scene.is_checkpoint,
        is_remediation=(target_scene.scene_type == "adaptive_remediation"),
        audio_asset=audio_asset,
        reduced_motion=reduced_motion,
    )
    return avatar_state
