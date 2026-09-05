"""Speech provider implementations: EdgeTTSProvider and MockSpeechProvider."""
import os
import re
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from ai_engine.providers.base import SpeechProvider
from ai_engine.schemas.language import AudioAsset, SubtitleSegment, LanguageCode

logger = logging.getLogger(__name__)

# Default audio storage directory within backend
AUDIO_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "media" / "audio"
AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class MockSpeechProvider(SpeechProvider):
    """
    Deterministic offline speech provider.
    Generates synthetic audio payloads and sentence-level subtitles without network dependencies.
    """

    async def synthesize_speech(
        self, text: str, voice_id: Optional[str] = None, language: str = "en"
    ) -> bytes:
        words = text.split()
        duration_est = max(2.0, round(len(words) / 2.6, 2))
        header = f"RIFF_MOCK_WAV:words={len(words)}:dur={duration_est}:lang={language}:voice={voice_id or 'default_teacher'}"
        return header.encode("utf-8")

    async def synthesize_speech_asset(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en",
        scene_id: Optional[str] = None,
        emotion: Optional[str] = None,
    ) -> AudioAsset:
        asset_id = f"audio-mock-{uuid.uuid4().hex[:8]}"
        words = text.split()
        total_duration = max(2.5, round(len(words) / 2.5, 2))

        # Sentence-level subtitle breakdown
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if not sentences:
            sentences = [text]

        subtitles: List[SubtitleSegment] = []
        current_time = 0.0
        time_per_sentence = round(total_duration / max(1, len(sentences)), 2)

        for idx, s in enumerate(sentences):
            start = current_time
            end = round(min(total_duration, current_time + time_per_sentence), 2)
            subtitles.append(
                SubtitleSegment(
                    id=idx + 1,
                    start_time=start,
                    end_time=end,
                    text=s,
                )
            )
            current_time = end

        words = text.split()
        word_cues = []
        if words:
            time_per_word = round(total_duration / len(words), 3)
            for widx, w in enumerate(words):
                w_start = round(widx * time_per_word, 3)
                w_end = round(min(total_duration, (widx + 1) * time_per_word), 3)
                word_cues.append({"text": w, "start": w_start, "end": w_end})

        # Save synthetic audio file for streaming endpoint
        file_path = AUDIO_STORAGE_DIR / f"{asset_id}.wav"
        audio_bytes = await self.synthesize_speech(text, voice_id=voice_id, language=language)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        return AudioAsset(
            asset_id=asset_id,
            scene_id=scene_id,
            language=language,
            voice_id=voice_id or "mock_teacher_voice",
            duration_seconds=total_duration,
            audio_url=f"/api/v1/media/audio/{asset_id}",
            subtitles=subtitles,
            word_cues=word_cues,
            provider_type="mock",
        )


class EdgeTTSProvider(SpeechProvider):
    """
    Real Microsoft Edge Neural TTS provider.
    Synthesizes natural spoken audio across English, Hindi, Tamil, Telugu, Malayalam, and Kannada.
    Extracts real word/sentence timing cues and falls back gracefully to MockSpeechProvider on error.
    """

    def __init__(self, fallback_provider: Optional[SpeechProvider] = None):
        self.fallback = fallback_provider or MockSpeechProvider()

    async def synthesize_speech(
        self, text: str, voice_id: Optional[str] = None, language: str = "en"
    ) -> bytes:
        asset = await self.synthesize_speech_asset(text=text, voice_id=voice_id, language=language)
        file_path = AUDIO_STORAGE_DIR / f"{asset.asset_id}.mp3"
        if file_path.exists():
            with open(file_path, "rb") as f:
                return f.read()
        return await self.fallback.synthesize_speech(text, voice_id=voice_id, language=language)

    async def synthesize_speech_asset(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en",
        scene_id: Optional[str] = None,
        emotion: Optional[str] = None,
    ) -> AudioAsset:
        try:
            import edge_tts

            # Determine voice
            chosen_voice = voice_id
            if not chosen_voice:
                from ai_engine.modules.language_controller import LanguageController
                chosen_voice = LanguageController.get_default_voice(language)

            asset_id = f"audio-edge-{uuid.uuid4().hex[:8]}"
            audio_path = AUDIO_STORAGE_DIR / f"{asset_id}.mp3"

            communicate = edge_tts.Communicate(text, chosen_voice)

            # Stream audio chunks and collect word/sentence boundary events
            audio_chunks = []
            word_cues = []

            async for event in communicate.stream():
                if event["type"] == "audio":
                    audio_chunks.append(event["data"])
                elif event["type"] == "WordBoundary":
                    # Offset and duration are in 100ns units
                    offset_sec = round(event["offset"] / 10_000_000, 3)
                    duration_sec = round(event["duration"] / 10_000_000, 3)
                    word_cues.append({
                        "text": event["text"],
                        "start": offset_sec,
                        "end": round(offset_sec + duration_sec, 3),
                    })

            if not audio_chunks:
                raise RuntimeError("Edge-TTS returned no audio data.")

            full_audio = b"".join(audio_chunks)
            with open(audio_path, "wb") as f:
                f.write(full_audio)

            # Calculate total duration from word cues or fallback
            if word_cues:
                total_duration = max(word_cues[-1]["end"], 1.5)
            else:
                total_duration = max(2.0, round(len(text.split()) / 2.4, 2))

            # Build sentence-level SubtitleSegments
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
            if not sentences:
                sentences = [text]

            subtitles: List[SubtitleSegment] = []
            current_time = 0.0
            time_per_sentence = round(total_duration / max(1, len(sentences)), 2)

            for idx, s in enumerate(sentences):
                start = current_time
                end = round(min(total_duration, current_time + time_per_sentence), 2)
                subtitles.append(
                    SubtitleSegment(
                        id=idx + 1,
                        start_time=start,
                        end_time=end,
                        text=s,
                    )
                )
                current_time = end

            return AudioAsset(
                asset_id=asset_id,
                scene_id=scene_id,
                language=language,
                voice_id=chosen_voice,
                duration_seconds=round(total_duration, 2),
                audio_url=f"/api/v1/media/audio/{asset_id}",
                subtitles=subtitles,
                word_cues=word_cues,
                provider_type="edge_tts",
            )

        except Exception as e:
            logger.warning(f"EdgeTTS failed or offline ({e}); falling back to MockSpeechProvider.")
            return await self.fallback.synthesize_speech_asset(
                text=text,
                voice_id=voice_id,
                language=language,
                scene_id=scene_id,
                emotion=emotion,
            )


def get_speech_provider() -> SpeechProvider:
    """Factory helper to obtain configured speech provider."""
    return EdgeTTSProvider()
