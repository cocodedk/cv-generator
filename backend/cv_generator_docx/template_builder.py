"""DOCX template builder for themes."""
from pathlib import Path
from typing import Any, Dict
from docx import Document
from backend.themes import THEMES, validate_theme
from backend.cv_generator_docx.style_utils import apply_character_style, apply_paragraph_style


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

    # Create custom "Contact Info" style (9pt font)
    contact_info_style = doc.styles.add_style("Contact Info", 1)  # 1 = paragraph style
    apply_paragraph_style(
        contact_info_style,
        theme,
        {"fontsize": "9pt", "color": theme["normal"].get("color")},
        theme["spacing"]["normal"],
        theme["line_height"]["normal"],
    )

    skill_category_style = doc.styles.add_style(
        "Skill Category", 1  # 1 = paragraph style
    )
    apply_paragraph_style(
        skill_category_style,
        theme,
        {
            "fontsize": "10pt",
            "fontweight": "bold",
            "color": theme.get("text_secondary", theme["normal"].get("color")),
        },
        ("0cm", "0cm"),
        "1.2",
    )

    skill_items_style = doc.styles.add_style("Skill Items", 1)  # 1 = paragraph style
    apply_paragraph_style(
        skill_items_style,
        theme,
        {"fontsize": "10pt", "color": theme["normal"].get("color")},
        ("0cm", "0cm"),
        "1.2",
    )

    skill_highlight_style = doc.styles.add_style(
        "Skill Highlight", 2  # 2 = character style
    )
    apply_character_style(
        skill_highlight_style,
        theme,
        {
            "fontsize": "10pt",
            "fontweight": "bold",
            "color": theme.get("divider_color", theme.get("accent_color")),
        },
    )

    skill_level_style = doc.styles.add_style("Skill Level", 2)  # 2 = character style
    apply_character_style(
        skill_level_style,
        theme,
        {"fontsize": "10pt", "color": theme.get("text_secondary")},
    )

    doc.save(output_path)


def build_all_templates() -> None:
    """Build templates for all themes."""
    for theme in THEMES:
        build_template(theme, TEMPLATES_DIR / f"{theme}.docx")

if __name__ == "__main__":
    build_all_templates()
