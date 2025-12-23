"""Tests for CVStyles class."""
from odf.opendocument import OpenDocumentText
from backend.cv_generator.styles import CVStyles


class TestCVStyles:
    """Test CVStyles class."""

    def _get_style_names(self, doc):
        """Helper to get style names from document."""
        return [
            s.getAttribute("name")
            for s in doc.styles.childNodes
            if s.getAttribute("name")
        ]

    def test_create_styles_classic_theme(self):
        """Test style creation with classic theme."""
        doc = OpenDocumentText()
        result = CVStyles.create_styles(doc, theme="classic")

        assert result is doc
        style_names = self._get_style_names(doc)
        assert "Heading" in style_names
        assert "Subheading" in style_names
        assert "Normal" in style_names

    def test_create_styles_modern_theme(self):
        """Test style creation with modern theme."""
        doc = OpenDocumentText()
        result = CVStyles.create_styles(doc, theme="modern")

        assert result is doc
        style_names = self._get_style_names(doc)
        assert "Heading" in style_names

    def test_create_styles_minimal_theme(self):
        """Test style creation with minimal theme."""
        doc = OpenDocumentText()
        result = CVStyles.create_styles(doc, theme="minimal")

        assert result is doc
        style_names = self._get_style_names(doc)
        assert "Heading" in style_names

    def test_create_styles_elegant_theme(self):
        """Test style creation with elegant theme."""
        doc = OpenDocumentText()
        result = CVStyles.create_styles(doc, theme="elegant")

        assert result is doc
        style_names = self._get_style_names(doc)
        assert "Heading" in style_names

    def test_create_styles_accented_theme(self):
        """Test style creation with accented theme."""
        doc = OpenDocumentText()
        result = CVStyles.create_styles(doc, theme="accented")

        assert result is doc
        style_names = self._get_style_names(doc)
        assert "Heading" in style_names
        assert "TopBar" in style_names
        assert "HeaderName" in style_names

    def test_create_styles_invalid_theme_defaults_to_classic(self):
        """Test that invalid theme defaults to classic."""
        doc = OpenDocumentText()
        result = CVStyles.create_styles(doc, theme="invalid_theme")

        assert result is doc
        style_names = self._get_style_names(doc)
        assert "Heading" in style_names

    def test_create_styles_all_required_styles_present(self):
        """Test that all required styles are created."""
        doc = OpenDocumentText()
        CVStyles.create_styles(doc, theme="classic")

        style_names = self._get_style_names(doc)
        required_styles = [
            "Heading",
            "Subheading",
            "SectionTitle",
            "Normal",
            "Emphasis",
        ]

        for style_name in required_styles:
            assert style_name in style_names

    def test_create_styles_accented_specific_styles(self):
        """Test accented theme creates specific styles."""
        doc = OpenDocumentText()
        CVStyles.create_styles(doc, theme="accented")

        style_names = self._get_style_names(doc)
        accented_styles = [
            "TopBar",
            "HeaderName",
            "HeaderTitle",
            "BulletText",
            "BodyTable",
            "PhotoText",
        ]

        for style_name in accented_styles:
            assert style_name in style_names
