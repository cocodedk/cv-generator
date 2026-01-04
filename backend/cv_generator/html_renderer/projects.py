"""Project preparation for HTML rendering."""
from typing import Any, List, Dict
from backend.cv_generator.html_renderer.utils import clean_list_item


def prepare_projects(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare project items for template rendering."""
    prepared_projects = []
    for project in projects:
        proj_copy = project.copy()
        proj_copy["highlights"] = normalize_highlights(
            proj_copy.get("highlights") or []
        )
        proj_copy["technologies"] = normalize_technologies(
            proj_copy.get("technologies") or []
        )
        prepared_projects.append(proj_copy)
    return prepared_projects


def normalize_highlights(highlights: Any) -> List[str]:
    """Normalize highlights to a list of strings."""
    if isinstance(highlights, str):
        return [
            clean_list_item(line)
            for line in highlights.splitlines()
            if clean_list_item(line)
        ]
    return highlights


def normalize_technologies(technologies: Any) -> List[str]:
    """Normalize technologies to a list of strings."""
    if isinstance(technologies, str):
        return [tech.strip() for tech in technologies.split(",") if tech.strip()]
    return technologies
