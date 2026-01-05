"""Create operations for profile update - compatibility module."""
# Re-export from refactored submodules for backward compatibility
from backend.database.queries.profile_update.person import (
    create_person_node,
)
from backend.database.queries.profile_update.experience import (
    create_experience_nodes,
)
from backend.database.queries.profile_update.education import (
    create_education_nodes,
)
from backend.database.queries.profile_update.skill import (
    create_skill_nodes,
)

__all__ = [
    "create_person_node",
    "create_experience_nodes",
    "create_education_nodes",
    "create_skill_nodes",
]
