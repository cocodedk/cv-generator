"""Render CV data into HTML for DOCX conversion."""
import re
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates" / "html"


def render_html(cv_data: Dict[str, Any]) -> str:
    """Render CV data into HTML using Jinja2 templates."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("base.html")

    # Prepare data for template
    template_data = _prepare_template_data(cv_data)

    return template.render(**template_data)


def _prepare_template_data(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare CV data for template rendering."""
    personal_info = cv_data.get("personal_info", {}).copy()

    # Format address if it exists
    address = personal_info.get("address")
    if address:
        personal_info["address"] = _format_address(address)

    experience = _prepare_experience(cv_data.get("experience", []))
    skills_by_category = _prepare_skills(cv_data.get("skills", []))

    return {
        "personal_info": personal_info,
        "experience": experience,
        "education": cv_data.get("education", []),
        "skills_by_category": skills_by_category,
        "theme": cv_data.get("theme", "classic"),
        "layout": cv_data.get("layout", "classic-two-column"),
    }


def _prepare_experience(experience_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare experience items for template rendering."""
    experience = []
    for exp in experience_list:
        exp_copy = exp.copy()
        _process_experience_description(exp_copy, exp.get("description", ""))
        exp_copy["projects"] = _prepare_projects(exp.get("projects") or [])
        experience.append(exp_copy)
    return experience


def _process_experience_description(exp_copy: Dict[str, Any], description: str) -> None:
    """Process and format experience description."""
    if description:
        desc_data = _split_description(description)
        exp_copy["description_format"] = desc_data["format"]
        if desc_data["format"] == "list":
            exp_copy["description_lines"] = desc_data["content"]
        elif desc_data["format"] == "paragraphs":
            exp_copy["description_paragraphs"] = desc_data["content"]
        else:  # paragraph
            exp_copy["description_text"] = desc_data["content"]
    else:
        # Default to paragraph format for empty descriptions
        exp_copy["description_format"] = "paragraph"
        exp_copy["description_text"] = ""


def _prepare_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare project items for template rendering."""
    prepared_projects = []
    for project in projects:
        proj_copy = project.copy()
        proj_copy["highlights"] = _normalize_highlights(
            proj_copy.get("highlights") or []
        )
        proj_copy["technologies"] = _normalize_technologies(
            proj_copy.get("technologies") or []
        )
        prepared_projects.append(proj_copy)
    return prepared_projects


def _normalize_highlights(highlights: Any) -> List[str]:
    """Normalize highlights to a list of strings."""
    if isinstance(highlights, str):
        return [
            _clean_list_item(line)
            for line in highlights.splitlines()
            if _clean_list_item(line)
        ]
    return highlights


def _normalize_technologies(technologies: Any) -> List[str]:
    """Normalize technologies to a list of strings."""
    if isinstance(technologies, str):
        return [tech.strip() for tech in technologies.split(",") if tech.strip()]
    return technologies


def _prepare_skills(skills: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
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
        skill_list.sort(
            key=lambda s: (s.get("name", "").lower(), s.get("level", "").lower())
        )

    # Sort categories alphabetically, with "Other" last
    sorted_categories = sorted(
        skills_by_category.keys(), key=lambda cat: (cat == "Other", cat.lower())
    )

    # Return dict with sorted order (Python 3.7+ maintains insertion order)
    return {category: skills_by_category[category] for category in sorted_categories}


def _format_address(address: Any) -> str:
    """Format address dict or string into a single string."""
    if not address:
        return ""
    if isinstance(address, str):
        return address
    parts = [
        address.get("street"),
        address.get("city"),
        address.get("state"),
        address.get("zip"),
        address.get("country"),
    ]
    return ", ".join([part for part in parts if part])


def _is_list_item(line: str) -> bool:
    """Check if a line is a list item (bullet or numbered)."""
    stripped = line.strip()
    list_markers = ["-", "*", "•"]
    if any(stripped.startswith(marker) for marker in list_markers):
        return True
    if stripped and stripped[0].isdigit() and len(stripped) > 1:
        return stripped[1] in [".", ")"]
    return False


def _count_list_items(lines: List[str]) -> int:
    """Count how many lines are list items."""
    return sum(1 for line in lines if _is_list_item(line))


def _clean_list_item(line: str) -> str:
    """Remove list markers and numbered prefixes from a line."""
    stripped = line.strip()
    list_markers = ["-", "*", "•"]
    for marker in list_markers:
        if stripped.startswith(marker):
            stripped = stripped[1:].strip()
            break
    if stripped and stripped[0].isdigit():
        stripped = re.sub(r"^\d+[.)]\s*", "", stripped)
    return stripped


def _process_as_list(non_empty_lines: List[str]) -> List[str]:
    """Process lines as a list, cleaning markers."""
    items = []
    for line in non_empty_lines:
        cleaned = _clean_list_item(line)
        if cleaned:
            items.append(cleaned)
    return items


def _split_description(description: str) -> Dict[str, Any]:
    """
    Split description and detect format (list vs paragraph).
    Returns dict with 'format' and 'content' keys.
    """
    if not description:
        return {"format": "paragraph", "content": ""}

    lines = description.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    if not non_empty_lines:
        return {"format": "paragraph", "content": ""}

    # Check if it's a list: count lines starting with list markers
    list_count = _count_list_items(non_empty_lines)
    is_list = list_count >= len(non_empty_lines) * 0.5 and len(non_empty_lines) > 1

    if is_list:
        items = _process_as_list(non_empty_lines)
        return {"format": "list", "content": items}

    # Check for multiple paragraphs (double newlines)
    if "\n\n" in description:
        paragraphs = []
        for para in description.split("\n\n"):
            cleaned = para.strip().replace("\n", " ")
            if cleaned:
                paragraphs.append(cleaned)
        if len(paragraphs) > 1:
            return {"format": "paragraphs", "content": paragraphs}

    # Single paragraph: join all lines with spaces
    paragraph_text = " ".join(line.strip() for line in lines if line.strip())
    return {"format": "paragraph", "content": paragraph_text}
