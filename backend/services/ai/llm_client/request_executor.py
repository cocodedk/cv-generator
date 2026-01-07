"""Request execution utilities."""

import asyncio
import logging
import httpx

from backend.services.ai.llm_client.retry_logic import _should_retry_status_error, _should_retry_timeout

logger = logging.getLogger(__name__)


async def _make_request_with_retry(self, url: str, payload: dict, headers: dict) -> str:
    """Make API request with retry logic for transient errors."""
    max_retries = 3
    retry_delays = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s

    for attempt in range(max_retries):
        try:
            return await _execute_request(self, url, payload, headers)
        except httpx.HTTPStatusError as e:
            should_retry, delay = _should_retry_status_error(e, attempt, max_retries, retry_delays)
            if not should_retry:
                raise
            await asyncio.sleep(delay)
        except httpx.TimeoutException as e:
            should_retry, delay = _should_retry_timeout(e, attempt, max_retries, retry_delays)
            if not should_retry:
                raise
            await asyncio.sleep(delay)
        except httpx.HTTPError as e:
            logger.error(f"LLM API request failed: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling LLM: {e}", exc_info=True)
            raise ValueError(f"Failed to rewrite text: {str(e)}")


async def _execute_request(self, url: str, payload: dict, headers: dict) -> str:
    """Execute a single API request."""
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        if "choices" not in result or not result["choices"]:
            raise ValueError("Invalid response from LLM API")

        content = result["choices"][0]["message"]["content"]
        return content.strip()
