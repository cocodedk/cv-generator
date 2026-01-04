"""AI drafting routes (heuristics-first)."""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError
from slowapi import Limiter
import httpx

from backend.database import queries
from backend.models import ProfileData
from backend.models_ai import (
    AIGenerateCVRequest,
    AIGenerateCVResponse,
    AIRewriteRequest,
    AIRewriteResponse,
)
from backend.services.ai.draft import generate_cv_draft
from backend.services.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


def _format_validation_error(errors: List[Dict[str, Any]]) -> str:
    """Convert Pydantic validation errors to user-friendly messages."""
    messages = []
    for err in errors:
        field_path = ".".join(str(loc) for loc in err["loc"])
        error_type = err.get("type", "")
        msg = err.get("msg", "")

        # Translate common errors to friendly messages
        if "string_too_long" in error_type or "at most" in msg.lower():
            messages.append(
                f"The AI-generated text for '{field_path}' was too long. "
                f"This can happen when the LLM expands the content. "
                f"Try using 'Select & reorder' style instead, or shorten your profile descriptions."
            )
        elif "string_too_short" in error_type:
            messages.append(f"The field '{field_path}' is too short.")
        elif "missing" in error_type:
            messages.append(f"Required field '{field_path}' is missing.")
        else:
            messages.append(f"{field_path}: {msg}")

    return " | ".join(messages)


def _format_exception_error(exc: Exception) -> str:
    """Convert exceptions to user-friendly error messages."""
    exc_type = type(exc).__name__
    exc_msg = str(exc)

    # Handle HTTP errors from LLM API
    if isinstance(exc, httpx.HTTPStatusError):
        return _format_http_error(exc.response.status_code)

    if isinstance(exc, httpx.TimeoutException):
        return "AI service request timed out. The service may be slow. Please try again."

    if isinstance(exc, httpx.ConnectError):
        return "Could not connect to AI service. Please check your internet connection."

    # Handle common error patterns
    if "timeout" in exc_msg.lower():
        return "Request timed out. The AI service may be slow. Please try again."

    if "rate limit" in exc_msg.lower():
        return "AI rate limit exceeded. Please wait a moment and try again."

    if "api key" in exc_msg.lower() or "authentication" in exc_msg.lower():
        return "AI service authentication error. Please check configuration."

    # Default: include some context but keep it readable
    return f"An error occurred during CV generation: {exc_type} - {exc_msg}"


def _format_http_error(status_code: int) -> str:
    """Format HTTP status code errors."""
    if status_code == 401:
        return "AI service authentication failed. Please check API key configuration."
    if status_code == 429:
        return "AI service rate limit exceeded. Please wait a moment and try again."
    if status_code in (500, 502, 503):
        return "AI service is temporarily unavailable. Please try again later."
    return f"AI service error (HTTP {status_code}). Please try again."


def _handle_validation_error(e: ValidationError) -> HTTPException:
    """Handle Pydantic validation errors."""
    friendly_msg = _format_validation_error(e.errors())
    logger.error(f"CV validation failed: {friendly_msg}", exc_info=e)
    return HTTPException(status_code=400, detail=friendly_msg)


def _handle_value_error(e: ValueError, context: str = "CV generation") -> HTTPException:
    """Handle ValueError (configuration/processing errors)."""
    error_msg = str(e)
    logger.error(f"{context} error: {error_msg}", exc_info=e)
    if "not configured" in error_msg.lower():
        if context == "CV generation":
            error_msg = (
                "AI tailoring requires LLM configuration. "
                "Please set AI_ENABLED=true and configure API credentials, "
                "or use 'Select & reorder' style which doesn't require AI."
            )
        else:
            error_msg = (
                "AI rewrite requires LLM configuration. "
                "Please set AI_ENABLED=true and configure API credentials."
            )
    return HTTPException(status_code=400, detail=error_msg)


def _handle_generic_error(exc: Exception) -> HTTPException:
    """Handle generic exceptions."""
    friendly_msg = _format_exception_error(exc)
    logger.error(f"Failed to generate CV draft: {exc}", exc_info=exc)
    return HTTPException(status_code=500, detail=friendly_msg)


async def _handle_generate_cv_request(payload: AIGenerateCVRequest) -> AIGenerateCVResponse:
    """Handle CV generation request."""
    profile_dict = queries.get_profile()
    if not profile_dict:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = ProfileData.model_validate(profile_dict)
    return await generate_cv_draft(profile, payload)


async def _handle_rewrite_request(payload: AIRewriteRequest) -> AIRewriteResponse:
    """Handle text rewrite request."""
    llm_client = get_llm_client()
    rewritten_text = await llm_client.rewrite_text(payload.text, payload.prompt)
    return AIRewriteResponse(rewritten_text=rewritten_text)


def create_ai_router(limiter: Limiter) -> APIRouter:  # noqa: C901
    """Create AI router with CV generation and rewrite endpoints."""
    router = APIRouter()

    @router.post("/api/ai/generate-cv", response_model=AIGenerateCVResponse)
    @limiter.limit("10/minute")
    async def generate_cv_from_profile_and_jd(request: Request, payload: AIGenerateCVRequest):
        try:
            return await _handle_generate_cv_request(payload)
        except HTTPException:
            raise
        except ValidationError as e:
            raise _handle_validation_error(e)
        except ValueError as e:
            raise _handle_value_error(e, "CV generation")
        except Exception as exc:
            raise _handle_generic_error(exc)

    @router.post("/api/ai/rewrite", response_model=AIRewriteResponse)
    @limiter.limit("20/minute")
    async def rewrite_text(request: Request, payload: AIRewriteRequest):
        """Rewrite text using LLM with a custom prompt."""
        try:
            return await _handle_rewrite_request(payload)
        except ValueError as e:
            raise _handle_value_error(e, "LLM rewrite")
        except Exception as exc:
            raise _handle_generic_error(exc)

    return router
