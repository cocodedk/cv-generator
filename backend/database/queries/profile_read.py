"""Read profile queries - compatibility module."""
# Re-export from refactored submodule for backward compatibility
from backend.database.queries.profile_read.get import (  # noqa: F401
    get_profile,
    get_profile_by_updated_at,
    get_profile_by_language,
)
from backend.database.queries.profile_read.list import list_profiles  # noqa: F401
