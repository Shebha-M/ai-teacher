"""Data contracts and schemas for multilingual teaching and voice synthesis."""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class LanguageCode(str, Enum):
    """Standard ISO 639-1 language codes for supported educational languages."""
    EN = "en"  # English
    HI = "hi"  # Hindi (हिन्दी)
    TA = "ta"  # Tamil (தமிழ்)
    TE = "te"  # Telugu (తెలుగు)
    ML = "ml"  # Malayalam (മലയാളം)
    KN = "kn"  # Kannada (ಕನ್ನಡ)


class LanguageMode(str, Enum):
    """Pedagogical language presentation mode."""
    FULL_LANGUAGE = "full"        # Pure target language throughout narrative
    BILINGUAL = "bilingual"        # Spoken in target language with technical terms preserved in English
    MIXED = "mixed"                # Natural Hinglish/Tanglish style conversational code-switching


class VoiceMetadata(BaseModel):
    """Metadata for an AI voice option."""
    voice_id: str = Field(..., description="Unique voice identifier (e.g. 'en-US-AriaNeural')")
    name: str = Field(..., description="Friendly display name")
    language_code: LanguageCode = Field(..., description="Language associated with this voice")
    gender: str = Field("neutral", description="female, male, neutral")
    provider: str = Field("edge_tts", description="Provider source: 'edge_tts', 'mock', 'elevenlabs'")
    is_default: bool = Field(False, description="Whether this is the default voice for the language")
    description: Optional[str] = Field(None, description="Voice style description, e.g. 'Warm & Clear'")


class LanguageConfig(BaseModel):
    """Linguistic and script configuration for a supported language."""
    code: LanguageCode = Field(..., description="Language code")
    display_name: str = Field(..., description="English name, e.g. 'Hindi'")
    native_name: str = Field(..., description="Native script name, e.g. 'हिन्दी'")
    script: str = Field(..., description="Primary writing system: Latin, Devanagari, Tamil, Telugu, Malayalam, Kannada")
    fallback_language: LanguageCode = Field(LanguageCode.EN, description="Fallback if translation unavailable")
    default_voice_id: str = Field(..., description="Default neural voice ID")
    supported_modes: List[LanguageMode] = Field(
        default_factory=lambda: [LanguageMode.FULL_LANGUAGE, LanguageMode.BILINGUAL, LanguageMode.MIXED]
    )


class LanguageDecision(BaseModel):
    """Structured decision output from the LanguageController."""
    requested_language: str = Field(..., description="Language requested by student or session")
    resolved_language: LanguageCode = Field(..., description="Resolved supported language code")
    mode: LanguageMode = Field(LanguageMode.BILINGUAL, description="Pedagogical language mode")
    fallback_used: bool = Field(False, description="True if requested language was unsupported and fell back")
    preserved_terms: List[str] = Field(
        default_factory=list, description="Technical terms preserved in English"
    )
    voice_id: str = Field(..., description="Selected neural voice ID")
    script: str = Field("Latin", description="Associated writing script")


class SubtitleSegment(BaseModel):
    """Timestamped subtitle cue for synchronized captioning."""
    id: int = Field(..., description="Sequential cue index")
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Subtitle text for this time segment")


class AudioAsset(BaseModel):
    """Synthesized educational speech audio asset."""
    asset_id: str = Field(..., description="Unique audio asset identifier")
    scene_id: Optional[str] = Field(None, description="Associated teaching scene ID")
    language: str = Field("en", description="Spoken language code")
    voice_id: str = Field(..., description="Voice model used for synthesis")
    duration_seconds: float = Field(..., description="Total audio duration in seconds")
    audio_url: str = Field(..., description="Safe relative or absolute URL to stream audio file")
    subtitles: List[SubtitleSegment] = Field(
        default_factory=list, description="Synchronized subtitle cues"
    )
    word_cues: List[Dict[str, Any]] = Field(
        default_factory=list, description="Word-level start and end timestamps"
    )
    provider_type: str = Field("mock", description="Provider used: 'edge_tts', 'mock'")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO creation timestamp",
    )
