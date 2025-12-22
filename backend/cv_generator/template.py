"""Template handling for CV generation."""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_template(template_path: str) -> Dict[str, Any]:
    """Load CV template from YAML file."""
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    with open(path, 'r') as f:
        return yaml.safe_load(f)


def validate_template(template_data: Dict[str, Any]) -> bool:
    """Validate template data structure."""
    required_sections = ['personal_info']
    for section in required_sections:
        if section not in template_data:
            return False
    return True
