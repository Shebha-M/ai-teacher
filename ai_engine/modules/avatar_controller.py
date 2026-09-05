"""
Avatar Controller Module: Connects Teaching State, Teaching Scenes, and Audio Timing
into a deterministic, structured AvatarState for real-time presentation.
"""
from typing import List, Optional, Dict, Any
from ai_engine.schemas.scene import TeachingScene, TeacherEmotion, VisualType
from ai_engine.schemas.avatar import (
    AvatarState,
    MouthState,
    EyeState,
    AvatarGesture,
    HeadMotion,
    TimingMode,
)
from ai_engine.schemas.language import AudioAsset


class AvatarController:
    """
    Central controller responsible for computing the AI Teacher's visual presentation state.
    Translates emotion, scene actions, checkpoints, adaptive remediation, and audio clocks into AvatarState.
    """

    # Mapping of teacher actions to pedagogical gestures
    ACTION_TO_GESTURE_MAP: Dict[str, AvatarGesture] = {
        "welcome": AvatarGesture.WELCOME,
        "greet": AvatarGesture.WELCOME,
        "introduce": AvatarGesture.WELCOME,
        "explain": AvatarGesture.EXPLAIN,
        "point_to_visual": AvatarGesture.POINT_VISUAL,
        "point_visual": AvatarGesture.POINT_VISUAL,
        "trace_visual": AvatarGesture.POINT_VISUAL,
        "trace_tree": AvatarGesture.POINT_VISUAL,
        "trace_circuit": AvatarGesture.POINT_VISUAL,
        "point_left": AvatarGesture.POINT_LEFT,
        "point_right": AvatarGesture.POINT_RIGHT,
        "ask_question": AvatarGesture.THINK,
        "checkpoint": AvatarGesture.THINK,
        "think": AvatarGesture.THINK,
        "encourage": AvatarGesture.ENCOURAGE,
        "remediate": AvatarGesture.ENCOURAGE,
        "celebrate": AvatarGesture.CELEBRATE,
        "congratulate": AvatarGesture.CELEBRATE,
        "idle": AvatarGesture.IDLE,
    }

    # Mapping of emotions to default gestures and head postures
    EMOTION_PROFILE_MAP: Dict[TeacherEmotion, Dict[str, Any]] = {
        TeacherEmotion.WELCOMING: {
            "default_gesture": AvatarGesture.WELCOME,
            "head_motion": HeadMotion.NOD,
        },
        TeacherEmotion.EXPLAINING: {
            "default_gesture": AvatarGesture.EXPLAIN,
            "head_motion": HeadMotion.NEUTRAL,
        },
        TeacherEmotion.ENCOURAGING: {
            "default_gesture": AvatarGesture.ENCOURAGE,
            "head_motion": HeadMotion.NOD,
        },
        TeacherEmotion.THOUGHTFUL: {
            "default_gesture": AvatarGesture.THINK,
            "head_motion": HeadMotion.TILT_THOUGHTFUL,
        },
        TeacherEmotion.CELEBRATING: {
            "default_gesture": AvatarGesture.CELEBRATE,
            "head_motion": HeadMotion.NOD,
        },
    }

    @classmethod
    def map_action_to_gesture(cls, action: str, visual_type: Optional[str] = None) -> AvatarGesture:
        """Derive body pose and gesture from scene action and visual layout."""
        act_lower = (action or "").strip().lower()
        if act_lower in cls.ACTION_TO_GESTURE_MAP:
            return cls.ACTION_TO_GESTURE_MAP[act_lower]

        # Contextual heuristics
        if "point" in act_lower or "trace" in act_lower:
            return AvatarGesture.POINT_VISUAL
        if "question" in act_lower or "check" in act_lower or "think" in act_lower:
            return AvatarGesture.THINK
        if "encourage" in act_lower or "remediat" in act_lower:
            return AvatarGesture.ENCOURAGE
        if "celebrat" in act_lower or "praise" in act_lower or "great" in act_lower:
            return AvatarGesture.CELEBRATE

        return AvatarGesture.EXPLAIN

    @classmethod
    def map_emotion_profile(
        cls,
        emotion: TeacherEmotion,
        is_checkpoint: bool = False,
        is_remediation: bool = False,
    ) -> Dict[str, Any]:
        """
        Connect TeacherEmotion to avatar posture and head motion.
        Checkpoints override posture to THOUGHTFUL/THINK, while remediation overrides to ENCOURAGING.
        """
        if is_checkpoint:
            return {
                "emotion": TeacherEmotion.THOUGHTFUL,
                "gesture": AvatarGesture.THINK,
                "head_motion": HeadMotion.TILT_THOUGHTFUL,
            }

        if is_remediation:
            return {
                "emotion": TeacherEmotion.ENCOURAGING,
                "gesture": AvatarGesture.ENCOURAGE,
                "head_motion": HeadMotion.NOD,
            }

        profile = cls.EMOTION_PROFILE_MAP.get(emotion, cls.EMOTION_PROFILE_MAP[TeacherEmotion.EXPLAINING])
        return {
            "emotion": emotion,
            "gesture": profile["default_gesture"],
            "head_motion": profile["head_motion"],
        }

    @classmethod
    def calculate_mouth_state(
        cls,
        playback_time: float,
        is_playing: bool,
        word_cues: Optional[List[Dict[str, Any]]] = None,
        subtitles: Optional[List[Any]] = None,
        total_duration: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculate instantaneous mouth viseme from audio playback time.
        Hierarchy:
          1. Word Cues (high fidelity visemes: REST -> OPEN -> HALF_OPEN -> NARROW -> REST)
          2. Sentence Subtitles (medium fidelity syllable timing)
          3. Deterministic fallback
        """
        if not is_playing or playback_time < 0.0:
            return {
                "mouth_state": MouthState.REST,
                "active_word": None,
                "speaking_progress": 0.0,
                "timing_mode": TimingMode.DETERMINISTIC,
            }

        # Check total duration boundary
        if total_duration > 0 and playback_time >= total_duration:
            return {
                "mouth_state": MouthState.REST,
                "active_word": None,
                "speaking_progress": 1.0,
                "timing_mode": TimingMode.DETERMINISTIC,
            }

        # 1. High precision: Word Cues
        if word_cues and len(word_cues) > 0:
            for cue in word_cues:
                start = cue.get("start", 0.0)
                end = cue.get("end", 0.0)
                if start <= playback_time <= end:
                    word_duration = max(0.01, end - start)
                    progress = (playback_time - start) / word_duration
                    word_text = cue.get("text", "")

                    # Viseme progression through word:
                    # 0% - 20%: OPEN (attack)
                    # 20% - 60%: HALF_OPEN (vocal body)
                    # 60% - 90%: NARROW (consonant release)
                    # 90% - 100%: REST (boundary)
                    if progress < 0.25:
                        mouth = MouthState.OPEN
                    elif progress < 0.65:
                        mouth = MouthState.HALF_OPEN
                    elif progress < 0.90:
                        mouth = MouthState.NARROW
                    else:
                        mouth = MouthState.REST

                    return {
                        "mouth_state": mouth,
                        "active_word": word_text,
                        "speaking_progress": round(progress, 3),
                        "timing_mode": TimingMode.WORD_CUES,
                    }

            # In gap between words
            return {
                "mouth_state": MouthState.REST,
                "active_word": None,
                "speaking_progress": 0.0,
                "timing_mode": TimingMode.WORD_CUES,
            }

        # 2. Medium precision: Sentence Cues
        if subtitles and len(subtitles) > 0:
            for sub in subtitles:
                start = getattr(sub, "start_time", sub.get("start_time", 0.0) if isinstance(sub, dict) else 0.0)
                end = getattr(sub, "end_time", sub.get("end_time", 0.0) if isinstance(sub, dict) else 0.0)
                if start <= playback_time <= end:
                    # Syllabic oscillation within sentence (approx ~4 syllables/sec)
                    cycle_time = (playback_time - start) % 0.28
                    if cycle_time < 0.08:
                        mouth = MouthState.OPEN
                    elif cycle_time < 0.18:
                        mouth = MouthState.HALF_OPEN
                    elif cycle_time < 0.24:
                        mouth = MouthState.NARROW
                    else:
                        mouth = MouthState.REST

                    norm_progress = (playback_time - start) / max(0.01, end - start)
                    return {
                        "mouth_state": mouth,
                        "active_word": None,
                        "speaking_progress": round(norm_progress, 3),
                        "timing_mode": TimingMode.SENTENCE_CUES,
                    }

        # 3. Fallback: Deterministic cyclic animation
        cycle = playback_time % 0.32
        if cycle < 0.10:
            mouth = MouthState.OPEN
        elif cycle < 0.22:
            mouth = MouthState.HALF_OPEN
        elif cycle < 0.28:
            mouth = MouthState.NARROW
        else:
            mouth = MouthState.REST

        return {
            "mouth_state": mouth,
            "active_word": None,
            "speaking_progress": round(cycle / 0.32, 3),
            "timing_mode": TimingMode.DETERMINISTIC,
        }

    @classmethod
    def calculate_eye_state(cls, playback_time: float) -> EyeState:
        """Natural non-periodic blinking model: blinks for 150ms every 3.5 seconds."""
        cycle = playback_time % 3.5
        # Blink in the window [3.35, 3.50]
        if cycle >= 3.35:
            return EyeState.BLINK
        return EyeState.OPEN

    @classmethod
    def get_avatar_state_for_scene(
        cls,
        scene: TeachingScene,
        playback_time: float = 0.0,
        is_playing: bool = False,
        is_checkpoint: bool = False,
        is_remediation: bool = False,
        audio_asset: Optional[AudioAsset] = None,
        reduced_motion: bool = False,
    ) -> AvatarState:
        """
        Produce a complete, self-consistent AvatarState for the current scene and audio time.
        """
        # Determine emotion & posture profile
        profile = cls.map_emotion_profile(
            emotion=scene.teacher_emotion,
            is_checkpoint=is_checkpoint or scene.is_checkpoint,
            is_remediation=is_remediation or (scene.scene_type == "adaptive_remediation"),
        )

        # Derive gesture from scene action if not overridden by checkpoint/remediation
        if is_checkpoint or scene.is_checkpoint:
            gesture = AvatarGesture.THINK
        elif is_remediation or (scene.scene_type == "adaptive_remediation"):
            gesture = AvatarGesture.ENCOURAGE
        else:
            gesture = cls.map_action_to_gesture(scene.teacher_action)

        # Checkpoint overrides speaking to False
        effective_is_playing = is_playing and not is_checkpoint and not scene.is_checkpoint

        # Extract timing cues from AudioAsset
        word_cues = audio_asset.word_cues if audio_asset else None
        subtitles = audio_asset.subtitles if audio_asset else (scene.subtitles or None)
        total_duration = audio_asset.duration_seconds if audio_asset else scene.estimated_duration

        mouth_data = cls.calculate_mouth_state(
            playback_time=playback_time,
            is_playing=effective_is_playing,
            word_cues=word_cues,
            subtitles=subtitles,
            total_duration=total_duration,
        )

        eye_state = cls.calculate_eye_state(playback_time) if not reduced_motion else EyeState.OPEN
        head_motion = profile["head_motion"] if not reduced_motion else HeadMotion.NEUTRAL

        return AvatarState(
            emotion=profile["emotion"],
            speaking=effective_is_playing,
            mouth_state=mouth_data["mouth_state"],
            eye_state=eye_state,
            head_motion=head_motion,
            gesture=gesture,
            speaking_progress=mouth_data["speaking_progress"],
            scene_action=scene.teacher_action,
            timing_mode=mouth_data["timing_mode"],
            reduced_motion=reduced_motion,
            active_word=mouth_data["active_word"],
        )
