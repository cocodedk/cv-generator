"""Skills preparation for HTML rendering."""
from typing import Dict, Any, List


def prepare_skills(skills: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
    """Prepare skills grouped by category."""
    skills_by_category: Dict[str, List[Dict[str, str]]] = {}
    for skill in skills:
        category = skill.get("category") or "Other"
        name = skill.get("name", "")
        if name:
            skill_obj = {"name": name}
            level = skill.get("level")
            if level:
                skill_obj["level"] = level
            skills_by_category.setdefault(category, []).append(skill_obj)
    return skills_by_category
