"""Template data preparation for HTML rendering."""
from typing import Dict, Any
from backend.cv_generator_docx.html_renderer.utils import format_address
from backend.cv_generator_docx.html_renderer.experience import prepare_experience
from backend.cv_generator_docx.html_renderer.skills import prepare_skills


def prepare_template_data(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare CV data for template rendering."""
    personal_info = cv_data.get("personal_info", {}).copy()

    # Format address if it exists
    address = personal_info.get("address")
    if address:
        personal_info["address"] = format_address(address)

    experience = prepare_experience(cv_data.get("experience", []))
    skills_by_category = prepare_skills(cv_data.get("skills", []))

    return {
        "personal_info": personal_info,
        "experience": experience,
        "education": cv_data.get("education", []),
        "skills_by_category": skills_by_category,
        "theme": cv_data.get("theme", "classic"),
    }
