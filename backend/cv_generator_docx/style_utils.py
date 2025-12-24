"""DOCX style helpers."""

from typing import Any, Dict, Tuple

from docx.shared import Pt, RGBColor


def apply_paragraph_style(
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


def apply_character_style(style, theme: Dict[str, Any], text_def: Dict[str, Any]) -> None:
    font = style.font
    font.name = theme["fontfamily"]
    font.size = Pt(_parse_pt(text_def.get("fontsize", "11pt")))
    font.bold = text_def.get("fontweight") == "bold"
    color = text_def.get("color")
    if color:
        font.color.rgb = RGBColor.from_string(color.lstrip("#"))


def _parse_pt(value: str) -> float:
    return float(value.replace("pt", "").strip())


def _cm_to_pt(value: str) -> float:
    return float(value.replace("cm", "").strip()) * 28.3465
