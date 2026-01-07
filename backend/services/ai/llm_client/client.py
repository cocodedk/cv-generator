"""Main LLM client implementation."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

from backend.services.ai.llm_client.request_builder import _build_payload
from backend.services.ai.llm_client.request_executor import _make_request_with_retry
from backend.services.ai.llm_client.validation import _validate_configuration

load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for OpenAI-compatible LLM APIs."""

    def __init__(self):
        self.base_url = os.getenv("AI_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("AI_API_KEY", "")
        self.model = os.getenv("AI_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.timeout = int(os.getenv("AI_REQUEST_TIMEOUT_S", "30"))
        self.enabled = os.getenv("AI_ENABLED", "false").lower() == "true"

    def is_configured(self) -> bool:
        """Check if LLM is properly configured."""
        return self.enabled and bool(self.base_url) and bool(self.api_key)

    async def rewrite_text(self, text: str, prompt: str) -> str:
        """
        Rewrite text using LLM with a custom prompt.

        Args:
            text: The text to rewrite
            prompt: User's prompt/instruction for rewriting

        Returns:
            Rewritten text

        Raises:
            ValueError: If LLM is not configured
            httpx.HTTPError: If API request fails
        """
        _validate_configuration(self)

        payload = _build_payload(self, text, prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"

        return await _make_request_with_retry(self, url, payload, headers)

    async def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Generate text using LLM with a custom prompt.

        Args:
            prompt: The generation prompt/instructions
            system_prompt: Optional custom system prompt (defaults to generic assistant)

        Returns:
            Generated text

        Raises:
            ValueError: If LLM is not configured
            httpx.HTTPError: If API request fails
        """
        _validate_configuration(self)

        if system_prompt is None:
            system_prompt = "You are a helpful assistant. Follow the user's instructions carefully."

        from backend.services.ai.llm_client.request_builder import _is_reasoning_model

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_completion_tokens": 2000,
        }

        # Only include temperature for models that support it
        # Reasoning models (o1, o3, gpt-5.x) don't support temperature
        if not _is_reasoning_model(self):
            payload["temperature"] = self.temperature

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"

        return await _make_request_with_retry(self, url, payload, headers)


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def reset_llm_client() -> None:
    """Reset the LLM client singleton (useful for testing or config changes)."""
    global _llm_client
    _llm_client = None
