"""Exception handlers for FastAPI application."""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def _build_friendly_field_name(loc: tuple) -> str:  # noqa: C901
    """Convert field location to user-friendly name."""
    if not loc:
        return "Unknown field"

    field_labels = {
        "personal_info": {
            "name": "Full Name",
            "title": "Professional Title",
            "email": "Email",
            "phone": "Phone",
            "address": "Address",
            "linkedin": "LinkedIn",
            "github": "GitHub",
            "website": "Website",
            "summary": "Professional Summary",
        },
        "experience": {
            "title": "Job Title",
            "company": "Company",
            "start_date": "Start Date",
            "end_date": "End Date",
            "description": "Role Summary",
            "location": "Location",
        },
        "education": {
            "degree": "Degree",
            "institution": "Institution",
            "year": "Year",
            "field": "Field",
            "gpa": "GPA",
        },
        "skills": {
            "name": "Skill Name",
            "category": "Category",
            "level": "Level",
        },
    }

    parts = list(loc)
    if not parts:
        return "Unknown field"

    # Handle array indices
    result_parts = []
    i = 0
    while i < len(parts):
        part = parts[i]

        if isinstance(part, int):
            # Array index - get the previous part to know what array
            if i > 0 and isinstance(parts[i - 1], str):
                array_name = parts[i - 1]
                index_num = part + 1  # 1-based for user display

                if array_name == "experience":
                    result_parts.append(f"Experience {index_num}")
                elif array_name == "education":
                    result_parts.append(f"Education {index_num}")
                elif array_name == "skills":
                    result_parts.append(f"Skill {index_num}")
                else:
                    result_parts.append(f"{array_name}[{part}]")
            i += 1
        elif isinstance(part, str):
            # Field name
            if part in field_labels:
                # This is a section, not a field yet
                i += 1
                continue
            else:
                # This is a field name
                section = (
                    parts[i - 2] if i >= 2 and isinstance(parts[i - 2], str) else None
                )
                if (
                    section
                    and section in field_labels
                    and part in field_labels[section]
                ):
                    field_label = field_labels[section][part]
                    if result_parts:
                        result_parts.append(f" - {field_label}")
                    else:
                        result_parts.append(field_label)
                else:
                    result_parts.append(part.replace("_", " ").title())
                i += 1
        else:
            i += 1

    return "".join(result_parts) if result_parts else "Unknown field"


def _build_field_path(loc: tuple) -> str:
    """Build react-hook-form compatible field path (e.g., 'experience.0.description')."""
    if not loc:
        return ""

    path_parts = []
    for part in loc:
        if isinstance(part, int):
            if path_parts:
                path_parts.append(f".{part}")
            else:
                path_parts.append(str(part))
        elif path_parts:
            path_parts.append(f".{part}")
        else:
            path_parts.append(str(part))

    return "".join(path_parts)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic validation errors to user-friendly messages."""
    import logging

    logger = logging.getLogger(__name__)
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
        field_name = _build_friendly_field_name(loc_without_body)
        field_path = _build_field_path(loc_without_body)  # For frontend mapping

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
