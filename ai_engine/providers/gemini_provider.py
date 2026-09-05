"""Gemini and Cloud LLM provider with structured Pydantic output validation and deterministic fallback."""
import os
import json
import logging
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel

from ai_engine.providers.base import LLMProvider
from ai_engine.providers.mock_provider import DeterministicTeachingProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class GeminiLLMProvider(LLMProvider):
    """
    Production-ready LLM provider interfacing with Gemini via REST API.
    Enforces strict Pydantic JSON schema output and transparently falls back
    to DeterministicTeachingProvider if GEMINI_API_KEY is not configured or in case of errors.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model
        self.fallback = DeterministicTeachingProvider()
        if not self.api_key:
            logger.info("GEMINI_API_KEY not configured. Operating in high-fidelity Deterministic mode.")

    async def generate_text(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        if not self.api_key:
            return await self.fallback.generate_text(prompt, system_prompt, **kwargs)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instructions: {system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, headers=headers, json={"contents": contents})
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                logger.warning("Gemini API non-200 or unexpected payload: %s. Using fallback.", res.text)
        except Exception as e:
            logger.warning("Error calling Gemini API: %s. Using deterministic fallback.", e)

        return await self.fallback.generate_text(prompt, system_prompt, **kwargs)

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> T:
        if not self.api_key:
            return await self.fallback.generate_structured(
                prompt, response_schema, system_prompt, **kwargs
            )

        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        system_instruction = (
            (system_prompt + "\n" if system_prompt else "")
            + f"You are a master human-like educator. You MUST output ONLY valid JSON conforming to this schema:\n{schema_json}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": system_instruction}]},
                {"role": "user", "parts": [{"text": prompt}]},
            ],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        raw_json = candidates[0]["content"]["parts"][0]["text"]
                        parsed = json.loads(raw_json)
                        return response_schema.model_validate(parsed)
                logger.warning("Gemini structured call failed: %s. Using deterministic fallback.", res.text)
        except Exception as e:
            logger.warning("Error in Gemini structured generation: %s. Using fallback.", e)

        return await self.fallback.generate_structured(
            prompt, response_schema, system_prompt, **kwargs
        )
