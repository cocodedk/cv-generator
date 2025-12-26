"""Experience preparation for HTML rendering."""
from typing import Dict, Any, List
from backend.cv_generator_docx.html_renderer.utils import split_description
from backend.cv_generator_docx.html_renderer.projects import prepare_projects


def prepare_experience(experience_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare experience items for template rendering."""
    experience = []
    for exp in experience_list:
        exp_copy = exp.copy()
        process_experience_description(exp_copy, exp.get("description", ""))
        exp_copy["projects"] = prepare_projects(exp.get("projects") or [])
        experience.append(exp_copy)
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
