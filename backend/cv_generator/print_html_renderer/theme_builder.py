"""Theme CSS building utilities."""


def _build_theme_css(accent: str, accent_2: str, ink: str, muted: str) -> str:
    """Build CSS override for theme colors."""
    # Return CSS that will override the :root variables
    return (
        f":root{{--accent:{accent};--accent-2:{accent_2};--ink:{ink};--muted:{muted};}}"
    )
