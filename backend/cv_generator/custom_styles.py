"""Custom DOCX styles used by Pandoc HTML rendering."""

from typing import Any, Dict

from docx.document import Document as DocxDocument
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from backend.cv_generator.style_utils import apply_character_style, apply_paragraph_style


def _add_no_border_table_style(doc: DocxDocument, name: str) -> None:
    style = doc.styles.add_style(name, WD_STYLE_TYPE.TABLE)
    style_el = style._element  # python-docx internal XML element
    tbl_pr = style_el.find(qn("w:tblPr"))
    if tbl_pr is None:
        tbl_pr = OxmlElement("w:tblPr")
        style_el.append(tbl_pr)

    tbl_borders = tbl_pr.find(qn("w:tblBorders"))
    if tbl_borders is None:
        tbl_borders = OxmlElement("w:tblBorders")
        tbl_pr.append(tbl_borders)
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        element = tbl_borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            tbl_borders.append(element)
        element.set(qn("w:val"), "nil")


def add_custom_styles(doc: DocxDocument, theme: Dict[str, Any]) -> None:
    _add_no_border_table_style(doc, "CV Table")

    contact_info_style = doc.styles.add_style("Contact Info", 1)  # 1 = paragraph style
    apply_paragraph_style(
        contact_info_style,
        theme,
        {"fontsize": "9pt", "color": theme["normal"].get("color")},
        theme["spacing"]["normal"],
        theme["line_height"]["normal"],
    )

    skill_category_style = doc.styles.add_style("Skill Category", 1)
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

    skill_items_style = doc.styles.add_style("Skill Items", 1)
    apply_paragraph_style(
        skill_items_style,
        theme,
        {"fontsize": "10pt", "color": theme["normal"].get("color")},
        ("0cm", "0cm"),
        "1.2",
    )

    skill_highlight_style = doc.styles.add_style("Skill Highlight", 2)  # 2 = character style
    apply_character_style(
        skill_highlight_style,
        theme,
        {
            "fontsize": "10pt",
            "fontweight": "bold",
            "color": theme.get("divider_color", theme.get("accent_color")),
        },
    )

    skill_level_style = doc.styles.add_style("Skill Level", 2)
    apply_character_style(
        skill_level_style,
        theme,
        {"fontsize": "10pt", "color": theme.get("text_secondary")},
    )

    exp_role_style = doc.styles.add_style("Exp Role", 1)
    apply_paragraph_style(
        exp_role_style,
        theme,
        {"fontsize": "11pt", "fontweight": "bold", "color": theme["normal"].get("color")},
        ("0cm", "0cm"),
        "1.15",
    )

    exp_company_style = doc.styles.add_style("Exp Company", 1)
    apply_paragraph_style(
        exp_company_style,
        theme,
        {
            "fontsize": "11pt",
            "fontweight": "bold",
            "color": theme.get("divider_color", theme.get("accent_color")),
        },
        ("0cm", "0cm"),
        "1.15",
    )

    exp_meta_style = doc.styles.add_style("Exp Meta", 1)
    apply_paragraph_style(
        exp_meta_style,
        theme,
        {"fontsize": "9pt", "color": theme.get("text_secondary")},
        ("0cm", "0cm"),
        "1.15",
    )

    exp_body_style = doc.styles.add_style("Exp Body", 1)
    apply_paragraph_style(
        exp_body_style,
        theme,
        {"fontsize": "10pt", "color": theme["normal"].get("color")},
        ("0cm", "0.1cm"),
        "1.25",
    )

    exp_highlight_style = doc.styles.add_style("Exp Highlight", 2)
    apply_character_style(
        exp_highlight_style,
        theme,
        {"fontsize": "10pt", "fontweight": "bold", "color": theme["normal"].get("color")},
    )
