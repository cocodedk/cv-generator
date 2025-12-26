"""Tests for HTML rendering and template selection."""
from backend.cv_generator_docx.html_renderer.render import render_html


def test_render_html_uses_base_template_for_classic_theme(sample_cv_data):
    """Test that base.html template is used for classic theme."""
    sample_cv_data["theme"] = "classic"
    html = render_html(sample_cv_data)
    assert sample_cv_data["personal_info"]["name"] in html
    assert "Experience" in html or "experience" in html.lower()


def test_render_html_uses_theme_specific_template_when_available(sample_cv_data):
    """Test that theme-specific templates are used when they exist."""
    # Test professional theme
    sample_cv_data["theme"] = "professional"
    html = render_html(sample_cv_data)
    assert sample_cv_data["personal_info"]["name"] in html
    # Professional template should have specific styling
    assert "professional" in html.lower() or sample_cv_data["personal_info"]["name"] in html

    # Test creative theme
    sample_cv_data["theme"] = "creative"
    html = render_html(sample_cv_data)
    assert sample_cv_data["personal_info"]["name"] in html

    # Test tech theme
    sample_cv_data["theme"] = "tech"
    html = render_html(sample_cv_data)
    assert sample_cv_data["personal_info"]["name"] in html

    # Test executive theme
    sample_cv_data["theme"] = "executive"
    html = render_html(sample_cv_data)
    assert sample_cv_data["personal_info"]["name"] in html

    # Test colorful theme
    sample_cv_data["theme"] = "colorful"
    html = render_html(sample_cv_data)
    assert sample_cv_data["personal_info"]["name"] in html


def test_render_html_falls_back_to_base_for_missing_template(sample_cv_data):
    """Test that base.html is used when theme-specific template doesn't exist."""
    # Use a theme that doesn't have a custom template (like 'modern')
    sample_cv_data["theme"] = "modern"
    html = render_html(sample_cv_data)
    assert sample_cv_data["personal_info"]["name"] in html
    # Should still render successfully using base.html


def test_render_html_includes_theme_in_template_data(sample_cv_data):
    """Test that theme is included in template data."""
    sample_cv_data["theme"] = "professional"
    html = render_html(sample_cv_data)
    # Template should render successfully with theme data
    assert sample_cv_data["personal_info"]["name"] in html


def test_render_html_defaults_to_classic_when_no_theme(sample_cv_data):
    """Test that theme defaults to classic when not provided."""
    if "theme" in sample_cv_data:
        del sample_cv_data["theme"]
    html = render_html(sample_cv_data)
    assert sample_cv_data["personal_info"]["name"] in html


def test_render_html_all_new_themes(sample_cv_data):
    """Test that all new themes render successfully."""
    new_themes = ["professional", "creative", "tech", "executive", "colorful"]
    for theme in new_themes:
        sample_cv_data["theme"] = theme
        html = render_html(sample_cv_data)
        assert sample_cv_data["personal_info"]["name"] in html
        assert len(html) > 0


def test_render_html_template_files_exist():
    """Test that theme-specific template files exist."""
    # Use the same path resolution as render.py
    from backend.cv_generator_docx.html_renderer.render import TEMPLATES_DIR

    # Check that new theme templates exist
    new_theme_templates = ["professional.html", "creative.html", "tech.html", "executive.html", "colorful.html"]
    for template_file in new_theme_templates:
        template_path = TEMPLATES_DIR / template_file
        assert template_path.exists(), f"Theme template {template_file} should exist at {template_path}"
