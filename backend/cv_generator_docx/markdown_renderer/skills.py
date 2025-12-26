"""Skills section rendering."""
from typing import Dict, Any, List


def render_skills(skills: List[Dict[str, Any]]) -> List[str]:
    """Render skills grouped by category."""
    lines: List[str] = []
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

    for category, skill_list in skills_by_category.items():
        lines.append(f"### {category}")
        for skill in skill_list:
            name = skill.get("name", "")
            level = skill.get("level")
            if level:
                lines.append(f"- {name} ({level})")
            else:
                lines.append(f"- {name}")
        lines.append("")
    return lines
