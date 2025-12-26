"""Profile data extracted from docs/me.md."""
from typing import Dict, Any
from backend.scripts.create_profile_from_me.personal_info import get_personal_info
from backend.scripts.create_profile_from_me.experience import get_experience_data
from backend.scripts.create_profile_from_me.education import get_education_data
from backend.scripts.create_profile_from_me.skills import get_skills_data


def get_profile_data() -> Dict[str, Any]:
    """Get profile data extracted from docs/me.md.

    Returns:
        Dictionary containing personal_info, experience, education, and skills
    """
    return {
        "personal_info": get_personal_info(),
        "experience": get_experience_data(),
        "education": get_education_data(),
        "skills": get_skills_data()
    }
