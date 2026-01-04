"""Create operations for profile update - compatibility module."""
# Re-export from refactored submodules for backward compatibility
from backend.database.queries.profile_update.person import (
    create_person_node,
)  # noqa: F401
from backend.database.queries.profile_update.experience import (
    create_experience_nodes,
)  # noqa: F401
from backend.database.queries.profile_update.education import (
    create_education_nodes,
)  # noqa: F401
from backend.database.queries.profile_update.skill import (
    create_skill_nodes,
)  # noqa: F401
