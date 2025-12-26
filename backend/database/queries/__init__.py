"""Database query modules."""
from backend.database.queries.create import create_cv
from backend.database.queries.read import get_cv_by_id, get_cv_by_filename
from backend.database.queries.list import list_cvs, search_cvs
from backend.database.queries.update import update_cv, set_cv_filename
from backend.database.queries.delete import delete_cv
from backend.database.queries.profile import (
    save_profile,
    create_profile,
    update_profile,
    get_profile,
    delete_profile,
    delete_profile_by_updated_at,
    list_profiles,
    get_profile_by_updated_at,
)

__all__ = [
    "create_cv",
    "get_cv_by_id",
    "get_cv_by_filename",
    "list_cvs",
    "search_cvs",
    "update_cv",
    "set_cv_filename",
    "delete_cv",
    "save_profile",
    "create_profile",
    "update_profile",
    "get_profile",
    "delete_profile",
    "delete_profile_by_updated_at",
    "list_profiles",
    "get_profile_by_updated_at",
]
