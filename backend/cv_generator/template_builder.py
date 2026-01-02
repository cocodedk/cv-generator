"""DOCX template builder for themes."""
from pathlib import Path
from docx import Document
from backend.themes import THEMES, validate_theme
from backend.cv_generator.custom_styles import add_custom_styles
from backend.cv_generator.style_utils import apply_paragraph_style


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def ensure_template(theme_name: str) -> Path:
    """Ensure a DOCX template exists for the theme."""
    theme = validate_theme(theme_name)
    path = TEMPLATES_DIR / f"{theme}.docx"
    if not path.exists():
        build_template(theme, path)
    return path


def build_template(theme_name: str, output_path: Path) -> None:
    """Build a DOCX template with themed styles."""
    theme = THEMES[theme_name]
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document()

    apply_paragraph_style(
        doc.styles["Normal"],
        theme,
        theme["normal"],
        theme["spacing"]["normal"],
        theme["line_height"]["normal"],
    )
    apply_paragraph_style(
        doc.styles["Heading 1"],
        theme,
        theme["heading"],
        theme["spacing"]["heading"],
        theme["line_height"]["heading"],
    )
    apply_paragraph_style(
        doc.styles["Heading 2"],
        theme,
        theme["subheading"],
        theme["spacing"]["subheading"],
        theme["line_height"]["subheading"],
    )
    apply_paragraph_style(
        doc.styles["Heading 3"],
        theme,
        theme["section"],
        theme["spacing"]["section"],
        theme["line_height"]["section"],
    )
    apply_paragraph_style(
        doc.styles["Title"],
        theme,
        theme["heading"],
        theme["spacing"]["heading"],
        theme["line_height"]["heading"],
    )
    apply_paragraph_style(
        doc.styles["Subtitle"],
        theme,
        theme["subheading"],
        theme["spacing"]["subheading"],
        theme["line_height"]["subheading"],
    )
    apply_paragraph_style(
        doc.styles["List Bullet"],
        theme,
        theme["normal"],
        theme["spacing"]["normal"],
        theme["line_height"]["normal"],
    )

    add_custom_styles(doc, theme)

    doc.save(output_path)


def build_all_templates() -> None:
    """Build templates for all themes."""
    for theme in THEMES:
        build_template(theme, TEMPLATES_DIR / f"{theme}.docx")


if __name__ == "__main__":
    build_all_templates()
