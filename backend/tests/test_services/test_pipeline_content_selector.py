"""Tests for Content Selector (Step 3)."""

from backend.models import Experience, Project
from backend.services.ai.pipeline.models import JDAnalysis, SkillMapping
from backend.services.ai.pipeline.content_selector import select_content


class TestContentSelector:
    def test_select_content_only_selects_from_profile(self):
        """Verify that content selector only selects from profile, never creates new."""
        profile_experiences = [
            Experience(
                title="Software Engineer",
                company="Test Corp",
                start_date="2023-01",
                end_date=None,
                projects=[
                    Project(
                        name="Project A",
                        highlights=["Built API"],
                        technologies=["Python"],
                    )
                ],
            )
        ]

        jd_analysis = JDAnalysis(
            required_skills={"python"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        skill_mapping = SkillMapping(
            matched_skills=[],
            selected_skills=[],
            coverage_gaps=[],
        )

        result = select_content(profile_experiences, jd_analysis, skill_mapping, max_experiences=1)

        # Should select from profile
        assert len(result.experiences) <= len(profile_experiences)
        if result.experiences:
            # Selected experience should be from profile
            assert result.experiences[0].company == "Test Corp"
            assert result.experiences[0].title == "Software Engineer"
