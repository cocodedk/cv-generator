"""List and search CV queries module."""
from backend.database.queries.list.list import list_cvs
from backend.database.queries.list.search import search_cvs

__all__ = [
    "list_cvs",
    "search_cvs",
]
