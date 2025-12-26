"""Delete profile queries - compatibility module."""
# Re-export from refactored submodule for backward compatibility
from backend.database.queries.profile_delete.delete import (  # noqa: F401
    delete_profile,
    delete_profile_by_updated_at,
)
