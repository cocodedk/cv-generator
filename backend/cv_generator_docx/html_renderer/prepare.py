"""Template data preparation for HTML rendering."""
from typing import Dict, Any, List
from backend.cv_generator_docx.html_renderer.utils import format_address
from backend.cv_generator_docx.html_renderer.experience import prepare_experience
from backend.cv_generator_docx.html_renderer.skills import prepare_skills


def _parse_year(year_str: Any) -> int:
    """Parse year string to integer for sorting."""
    if not year_str:
        return 0
    try:
        return int(str(year_str))
    except (ValueError, TypeError):
        return 0


def _sort_education_key(edu: Dict[str, Any]) -> int:
    """Get sort key for education item (most recent first)."""
    year = edu.get("year", "")
    return _parse_year(year)


def prepare_education(education_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare education items in reverse-chronological order."""
    education = list(education_list)
    # Sort in reverse-chronological order (most recent first)
    education.sort(key=_sort_education_key, reverse=True)
    return education


def prepare_template_data(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare CV data for template rendering."""
    personal_info = cv_data.get("personal_info", {}).copy()

    # Format address if it exists
    address = personal_info.get("address")
    if address:
        personal_info["address"] = format_address(address)

    experience = prepare_experience(cv_data.get("experience", []))
    education = prepare_education(cv_data.get("education", []))
    skills_by_category = prepare_skills(cv_data.get("skills", []))

    return {
        "personal_info": personal_info,
        "experience": experience,
        "education": education,
        "skills_by_category": skills_by_category,
        "theme": cv_data.get("theme", "classic"),
        "layout": cv_data.get("layout", "classic-two-column"),
    }
