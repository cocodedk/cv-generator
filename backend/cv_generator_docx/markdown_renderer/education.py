"""Education section rendering."""
from typing import Dict, Any, List


def render_education(edu: Dict[str, Any]) -> List[str]:
    """Render a single education entry."""
    lines: List[str] = []
    degree = edu.get("degree", "")
    institution = edu.get("institution", "")
    heading = ", ".join([part for part in [degree, institution] if part])
    if heading:
        lines.append(f"### {heading}")
    info_parts = [
        edu.get("year"),
        edu.get("field"),
        f"GPA: {edu['gpa']}" if edu.get("gpa") else None,
    ]
    info = " | ".join([part for part in info_parts if part])
    if info:
        lines.append(info)
    lines.append("")
    return lines
