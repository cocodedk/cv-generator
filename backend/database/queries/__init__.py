"""Database query modules."""
from backend.database.queries.create import create_cv
from backend.database.queries.create.cover_letter import create_cover_letter_node
from backend.database.queries.read import get_cv_by_id, get_cv_by_filename
from backend.database.queries.read.cover_letter_get import get_cover_letter_by_id
from backend.database.queries.list import list_cvs, search_cvs
from backend.database.queries.list.cover_letter_list import list_cover_letters
from backend.database.queries.update import update_cv, set_cv_filename
from backend.database.queries.delete import delete_cv, delete_cover_letter
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
from backend.database.queries.profile_read.get import get_profile_by_language

__all__ = [
    "create_cv",
    "create_cover_letter_node",
    "get_cv_by_id",
    "get_cv_by_filename",
    "get_cover_letter_by_id",
    "list_cvs",
    "search_cvs",
    "list_cover_letters",
    "update_cv",
    "set_cv_filename",
    "delete_cv",
    "delete_cover_letter",
    "save_profile",
    "create_profile",
    "update_profile",
    "get_profile",
    "delete_profile",
    "delete_profile_by_updated_at",
    "list_profiles",
    "get_profile_by_updated_at",
    "get_profile_by_language",
]
