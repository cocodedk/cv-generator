"""Tests for Content Adapter (Step 4)."""

import pytest
from backend.models import Experience, Project
from backend.services.ai.pipeline.models import JDAnalysis, SelectionResult
from backend.services.ai.pipeline.content_adapter import adapt_content


class TestContentAdapter:
    @pytest.mark.asyncio
    async def test_adapt_content_preserves_facts(self):
        """Verify that content adapter preserves all facts from profile."""
        selection_result = SelectionResult(
            experiences=[
                Experience(
                    title="Software Engineer",
                    company="Test Corp",
                    start_date="2023-01",
                    projects=[
                        Project(
                            name="API Project",
                            highlights=["Built REST API using Python"],
                            technologies=["Python"],
                        )
                    ],
                )
            ],
            selected_indices={},
        )

        jd_analysis = JDAnalysis(
            required_skills={"python", "api"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        result = await adapt_content(selection_result, jd_analysis)

        # Should preserve core facts
        assert len(result.experiences) == 1
        assert result.experiences[0].title == "Software Engineer"
        assert result.experiences[0].company == "Test Corp"
        assert len(result.experiences[0].projects) == 1
        assert "Python" in result.experiences[0].projects[0].technologies
