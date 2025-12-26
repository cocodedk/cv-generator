"""Create operations for CV update - compatibility module."""
# Re-export from refactored submodules for backward compatibility
from backend.database.queries.update.person import create_person_node  # noqa: F401
from backend.database.queries.update.experience import create_experience_nodes  # noqa: F401
from backend.database.queries.update.education import create_education_nodes  # noqa: F401
from backend.database.queries.update.skill import create_skill_nodes  # noqa: F401
