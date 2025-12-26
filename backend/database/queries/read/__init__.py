"""CV read queries module."""
from backend.database.queries.read.get import (
    get_cv_by_id,
    get_cv_by_filename,
)

__all__ = [
    "get_cv_by_id",
    "get_cv_by_filename",
]
