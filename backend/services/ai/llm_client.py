"""LLM client for OpenAI-compatible APIs."""

# Re-export main functionality for backward compatibility
from backend.services.ai.llm_client.client import LLMClient, get_llm_client, reset_llm_client

__all__ = [
    "LLMClient",
    "get_llm_client",
    "reset_llm_client",
]
