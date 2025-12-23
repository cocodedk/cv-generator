"""Theme registry and helpers."""
import logging
from backend.themes.classic import THEME as CLASSIC
from backend.themes.modern import THEME as MODERN
from backend.themes.minimal import THEME as MINIMAL
from backend.themes.elegant import THEME as ELEGANT
from backend.themes.accented import THEME as ACCENTED

logger = logging.getLogger(__name__)

THEMES = {
    "classic": CLASSIC,
    "modern": MODERN,
    "minimal": MINIMAL,
    "elegant": ELEGANT,
    "accented": ACCENTED,
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
