"""Tests for A4 print HTML rendering."""

from backend.cv_generator_docx.print_html_renderer import render_print_html


def test_render_print_html_contains_a4_css(sample_cv_data):
    html = render_print_html(sample_cv_data)
    assert "@page{size:A4" in html
    assert "A4 preview" in html
    assert sample_cv_data["personal_info"]["name"] in html
    assert sample_cv_data["experience"][0]["projects"][0]["name"] in html


def test_render_print_html_professional_theme_has_css(sample_cv_data):
    """Test that professional theme generates HTML with CSS styling."""
    sample_cv_data["theme"] = "professional"
    html = render_print_html(sample_cv_data)

    # Should contain CSS styling
    assert "<style>" in html
    assert "@page{size:A4" in html

    # Should contain professional theme colors in CSS variables
    # accent_color: #3b82f6, section color: #1e40af, text: #1e293b, muted: #475569
    assert "--accent:#3b82f6" in html or "--accent: #3b82f6" in html
    assert "--accent-2:#1e40af" in html or "--accent-2: #1e40af" in html
    assert "--ink:#1e293b" in html or "--ink: #1e293b" in html
    assert "--muted:#475569" in html or "--muted: #475569" in html

    # Should contain content
    assert sample_cv_data["personal_info"]["name"] in html
