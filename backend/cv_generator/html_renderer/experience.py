"""Experience preparation for HTML rendering."""
from typing import Dict, Any, List
from datetime import datetime
from backend.cv_generator.html_renderer.utils import split_description
from backend.cv_generator.html_renderer.projects import prepare_projects


def _parse_date(date_str: str) -> datetime:
    """Parse date string in YYYY-MM format to datetime for sorting."""
    try:
        return datetime.strptime(date_str, "%Y-%m")
    except (ValueError, TypeError):
        # If parsing fails, return a very old date to push to end
        return datetime(1900, 1, 1)


def _sort_key(exp: Dict[str, Any]) -> datetime:
    """Get sort key for experience item (most recent first)."""
    start_date = exp.get("start_date", "")
    if not start_date:
        return datetime(1900, 1, 1)
    return _parse_date(start_date)


def prepare_experience(experience_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare experience items for template rendering in reverse-chronological order."""
    experience = []
    for exp in experience_list:
        exp_copy = exp.copy()
        process_experience_description(exp_copy, exp.get("description", ""))
        exp_copy["projects"] = prepare_projects(exp.get("projects") or [])
        experience.append(exp_copy)

    # Sort in reverse-chronological order (most recent first)
    experience.sort(key=_sort_key, reverse=True)
    return experience


def process_experience_description(exp_copy: Dict[str, Any], description: str) -> None:
    """Process and format experience description."""
    if description:
        desc_data = split_description(description)
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
