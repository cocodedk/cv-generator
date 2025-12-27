"""Layout registry and validation."""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Layout metadata: name, description, print_friendly, web_optimized
LAYOUTS: Dict[str, Dict[str, Any]] = {
    "classic-two-column": {
        "name": "Classic Two-Column",
        "description": "Traditional print-first layout with left sidebar and main content",
        "print_friendly": True,
        "web_optimized": False,
    },
    "ats-single-column": {
        "name": "ATS-Optimized Single Column",
        "description": "Maximum compatibility with ATS parsers, minimal decoration",
        "print_friendly": True,
        "web_optimized": False,
    },
    "modern-sidebar": {
        "name": "Modern Sidebar",
        "description": "Web-first with persistent sidebar, still printable",
        "print_friendly": True,
        "web_optimized": True,
    },
    "section-cards-grid": {
        "name": "Section Cards Grid",
        "description": "Web presentation with card-based sections",
        "print_friendly": False,
        "web_optimized": True,
    },
    "career-timeline": {
        "name": "Career Timeline",
        "description": "Narrative progression with timeline visualization",
        "print_friendly": True,
        "web_optimized": True,
    },
    "project-case-studies": {
        "name": "Project Case Studies",
        "description": "Long-scroll story format for projects",
        "print_friendly": False,
        "web_optimized": True,
    },
    "portfolio-spa": {
        "name": "Portfolio SPA",
        "description": "Multi-route web CV with navigation",
        "print_friendly": False,
        "web_optimized": True,
    },
    "interactive-skills-matrix": {
        "name": "Interactive Skills Matrix",
        "description": "Web showcase with filtering and interaction",
        "print_friendly": False,
        "web_optimized": True,
    },
    "academic-cv": {
        "name": "Academic CV",
        "description": "Publications-first layout for academic use",
        "print_friendly": True,
        "web_optimized": False,
    },
    "dark-mode-tech": {
        "name": "Dark Mode Tech",
        "description": "Web showcase with dark mode support",
        "print_friendly": False,
        "web_optimized": True,
    },
}


def get_layout(layout_name: str) -> Dict[str, Any]:
    """Get layout definition by name."""
    return LAYOUTS.get(layout_name, LAYOUTS["classic-two-column"])


def validate_layout(layout_name: str) -> str:
    """Validate layout name and return valid layout or default to classic-two-column."""
    if layout_name not in LAYOUTS:
        logger.warning(
            "Invalid layout '%s', defaulting to 'classic-two-column'. Valid layouts: %s",
            layout_name,
            list(LAYOUTS.keys()),
        )
        return "classic-two-column"
    return layout_name
