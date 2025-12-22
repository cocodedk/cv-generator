"""Document styling utilities for CV generation."""
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import P


class CVStyles:
    """Predefined styles for professional CVs."""

    @staticmethod
    def create_styles(doc: OpenDocumentText):
        """Create all CV styles in the document."""

        # Heading style
        heading_style = Style(name="Heading", family="paragraph")
        heading_style.addElement(TextProperties(
            fontsize="18pt",
            fontweight="bold",
            color="#2c3e50"
        ))
        heading_style.addElement(ParagraphProperties(
            margintop="0.5cm",
            marginbottom="0.3cm"
        ))
        doc.styles.addElement(heading_style)

        # Subheading style
        subheading_style = Style(name="Subheading", family="paragraph")
        subheading_style.addElement(TextProperties(
            fontsize="14pt",
            fontweight="bold",
            color="#34495e"
        ))
        subheading_style.addElement(ParagraphProperties(
            margintop="0.4cm",
            marginbottom="0.2cm"
        ))
        doc.styles.addElement(subheading_style)

        # Section title style
        section_style = Style(name="SectionTitle", family="paragraph")
        section_style.addElement(TextProperties(
            fontsize="12pt",
            fontweight="bold",
            color="#34495e"
        ))
        section_style.addElement(ParagraphProperties(
            margintop="0.3cm",
            marginbottom="0.15cm"
        ))
        doc.styles.addElement(section_style)

        # Normal text style
        normal_style = Style(name="Normal", family="paragraph")
        normal_style.addElement(TextProperties(
            fontsize="11pt",
            color="#2c3e50"
        ))
        normal_style.addElement(ParagraphProperties(
            marginbottom="0.1cm"
        ))
        doc.styles.addElement(normal_style)

        # Emphasis style
        emphasis_style = Style(name="Emphasis", family="text")
        emphasis_style.addElement(TextProperties(
            fontweight="bold"
        ))
        doc.styles.addElement(emphasis_style)

        return doc
