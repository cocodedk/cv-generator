"""Cover letter generation routes."""

# Re-export main functionality for backward compatibility
from backend.app_helpers.routes.cover_letter.router import create_cover_letter_router
from backend.app_helpers.routes.cover_letter.endpoints import (
    generate_cover_letter_endpoint,
    export_cover_letter_pdf,
    save_cover_letter_endpoint,
    list_cover_letters_endpoint,
    get_cover_letter_endpoint,
    delete_cover_letter_endpoint,
)
from backend.app_helpers.routes.cover_letter.error_handlers import (
    _format_validation_error,
    _handle_validation_error,
    _handle_value_error,
    _handle_generic_error,
)
from backend.app_helpers.routes.cover_letter.request_handlers import (
    _handle_generate_cover_letter_request,
)
from backend.database import queries

__all__ = [
    "create_cover_letter_router",
    "generate_cover_letter_endpoint",
    "export_cover_letter_pdf",
    "save_cover_letter_endpoint",
    "list_cover_letters_endpoint",
    "get_cover_letter_endpoint",
    "delete_cover_letter_endpoint",
    "_format_validation_error",
    "_handle_validation_error",
    "_handle_value_error",
    "_handle_generic_error",
    "_handle_generate_cover_letter_request",
    "queries",
]
