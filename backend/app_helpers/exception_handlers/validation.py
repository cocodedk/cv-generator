"""Validation exception handler."""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.app_helpers.exception_handlers.field_names import build_friendly_field_name
from backend.app_helpers.exception_handlers.field_paths import build_field_path

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic validation errors to user-friendly messages."""
    logger.error("Validation error: %s", exc.errors())
    error_messages = []
    modified_errors = []
    error_mapping = {
        "value_error.email": "Email format invalid",
        "value_error.missing": "Field is required",
        "type_error.str": "Expected text value",
        "type_error.integer": "Expected number value",
        "value_error.str.min_length": "Value is too short",
        "value_error.str.max_length": "Value is too long",
        "string_too_long": "Value is too long",
    }

    for error in exc.errors():
        loc = error["loc"]

        # Skip leading "body" element if present
        if loc and loc[0] == "body":
            loc_without_body = loc[1:]
        else:
            loc_without_body = loc

        error_type = error.get("type", "")
        error_msg = error.get("msg", "")
        ctx = error.get("ctx", {})

        # Build user-friendly field name
        field_name = build_friendly_field_name(loc_without_body)
        field_path = build_field_path(loc_without_body)  # For frontend mapping

        # Try to map to friendly message
        friendly_msg = error_mapping.get(error_type, error_msg)

        # Add context for length errors
        if error_type == "string_too_long" and "max_length" in ctx:
            max_len = ctx["max_length"]
            friendly_msg = f"Maximum {max_len} characters allowed. Please shorten or move details to projects."

        error_messages.append(f"{field_name}: {friendly_msg}")

        # Store field path in error for frontend mapping
        error_copy = error.copy()
        error_copy["field_path"] = field_path
        modified_errors.append(error_copy)

    return JSONResponse(
        status_code=422,
        content={"detail": error_messages, "errors": modified_errors},
    )
