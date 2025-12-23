"""Document styling utilities for CV generation."""
from odf.opendocument import OpenDocumentText
from odf.style import (
    Style,
    TextProperties,
    ParagraphProperties,
    TableCellProperties,
    TableColumnProperties,
    TableProperties,
    GraphicProperties,
)


class CVStyles:
    """Predefined styles for professional CVs."""

    THEMES = {
        "classic": {
            "fontfamily": "Liberation Serif",
            "heading": {"fontsize": "18pt", "fontweight": "bold", "color": "#2c3e50"},
            "subheading": {
                "fontsize": "14pt",
                "fontweight": "bold",
                "color": "#34495e",
            },
            "section": {"fontsize": "12pt", "fontweight": "bold", "color": "#34495e"},
            "normal": {"fontsize": "11pt", "color": "#2c3e50"},
            "spacing": {
                "heading": ("0.5cm", "0.3cm"),
                "subheading": ("0.4cm", "0.2cm"),
                "section": ("0.3cm", "0.15cm"),
                "normal": ("0cm", "0.1cm"),
            },
        },
        "modern": {
            "fontfamily": "Liberation Sans",
            "heading": {"fontsize": "19pt", "fontweight": "bold", "color": "#1b3a57"},
            "subheading": {
                "fontsize": "13pt",
                "fontweight": "bold",
                "color": "#1f4c6b",
            },
            "section": {"fontsize": "11.5pt", "fontweight": "bold", "color": "#1f4c6b"},
            "normal": {"fontsize": "10.5pt", "color": "#23313f"},
            "spacing": {
                "heading": ("0.45cm", "0.25cm"),
                "subheading": ("0.35cm", "0.18cm"),
                "section": ("0.25cm", "0.12cm"),
                "normal": ("0cm", "0.12cm"),
            },
        },
        "minimal": {
            "fontfamily": "Liberation Sans",
            "heading": {"fontsize": "17pt", "fontweight": "bold", "color": "#111111"},
            "subheading": {
                "fontsize": "12.5pt",
                "fontweight": "bold",
                "color": "#222222",
            },
            "section": {"fontsize": "11pt", "fontweight": "bold", "color": "#222222"},
            "normal": {"fontsize": "10.5pt", "color": "#222222"},
            "spacing": {
                "heading": ("0.35cm", "0.2cm"),
                "subheading": ("0.25cm", "0.15cm"),
                "section": ("0.2cm", "0.1cm"),
                "normal": ("0cm", "0.08cm"),
            },
        },
        "elegant": {
            "fontfamily": "Liberation Serif",
            "heading": {"fontsize": "19pt", "fontweight": "bold", "color": "#5a3e2b"},
            "subheading": {
                "fontsize": "14pt",
                "fontweight": "bold",
                "color": "#6b4a34",
            },
            "section": {"fontsize": "12pt", "fontweight": "bold", "color": "#6b4a34"},
            "normal": {"fontsize": "11pt", "color": "#3a2b23"},
            "spacing": {
                "heading": ("0.55cm", "0.28cm"),
                "subheading": ("0.4cm", "0.2cm"),
                "section": ("0.3cm", "0.14cm"),
                "normal": ("0cm", "0.1cm"),
            },
        },
        "accented": {
            "fontfamily": "Liberation Sans",
            "heading": {"fontsize": "18pt", "fontweight": "bold", "color": "#2c3e50"},
            "subheading": {
                "fontsize": "12.5pt",
                "fontweight": "bold",
                "color": "#2c3e50",
            },
            "section": {"fontsize": "11.5pt", "fontweight": "bold", "color": "#2c3e50"},
            "normal": {"fontsize": "10.5pt", "color": "#2f2f2f"},
            "accent": "#e67e22",
            "spacing": {
                "heading": ("0.4cm", "0.2cm"),
                "subheading": ("0.25cm", "0.15cm"),
                "section": ("0.2cm", "0.1cm"),
                "normal": ("0cm", "0.1cm"),
            },
        },
    }

    @staticmethod
    def create_styles(doc: OpenDocumentText, theme: str = "classic"):
        """Create all CV styles in the document."""
        theme_def = CVStyles.THEMES.get(theme, CVStyles.THEMES["classic"])
        fontfamily = theme_def["fontfamily"]
        spacing = theme_def["spacing"]

        # Heading style
        heading_style = Style(name="Heading", family="paragraph")
        heading_style.addElement(
            TextProperties(fontfamily=fontfamily, **theme_def["heading"])
        )
        heading_style.addElement(
            ParagraphProperties(
                margintop=spacing["heading"][0], marginbottom=spacing["heading"][1]
            )
        )
        doc.styles.addElement(heading_style)

        # Subheading style
        subheading_style = Style(name="Subheading", family="paragraph")
        subheading_style.addElement(
            TextProperties(fontfamily=fontfamily, **theme_def["subheading"])
        )
        subheading_style.addElement(
            ParagraphProperties(
                margintop=spacing["subheading"][0],
                marginbottom=spacing["subheading"][1],
            )
        )
        doc.styles.addElement(subheading_style)

        # Section title style
        section_style = Style(name="SectionTitle", family="paragraph")
        section_style.addElement(
            TextProperties(fontfamily=fontfamily, **theme_def["section"])
        )
        section_style.addElement(
            ParagraphProperties(
                margintop=spacing["section"][0], marginbottom=spacing["section"][1]
            )
        )
        doc.styles.addElement(section_style)

        # Normal text style
        normal_style = Style(name="Normal", family="paragraph")
        normal_style.addElement(
            TextProperties(fontfamily=fontfamily, **theme_def["normal"])
        )
        normal_style.addElement(
            ParagraphProperties(
                margintop=spacing["normal"][0], marginbottom=spacing["normal"][1]
            )
        )
        doc.styles.addElement(normal_style)

        # Emphasis style
        emphasis_style = Style(name="Emphasis", family="text")
        emphasis_style.addElement(
            TextProperties(fontfamily=fontfamily, fontweight="bold")
        )
        doc.styles.addElement(emphasis_style)

        accent = theme_def.get("accent", "#e67e22")

        # Accented layout helpers
        topbar_style = Style(name="TopBar", family="paragraph")
        topbar_style.addElement(
            TextProperties(fontfamily=fontfamily, fontsize="2pt", color=accent)
        )
        topbar_style.addElement(
            ParagraphProperties(backgroundcolor=accent, marginbottom="0.4cm")
        )
        doc.styles.addElement(topbar_style)

        header_name_style = Style(name="HeaderName", family="paragraph")
        header_name_style.addElement(
            TextProperties(
                fontfamily=fontfamily,
                fontsize="20pt",
                fontweight="bold",
                color=theme_def["heading"]["color"],
            )
        )
        header_name_style.addElement(ParagraphProperties(marginbottom="0.1cm"))
        doc.styles.addElement(header_name_style)

        header_title_style = Style(name="HeaderTitle", family="paragraph")
        header_title_style.addElement(
            TextProperties(
                fontfamily=fontfamily,
                fontsize="12.5pt",
                fontweight="bold",
                color=accent,
            )
        )
        header_title_style.addElement(ParagraphProperties(marginbottom="0.2cm"))
        doc.styles.addElement(header_title_style)

        bullet_style = Style(name="BulletText", family="paragraph")
        bullet_style.addElement(
            TextProperties(
                fontfamily=fontfamily,
                fontsize=theme_def["normal"]["fontsize"],
                color=theme_def["normal"]["color"],
            )
        )
        bullet_style.addElement(ParagraphProperties(marginbottom="0.1cm"))
        doc.styles.addElement(bullet_style)

        body_table_style = Style(name="BodyTable", family="table")
        body_table_style.addElement(TableProperties(align="left"))
        doc.styles.addElement(body_table_style)

        header_col_left = Style(name="HeaderColLeft", family="table-column")
        header_col_left.addElement(TableColumnProperties(columnwidth="14cm"))
        doc.styles.addElement(header_col_left)

        header_col_right = Style(name="HeaderColRight", family="table-column")
        header_col_right.addElement(TableColumnProperties(columnwidth="4cm"))
        doc.styles.addElement(header_col_right)

        main_col_style = Style(name="MainCol", family="table-column")
        main_col_style.addElement(TableColumnProperties(columnwidth="12.5cm"))
        doc.styles.addElement(main_col_style)

        side_col_style = Style(name="SideCol", family="table-column")
        side_col_style.addElement(TableColumnProperties(columnwidth="5.5cm"))
        doc.styles.addElement(side_col_style)

        main_cell_style = Style(name="MainCell", family="table-cell")
        main_cell_style.addElement(TableCellProperties(padding="0.2cm", border="none"))
        doc.styles.addElement(main_cell_style)

        header_cell_left = Style(name="HeaderCellLeft", family="table-cell")
        header_cell_left.addElement(TableCellProperties(padding="0.2cm", border="none"))
        doc.styles.addElement(header_cell_left)

        header_cell_right = Style(name="HeaderCellRight", family="table-cell")
        header_cell_right.addElement(
            TableCellProperties(padding="0.2cm", border="none")
        )
        doc.styles.addElement(header_cell_right)

        side_cell_style = Style(name="SideCell", family="table-cell")
        side_cell_style.addElement(
            TableCellProperties(
                padding="0.2cm", borderleft=f"0.04cm solid {accent}", border="none"
            )
        )
        doc.styles.addElement(side_cell_style)

        photo_frame_style = Style(name="PhotoFrame", family="graphic")
        photo_frame_style.addElement(
            GraphicProperties(
                stroke="solid", strokecolor="#c0c0c0", fillcolor="#f4f4f4"
            )
        )
        doc.styles.addElement(photo_frame_style)

        photo_text_style = Style(name="PhotoText", family="paragraph")
        photo_text_style.addElement(
            TextProperties(fontfamily=fontfamily, fontsize="10pt", color="#666666")
        )
        photo_text_style.addElement(
            ParagraphProperties(textalign="center", marginbottom="0cm")
        )
        doc.styles.addElement(photo_text_style)

        return doc
