"""Create profile from docs/me.md data - modular components."""
from backend.scripts.create_profile_from_me.profile_data import get_profile_data
from backend.scripts.create_profile_from_me.create import create_profile
from backend.scripts.create_profile_from_me.personal_info import get_personal_info
from backend.scripts.create_profile_from_me.experience import get_experience_data
from backend.scripts.create_profile_from_me.education import get_education_data
from backend.scripts.create_profile_from_me.skills import get_skills_data

__all__ = [
    'get_profile_data',
    'create_profile',
    'get_personal_info',
    'get_experience_data',
    'get_education_data',
    'get_skills_data',
]
