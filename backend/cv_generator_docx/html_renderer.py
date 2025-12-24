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

    # Preprocess experience descriptions
    experience = []
    for exp in cv_data.get("experience", []):
        exp_copy = exp.copy()
        description = exp.get("description", "")
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
        experience.append(exp_copy)

    # Preprocess skills by category
    skills_by_category: Dict[str, List[Dict[str, str]]] = {}
    for skill in cv_data.get("skills", []):
        category = skill.get("category") or "Other"
        name = skill.get("name", "")
        if name:
            skill_obj = {"name": name}
            level = skill.get("level")
            if level:
                skill_obj["level"] = level
            skills_by_category.setdefault(category, []).append(skill_obj)

    return {
        "personal_info": personal_info,
        "experience": experience,
        "education": cv_data.get("education", []),
        "skills_by_category": skills_by_category,
        "theme": cv_data.get("theme", "classic"),
    }


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
    list_markers = ["-", "*", "•"]
    list_count = 0
    for line in non_empty_lines:
        stripped = line.strip()
        # Check for numbered list (1., 2., etc.) or bullet markers
        if any(stripped.startswith(marker) for marker in list_markers):
            list_count += 1
        elif stripped and stripped[0].isdigit() and len(stripped) > 1 and stripped[1] in [".", ")"]:
            list_count += 1

    # If ≥50% of lines are list items, treat as list
    is_list = list_count >= len(non_empty_lines) * 0.5 and len(non_empty_lines) > 1

    if is_list:
        # Process as list: clean and extract items
        items = []
        for line in non_empty_lines:
            stripped = line.strip()
            # Remove list markers
            for marker in list_markers:
                if stripped.startswith(marker):
                    stripped = stripped[1:].strip()
                    break
            # Remove numbered list prefix (1., 2., etc.)
            if stripped and stripped[0].isdigit():
                stripped = re.sub(r"^\d+[.)]\s*", "", stripped)
            if stripped:
                items.append(stripped)
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
