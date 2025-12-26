"""Theme registry and helpers."""
import logging
from backend.themes.classic import THEME as CLASSIC
from backend.themes.modern import THEME as MODERN
from backend.themes.minimal import THEME as MINIMAL
from backend.themes.elegant import THEME as ELEGANT
from backend.themes.accented import THEME as ACCENTED
from backend.themes.professional import THEME as PROFESSIONAL
from backend.themes.creative import THEME as CREATIVE
from backend.themes.tech import THEME as TECH
from backend.themes.executive import THEME as EXECUTIVE
from backend.themes.colorful import THEME as COLORFUL

logger = logging.getLogger(__name__)

THEMES = {
    "classic": CLASSIC,
    "modern": MODERN,
    "minimal": MINIMAL,
    "elegant": ELEGANT,
    "accented": ACCENTED,
    "professional": PROFESSIONAL,
    "creative": CREATIVE,
    "tech": TECH,
    "executive": EXECUTIVE,
    "colorful": COLORFUL,
}


def get_theme(theme_name: str) -> dict:
    """Get theme definition by name."""
    return THEMES.get(theme_name, THEMES["classic"])


def validate_theme(theme_name: str) -> str:
    """Validate theme name and return valid theme or default to classic."""
    if theme_name not in THEMES:
        logger.warning(
            "Invalid theme '%s', defaulting to 'classic'. Valid themes: %s",
            theme_name,
            list(THEMES.keys()),
        )
        return "classic"
    return theme_name
