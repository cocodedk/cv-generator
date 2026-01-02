"""Tests for CV layout rendering."""
import pytest
from backend.cv_generator.print_html_renderer import render_print_html
from backend.cv_generator.layouts import validate_layout, LAYOUTS


@pytest.fixture
def sample_cv_data():
    """Sample CV data for testing."""
    return {
        "personal_info": {
            "name": "John Doe",
            "title": "Software Engineer",
            "email": "john@example.com",
            "phone": "123-456-7890",
            "summary": "Experienced software engineer with expertise in Python.",
        },
        "experience": [
            {
                "title": "Senior Developer",
                "company": "Tech Corp",
                "start_date": "2020-01",
                "end_date": "Present",
                "description": "Led development team",
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "University",
                "year": "2018",
            }
        ],
        "skills": [
            {"name": "Python", "category": "Programming"},
            {"name": "JavaScript", "category": "Programming"},
            {"name": "Docker", "category": "DevOps"},
        ],
        "theme": "classic",
        "layout": "classic-two-column",
    }


def test_validate_layout_valid():
    """Test layout validation with valid layout."""
    assert validate_layout("classic-two-column") == "classic-two-column"
    assert validate_layout("ats-single-column") == "ats-single-column"


def test_validate_layout_invalid():
    """Test layout validation with invalid layout defaults to classic-two-column."""
    assert validate_layout("invalid-layout") == "classic-two-column"


def test_render_with_layout(sample_cv_data):
    """Test rendering CV with specific layout."""
    sample_cv_data["layout"] = "classic-two-column"
    html = render_print_html(sample_cv_data)
    assert html is not None
    assert len(html) > 0
    assert "John Doe" in html


def test_render_all_layouts(sample_cv_data):
    """Test that all layouts can be rendered."""
    for layout_name in LAYOUTS.keys():
        sample_cv_data["layout"] = layout_name
        html = render_print_html(sample_cv_data)
        assert html is not None
        assert len(html) > 0
        assert "John Doe" in html


def test_render_with_theme_and_layout(sample_cv_data):
    """Test rendering with different theme and layout combinations."""
    themes = ["classic", "modern", "tech"]
    layouts = ["classic-two-column", "ats-single-column", "modern-sidebar"]

    for theme in themes:
        for layout in layouts:
            sample_cv_data["theme"] = theme
            sample_cv_data["layout"] = layout
            html = render_print_html(sample_cv_data)
            assert html is not None
            assert len(html) > 0


def test_render_missing_layout_defaults(sample_cv_data):
    """Test that missing layout defaults to classic-two-column."""
    del sample_cv_data["layout"]
    html = render_print_html(sample_cv_data)
    assert html is not None
    assert len(html) > 0


def test_render_empty_sections(sample_cv_data):
    """Test rendering with empty optional sections."""
    sample_cv_data["experience"] = []
    sample_cv_data["education"] = []
    sample_cv_data["skills"] = []
    sample_cv_data["layout"] = "classic-two-column"

    html = render_print_html(sample_cv_data)
    assert html is not None
    assert "John Doe" in html


# =============================================================================
# Layout-Specific Structure Tests
# =============================================================================


@pytest.mark.parametrize(
    "layout,expected_element",
    [
        ("classic-two-column", "grid-template-columns"),
        ("ats-single-column", "max-width: 750px"),
        ("modern-sidebar", "sticky"),
        ("career-timeline", "timeline"),
        ("section-cards-grid", "cards-grid"),
        ("project-case-studies", "case-study"),
        ("portfolio-spa", '<nav>'),
        ("interactive-skills-matrix", "skills-matrix"),
        ("academic-cv", "publication"),
        ("dark-mode-tech", "prefers-color-scheme: dark"),
    ],
)
def test_layout_has_specific_structure(sample_cv_data, layout, expected_element):
    """Test that each layout produces HTML with its distinctive structure."""
    sample_cv_data["layout"] = layout
    html = render_print_html(sample_cv_data)
    assert expected_element in html, (
        f"Layout '{layout}' should contain '{expected_element}'"
    )


def test_layout_change_produces_different_output(sample_cv_data):
    """Test that changing layout produces different HTML output."""
    sample_cv_data["layout"] = "classic-two-column"
    html_classic = render_print_html(sample_cv_data)

    sample_cv_data["layout"] = "career-timeline"
    html_timeline = render_print_html(sample_cv_data)

    # Both should contain the name
    assert "John Doe" in html_classic
    assert "John Doe" in html_timeline

    # But the HTML structure should be different
    assert html_classic != html_timeline
    assert "timeline" in html_timeline
    assert "timeline" not in html_classic


def test_theme_css_is_injected(sample_cv_data):
    """Test that theme CSS variables are injected into rendered HTML."""
    sample_cv_data["theme"] = "professional"
    sample_cv_data["layout"] = "classic-two-column"
    html = render_print_html(sample_cv_data)

    # Should contain CSS variable overrides
    assert "--accent:" in html
    assert "--ink:" in html or "--muted:" in html


