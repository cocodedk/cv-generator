"""Error handling utilities for cover letter endpoints."""

import logging
from fastapi import HTTPException
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def _format_validation_error(errors: list) -> str:
    """Convert Pydantic validation errors to user-friendly messages."""
    messages = []
    for err in errors:
        field_path = ".".join(str(loc) for loc in err["loc"])
        error_type = err.get("type", "")
        msg = err.get("msg", "")

        if "string_too_long" in error_type or "at most" in msg.lower():
            messages.append(f"The field '{field_path}' is too long.")
        elif "string_too_short" in error_type:
            messages.append(f"The field '{field_path}' is too short.")
        elif "missing" in error_type:
            messages.append(f"Required field '{field_path}' is missing.")
        else:
            messages.append(f"{field_path}: {msg}")

    return " | ".join(messages)


def _handle_validation_error(e: ValidationError) -> HTTPException:
    """Handle Pydantic validation errors."""
    friendly_msg = _format_validation_error(e.errors())
    logger.error(f"Cover letter validation failed: {friendly_msg}", exc_info=e)
    return HTTPException(status_code=400, detail=friendly_msg)


def _handle_value_error(e: ValueError) -> HTTPException:
    """Handle ValueError (configuration/processing errors)."""
    error_msg = str(e)
    logger.error(f"Cover letter generation error: {error_msg}", exc_info=e)
    if "not configured" in error_msg.lower():
        error_msg = (
            "AI cover letter generation requires LLM configuration. "
            "Please set AI_ENABLED=true and configure API credentials."
        )
    return HTTPException(status_code=400, detail=error_msg)


def _handle_generic_error(exc: Exception) -> HTTPException:
    """Handle generic exceptions."""
    error_msg = f"Failed to generate cover letter: {str(exc)}"
    logger.error(f"Failed to generate cover letter: {exc}", exc_info=exc)
    return HTTPException(status_code=500, detail=error_msg)
