"""Base provider abstractions for AI Teacher services."""
from abc import ABC, abstractmethod
from typing import List, Optional, Type, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract interface for Large Language Model providers."""

    @abstractmethod
    async def generate_text(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        """Generate unstructured text from a prompt."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> T:
        """Generate structured data strictly validated against a Pydantic model."""
        pass


class EmbeddingProvider(ABC):
    """Abstract interface for text embedding providers (RAG)."""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single text chunk."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for multiple chunks."""
        pass


class SpeechProvider(ABC):
    """Abstract interface for AI Voice / Text-to-Speech synthesis."""

    @abstractmethod
    async def synthesize_speech(
        self, text: str, voice_id: Optional[str] = None, language: str = "en"
    ) -> bytes:
        """Synthesize spoken audio from text."""
        pass

    @abstractmethod
    async def synthesize_speech_asset(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en",
        scene_id: Optional[str] = None,
        emotion: Optional[str] = None,
    ) -> Any:
        """Synthesize spoken audio and return complete AudioAsset with duration and subtitle timing."""
        pass



class AvatarProvider(ABC):
    """Abstract interface for Human-Like AI Avatar generation."""

    @abstractmethod
    async def generate_avatar_frames(
        self, audio_bytes: bytes, avatar_id: Optional[str] = None
    ) -> Any:
        """Generate synchronized avatar video/frames for spoken audio."""
        pass

    @abstractmethod
    def derive_avatar_state(
        self, scene_dict: dict, playback_time: float, is_playing: bool
    ) -> Any:
        """Derive structured presentation state for the active frame."""
        pass


class VideoProvider(ABC):
    """Abstract interface for composite educational video generation."""

    @abstractmethod
    async def composite_lesson_video(
        self,
        audio_stream: bytes,
        visual_plan: dict,
        output_format: str = "mp4",
    ) -> str:
        """Render synchronized educational video with visuals and avatar."""
        pass
