"""Database query modules."""
from backend.database.queries.create import create_cv
from backend.database.queries.read import get_cv_by_id
from backend.database.queries.list import list_cvs, search_cvs
from backend.database.queries.update import update_cv, set_cv_filename
from backend.database.queries.delete import delete_cv
from backend.database.queries.profile import save_profile, get_profile, delete_profile

__all__ = [
    "create_cv",
    "get_cv_by_id",
    "list_cvs",
    "search_cvs",
    "update_cv",
    "set_cv_filename",
    "delete_cv",
    "save_profile",
    "get_profile",
    "delete_profile",
]
