"""Export providers and default factory."""
import os
from ai_engine.providers.base import (
    LLMProvider,
    EmbeddingProvider,
    SpeechProvider,
    AvatarProvider,
    VideoProvider,
)
from ai_engine.providers.mock_provider import DeterministicTeachingProvider
from ai_engine.providers.gemini_provider import GeminiLLMProvider


def get_default_llm_provider() -> LLMProvider:
    """Factory returns GeminiLLMProvider if GEMINI_API_KEY is present, else DeterministicTeachingProvider."""
    if os.environ.get("GEMINI_API_KEY"):
        return GeminiLLMProvider()
    return DeterministicTeachingProvider()


def get_teaching_provider() -> DeterministicTeachingProvider:
    """Factory returning active teaching provider."""
    return DeterministicTeachingProvider()


def get_default_embedding_provider() -> EmbeddingProvider:
    """Factory returning default embedding provider."""
    return DeterministicTeachingProvider()


from ai_engine.providers.speech_provider import (
    MockSpeechProvider,
    EdgeTTSProvider,
    get_speech_provider,
)


__all__ = [
    "LLMProvider",
    "EmbeddingProvider",
    "SpeechProvider",
    "AvatarProvider",
    "VideoProvider",
    "DeterministicTeachingProvider",
    "GeminiLLMProvider",
    "MockSpeechProvider",
    "EdgeTTSProvider",
    "get_default_llm_provider",
    "get_teaching_provider",
    "get_default_embedding_provider",
    "get_speech_provider",
]

