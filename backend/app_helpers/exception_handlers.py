"""Exception handlers for FastAPI application."""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic validation errors to user-friendly messages."""
    error_messages = []
    error_mapping = {
        "value_error.email": "Email format invalid",
        "value_error.missing": "Field is required",
        "type_error.str": "Expected text value",
        "type_error.integer": "Expected number value",
        "value_error.str.min_length": "Value is too short",
        "value_error.str.max_length": "Value is too long",
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

        # Try to map to friendly message
        friendly_msg = error_mapping.get(error_type, error_msg)

        # Extract field name (last part of path, or "unknown field" if empty)
        if loc_without_body:
            field_name = str(loc_without_body[-1])
        else:
            field_name = "unknown field"

        error_messages.append(f"{field_name}: {friendly_msg}")

    return JSONResponse(
        status_code=422,
        content={"detail": error_messages, "errors": exc.errors()},
    )