@pytest.mark.parametrize("layout", list(LAYOUTS.keys()))
def test_all_layouts_handle_empty_sections(sample_cv_data, layout):
    """Test that all layouts gracefully handle empty sections."""
    sample_cv_data["layout"] = layout
    sample_cv_data["experience"] = []
    sample_cv_data["education"] = []
    sample_cv_data["skills"] = []

    html = render_print_html(sample_cv_data)
    assert html is not None
    assert len(html) > 0
    assert "John Doe" in html


def test_interactive_skills_matrix_has_javascript(sample_cv_data):
    """Test that interactive-skills-matrix layout includes JavaScript."""
    sample_cv_data["layout"] = "interactive-skills-matrix"
    html = render_print_html(sample_cv_data)

    assert "<script>" in html
    assert "filterSkills" in html
    assert "event" in html  # Verify event parameter is used


def test_interactive_skills_matrix_filter_buttons(sample_cv_data):
    """Test that interactive-skills-matrix has filter buttons for categories."""
    sample_cv_data["layout"] = "interactive-skills-matrix"
    html = render_print_html(sample_cv_data)

    assert "filter-btn" in html
    assert "onclick" in html
    # Should have buttons for each category
    assert "Programming" in html
    assert "DevOps" in html


def test_academic_cv_has_research_section(sample_cv_data):
    """Test that academic-cv layout has research interests section."""
    sample_cv_data["layout"] = "academic-cv"
    html = render_print_html(sample_cv_data)

    assert 'id="research"' in html
    assert "Research Interests" in html


def test_academic_cv_skills_in_correct_categories(sample_cv_data):
    """Test that skills appear under their correct category headings in academic-cv layout."""
    # Use skills with specific categories that should be clearly separated
    sample_cv_data["skills"] = [
        {"name": "React", "category": "Frontend"},
        {"name": "Python", "category": "Programming"},
    ]
    sample_cv_data["layout"] = "academic-cv"
    html = render_print_html(sample_cv_data)

    # Find the skills section specifically (between <section id="skills"> and </section>)
    skills_section_start = html.find('<section id="skills">')
    assert skills_section_start != -1, "Skills section should be present"

    # Find the end of the skills section (next </section> after skills section start)
    skills_section_end = html.find("</section>", skills_section_start)
    assert skills_section_end != -1, "Skills section should have closing tag"

    # Extract only the skills section HTML
    skills_section = html[skills_section_start:skills_section_end]

    # Find positions within the skills section only
    frontend_idx = skills_section.find("Frontend")
    programming_idx = skills_section.find("Programming")
    react_idx = skills_section.find("React")
    python_idx = skills_section.find("Python")

    # Both categories and skills should be present in the skills section
    assert frontend_idx != -1, "Frontend category should be present in skills section"
    assert programming_idx != -1, "Programming category should be present in skills section"
    assert react_idx != -1, "React skill should be present in skills section"
    assert python_idx != -1, "Python skill should be present in skills section"

    # React should appear after Frontend heading and before Programming heading
    assert react_idx > frontend_idx, "React should appear after Frontend category"
    assert react_idx < programming_idx, "React should appear before Programming category"

    # Python should appear after Programming heading
    assert python_idx > programming_idx, "Python should appear after Programming category"

    # Verify React is in the Frontend section (between Frontend and Programming headings)
    section_between = skills_section[frontend_idx:programming_idx]
    assert "React" in section_between, "React should be in the Frontend section"
    assert "Python" not in section_between, "Python should not be in the Frontend section"

    # Verify Python is in the Programming section (after Programming heading)
    section_after_programming = skills_section[programming_idx:]
    assert "Python" in section_after_programming, "Python should be in the Programming section"
    assert "React" not in section_after_programming, "React should not be in the Programming section"


def test_portfolio_spa_has_navigation(sample_cv_data):
    """Test that portfolio-spa layout has navigation links."""
    sample_cv_data["layout"] = "portfolio-spa"
    html = render_print_html(sample_cv_data)

    assert "<nav>" in html
    assert 'href="#home"' in html
    assert 'href="#experience"' in html
    assert 'href="#education"' in html


def test_dark_mode_tech_has_dark_theme_support(sample_cv_data):
    """Test that dark-mode-tech layout supports dark mode."""
    sample_cv_data["layout"] = "dark-mode-tech"
    html = render_print_html(sample_cv_data)

    assert "prefers-color-scheme: dark" in html
    assert "monospace" in html  # Code-like typography


def test_career_timeline_has_timeline_structure(sample_cv_data):
    """Test that career-timeline layout has proper timeline structure."""
    sample_cv_data["layout"] = "career-timeline"
    html = render_print_html(sample_cv_data)

    assert "timeline" in html
    assert "timeline-item" in html


def test_modern_sidebar_has_sticky_sidebar(sample_cv_data):
    """Test that modern-sidebar layout has sticky sidebar."""
    sample_cv_data["layout"] = "modern-sidebar"
    html = render_print_html(sample_cv_data)

    assert "sticky" in html
    assert "<aside>" in html
