"""LLM client for OpenAI-compatible APIs."""
import os
import logging
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
            "temperature": self.temperature,
            "max_tokens": 2000,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()

                if "choices" not in result or not result["choices"]:
                    raise ValueError("Invalid response from LLM API")

                content = result["choices"][0]["message"]["content"]
                return content.strip()
        except httpx.HTTPError as e:
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
