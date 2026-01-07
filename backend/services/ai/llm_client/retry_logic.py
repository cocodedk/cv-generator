"""Retry logic utilities."""

import logging
import httpx

logger = logging.getLogger(__name__)


def _should_retry_status_error(
    e: httpx.HTTPStatusError, attempt: int, max_retries: int, retry_delays: list
) -> tuple[bool, float]:
    """Check if status error should be retried. Returns (should_retry, delay)."""
    status_code = e.response.status_code
    # Retry on transient server errors
    if status_code in (429, 500, 502, 503) and attempt < max_retries - 1:
        delay = retry_delays[attempt]
        logger.warning(
            f"LLM API request failed with {status_code} (attempt {attempt + 1}/{max_retries}). "
            f"Retrying in {delay}s..."
        )
        return True, delay
    # Don't retry on client errors (400, 401, 403) or after max retries
    logger.error(f"LLM API request failed: {e}", exc_info=True)
    return False, 0.0


def _should_retry_timeout(
    e: httpx.TimeoutException, attempt: int, max_retries: int, retry_delays: list
) -> tuple[bool, float]:
    """Check if timeout should be retried. Returns (should_retry, delay)."""
    if attempt < max_retries - 1:
        delay = retry_delays[attempt]
        logger.warning(
            f"LLM API request timed out (attempt {attempt + 1}/{max_retries}). "
            f"Retrying in {delay}s..."
        )
        return True, delay
    logger.error(f"LLM API request timed out after {max_retries} attempts: {e}", exc_info=True)
    return False, 0.0
