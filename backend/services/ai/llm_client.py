"""LLM client for OpenAI-compatible APIs."""
import os
import logging
import asyncio
from typing import Optional
import httpx
from dotenv import load_dotenv

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

    def _is_reasoning_model(self) -> bool:
        """Check if the model is a reasoning model that doesn't support temperature."""
        model_lower = self.model.lower()
        # Reasoning models: o1, o3, gpt-5.x series don't support temperature
        reasoning_patterns = ("o1", "o3", "gpt-5")
        return any(pattern in model_lower for pattern in reasoning_patterns)

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
        if not self.is_configured():
            missing = []
            if not self.enabled:
                missing.append("AI_ENABLED=true")
            if not self.base_url:
                missing.append("AI_BASE_URL")
            if not self.api_key:
                missing.append("AI_API_KEY")
            raise ValueError(
                f"LLM is not configured. Missing: {', '.join(missing)}. "
                f"Set these in .env file and ensure docker-compose.yml passes them to the container."
            )

        system_prompt = (
            "You are a helpful writing assistant. Rewrite the provided text according to the user's instructions. "
            "Return only the rewritten text, without any explanations or markdown formatting."
        )

        user_message = f"{prompt}\n\nText to rewrite:\n{text}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_completion_tokens": 2000,
        }

        # Only include temperature for models that support it
        # Reasoning models (o1, o3, gpt-5.x) don't support temperature
        if not self._is_reasoning_model():
            payload["temperature"] = self.temperature

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"

        # Retry logic for transient errors
        max_retries = 3
        retry_delays = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    result = response.json()

                    if "choices" not in result or not result["choices"]:
                        raise ValueError("Invalid response from LLM API")

                    content = result["choices"][0]["message"]["content"]
                    return content.strip()
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                # Retry on transient server errors
                if status_code in (429, 500, 502, 503) and attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(
                        f"LLM API request failed with {status_code} (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    continue
                # Don't retry on client errors (400, 401, 403) or after max retries
                logger.error(f"LLM API request failed: {e}", exc_info=True)
                raise
            except httpx.TimeoutException as e:
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(
                        f"LLM API request timed out (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"LLM API request timed out after {max_retries} attempts: {e}", exc_info=True)
                raise
            except httpx.HTTPError as e:
                # Don't retry on connection errors or other HTTP errors
                logger.error(f"LLM API request failed: {e}", exc_info=True)
                raise
            except Exception as e:
                logger.error(f"Unexpected error calling LLM: {e}", exc_info=True)
                raise ValueError(f"Failed to rewrite text: {str(e)}")


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
