"""Tests for browser-printable HTML endpoints."""

from unittest.mock import patch
import pytest


@pytest.mark.asyncio
@pytest.mark.api
class TestPrintHtmlRoutes:
    async def test_render_print_html_from_payload(self, client, sample_cv_data):
        response = await client.post("/api/render-print-html", json=sample_cv_data)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "A4 preview" in response.text

    async def test_render_print_html_for_cv(self, client):
        cv_data = {
            "cv_id": "cv-id",
            "personal_info": {"name": "Jane Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "classic",
        }
        with patch("backend.database.queries.get_cv_by_id", return_value=cv_data):
            response = await client.get("/api/cv/cv-id/print-html")
        assert response.status_code == 200
        assert "Jane Doe" in response.text
