"""DOCX template builder for themes."""
from pathlib import Path
from typing import Dict, Any, Tuple
from docx import Document
from docx.shared import Pt, RGBColor
from backend.themes import THEMES, validate_theme


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

    _apply_paragraph_style(
        doc.styles["Normal"],
        theme,
        theme["normal"],
        theme["spacing"]["normal"],
        theme["line_height"]["normal"],
    )
    _apply_paragraph_style(
        doc.styles["Heading 1"],
        theme,
        theme["heading"],
        theme["spacing"]["heading"],
        theme["line_height"]["heading"],
    )
    _apply_paragraph_style(
        doc.styles["Heading 2"],
        theme,
        theme["subheading"],
        theme["spacing"]["subheading"],
        theme["line_height"]["subheading"],
    )
    _apply_paragraph_style(
        doc.styles["Heading 3"],
        theme,
        theme["section"],
        theme["spacing"]["section"],
        theme["line_height"]["section"],
    )
    _apply_paragraph_style(
        doc.styles["Title"],
        theme,
        theme["heading"],
        theme["spacing"]["heading"],
        theme["line_height"]["heading"],
    )
    _apply_paragraph_style(
        doc.styles["Subtitle"],
        theme,
        theme["subheading"],
        theme["spacing"]["subheading"],
        theme["line_height"]["subheading"],
    )
    _apply_paragraph_style(
        doc.styles["List Bullet"],
        theme,
        theme["normal"],
        theme["spacing"]["normal"],
        theme["line_height"]["normal"],
    )

    doc.save(output_path)


def build_all_templates() -> None:
    """Build templates for all themes."""
    for theme in THEMES:
        build_template(theme, TEMPLATES_DIR / f"{theme}.docx")


def _apply_paragraph_style(
    style,
    theme: Dict[str, Any],
    text_def: Dict[str, Any],
    spacing: Tuple[str, str],
    line_height: str,
) -> None:
    font = style.font
    font.name = theme["fontfamily"]
    font.size = Pt(_parse_pt(text_def.get("fontsize", "11pt")))
    font.bold = text_def.get("fontweight") == "bold"
    color = text_def.get("color")
    if color:
        font.color.rgb = RGBColor.from_string(color.lstrip("#"))

    paragraph = style.paragraph_format
    paragraph.space_before = Pt(_cm_to_pt(spacing[0]))
    paragraph.space_after = Pt(_cm_to_pt(spacing[1]))
    paragraph.line_spacing = float(line_height)


def _parse_pt(value: str) -> float:
    return float(value.replace("pt", "").strip())


def _cm_to_pt(value: str) -> float:
    return float(value.replace("cm", "").strip()) * 28.3465


if __name__ == "__main__":
    build_all_templates()
