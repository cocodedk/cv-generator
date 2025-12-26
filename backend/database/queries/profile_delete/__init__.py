"""Profile delete queries module."""
from backend.database.queries.profile_delete.delete import (
    delete_profile,
    delete_profile_by_updated_at,
)

__all__ = [
    "delete_profile",
    "delete_profile_by_updated_at",
]
