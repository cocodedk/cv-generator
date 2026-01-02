"""Tests for A4 print HTML rendering."""

from backend.cv_generator.print_html_renderer import render_print_html


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


def test_render_print_html_no_scrambling_when_config_none(sample_cv_data):
    """Test that render_print_html works without scrambling when config is None."""
    html = render_print_html(sample_cv_data, scramble_config=None)
    # Original personal info should be present
    assert sample_cv_data["personal_info"]["name"] in html
    assert sample_cv_data["personal_info"]["email"] in html
    # Should not contain unlock script
    assert "unlockWithKey" not in html


def test_render_print_html_scrambling_enabled(sample_cv_data):
    """Test that render_print_html scrambles when config is enabled."""
    scramble_key = "test-key-123"
    html = render_print_html(
        sample_cv_data, scramble_config={"enabled": True, "key": scramble_key}
    )
    # Original personal info should NOT be present
    assert sample_cv_data["personal_info"]["name"] not in html
    assert sample_cv_data["personal_info"]["email"] not in html
    # Should contain unlock script
    assert "unlockWithKey" in html
    assert "</body>" in html


def test_render_print_html_scrambled_contains_unlock_script(sample_cv_data):
    """Test that scrambled HTML contains unlock script."""
    scramble_key = "test-key-123"
    html = render_print_html(
        sample_cv_data, scramble_config={"enabled": True, "key": scramble_key}
    )
    # Should contain the scramble script
    assert "unlockWithKey" in html
    assert "createUnlockUi" in html
    assert "SELECTOR" in html
    assert 'data-scramble="1"' in html


def test_render_print_html_exempt_fields_not_scrambled(sample_cv_data):
    """Test that exempt fields (linkedin, github, website) are NOT scrambled."""
    scramble_key = "test-key-123"
    # Ensure exempt fields are in personal_info
    sample_cv_data["personal_info"]["linkedin"] = "https://linkedin.com/in/johndoe"
    sample_cv_data["personal_info"]["github"] = "https://github.com/johndoe"
    sample_cv_data["personal_info"]["website"] = "https://johndoe.com"

    html = render_print_html(
        sample_cv_data, scramble_config={"enabled": True, "key": scramble_key}
    )
    # Exempt fields should still be present (not scrambled)
    assert "linkedin.com/in/johndoe" in html
    assert "github.com/johndoe" in html
    assert "johndoe.com" in html


def test_render_print_html_non_personal_info_not_scrambled(sample_cv_data):
    """Test that non-personal-info sections are NOT scrambled."""
    scramble_key = "test-key-123"
    html = render_print_html(
        sample_cv_data, scramble_config={"enabled": True, "key": scramble_key}
    )
    # Experience content should still be present (not scrambled)
    assert sample_cv_data["experience"][0]["title"] in html
    assert sample_cv_data["experience"][0]["company"] in html
    # Education content should still be present
    assert sample_cv_data["education"][0]["degree"] in html
    assert sample_cv_data["education"][0]["institution"] in html
