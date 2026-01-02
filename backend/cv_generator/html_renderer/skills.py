"""Skills preparation for HTML rendering."""
from typing import Dict, Any, List


def prepare_skills(skills: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
    """Prepare skills grouped by category, sorted alphabetically."""
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

    # Sort skills within each category by name, then by level
    for category, skill_list in skills_by_category.items():
        skill_list.sort(key=lambda s: (
            s.get("name", "").lower(),
            s.get("level", "").lower()
        ))

    # Sort categories alphabetically, with "Other" last
    sorted_categories = sorted(
        skills_by_category.keys(),
        key=lambda cat: (cat == "Other", cat.lower())
    )

    # Return dict with sorted order (Python 3.7+ maintains insertion order)
    return {category: skills_by_category[category] for category in sorted_categories}
