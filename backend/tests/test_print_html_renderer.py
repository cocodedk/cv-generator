"""Tests for A4 print HTML rendering."""

from backend.cv_generator_docx.print_html_renderer import render_print_html


def test_render_print_html_contains_a4_css(sample_cv_data):
    html = render_print_html(sample_cv_data)
    assert "@page{size:A4" in html
    assert "A4 preview" in html
    assert sample_cv_data["personal_info"]["name"] in html
    assert sample_cv_data["experience"][0]["projects"][0]["name"] in html
