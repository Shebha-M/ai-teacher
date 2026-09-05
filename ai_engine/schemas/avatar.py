"""Data contracts and schemas for Human-Like AI Teacher Avatar presentation and speech synchronization."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ai_engine.schemas.scene import TeacherEmotion


class MouthState(str, Enum):
    """Mouth viseme states for speech and lip synchronization."""
    REST = "rest"
    OPEN = "open"
    HALF_OPEN = "half_open"
    NARROW = "narrow"


class EyeState(str, Enum):
    """Eye eyelid states for natural blinking and facial expression."""
    OPEN = "open"
    BLINK = "blink"


class AvatarGesture(str, Enum):
    """Pedagogical body poses and gestures displayed by the AI Teacher."""
    IDLE = "idle"
    WELCOME = "welcome"
    POINT_LEFT = "point_left"
    POINT_RIGHT = "point_right"
    POINT_VISUAL = "point_visual"
    EXPLAIN = "explain"
    THINK = "think"
    ENCOURAGE = "encourage"
    CELEBRATE = "celebrate"


class HeadMotion(str, Enum):
    """Subtle head positioning and motion states."""
    NEUTRAL = "neutral"
    NOD = "nod"
    TILT_THOUGHTFUL = "tilt_thoughtful"
    TILT_LISTENING = "tilt_listening"


class TimingMode(str, Enum):
    """Precision tier used to drive avatar mouth synchronization."""
    WORD_CUES = "word_cues"          # High precision: exact word boundary timestamps from EdgeTTS
    SENTENCE_CUES = "sentence_cues"  # Medium precision: sentence level durations
    BROWSER_SPEECH = "browser_speech"# Fallback: client Web Speech synthesis
    DETERMINISTIC = "deterministic"  # Offline / fallback animation


class AvatarState(BaseModel):
    """
    Structured state model representing the instantaneous presentation of the AI Teacher avatar.
    Derived deterministically from Teaching State + Teaching Scene + Audio Timing.
    """
    emotion: TeacherEmotion = Field(TeacherEmotion.EXPLAINING, description="Current emotional tone and facial expression")
    speaking: bool = Field(False, description="True if voice audio is actively playing")
    mouth_state: MouthState = Field(MouthState.REST, description="Instantaneous mouth viseme position")
    eye_state: EyeState = Field(EyeState.OPEN, description="Eye state (open or blinking)")
    head_motion: HeadMotion = Field(HeadMotion.NEUTRAL, description="Subtle head angle or nod")
    gesture: AvatarGesture = Field(AvatarGesture.IDLE, description="Pedagogical body pose or gesture")
    speaking_progress: float = Field(0.0, description="Normalized speaking progress through current segment (0.0 to 1.0)")
    scene_action: str = Field("explain", description="Action name from the active TeachingScene")
    timing_mode: TimingMode = Field(TimingMode.DETERMINISTIC, description="Timing precision mode in effect")
    reduced_motion: bool = Field(False, description="True if accessibility reduced-motion mode is active")
    active_word: Optional[str] = Field(None, description="Current word being pronounced, if word cues are available")
