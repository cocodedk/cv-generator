"""Read profile queries - compatibility module."""
# Re-export from refactored submodule for backward compatibility
from backend.database.queries.profile_read import (
    get_profile,
    get_profile_by_updated_at,
    list_profiles,
)
