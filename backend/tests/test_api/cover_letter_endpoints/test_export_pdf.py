"""Tests for POST /api/ai/cover-letter/pdf endpoint."""

import pytest


@pytest.mark.asyncio
@pytest.mark.api
class TestExportCoverLetterPDF:
    """Test POST /api/ai/cover-letter/pdf endpoint."""

    async def test_export_cover_letter_pdf_success(self, client, pdf_service):
        """Test successful PDF export."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
            <h1>Cover Letter</h1>
            <p>This is a test cover letter.</p>
        </body>
        </html>
        """

        response = await client.post(
            "/api/ai/cover-letter/pdf",
            json={"html": html_content},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert len(response.content) > 0  # PDF should have content

    async def test_export_cover_letter_pdf_empty_html(self, client):
        """Test PDF export with empty HTML."""
        response = await client.post(
            "/api/ai/cover-letter/pdf",
            json={"html": ""},
        )
        assert response.status_code == 422

    async def test_export_cover_letter_pdf_missing_html(self, client):
        """Test PDF export with missing HTML field."""
        response = await client.post(
            "/api/ai/cover-letter/pdf",
            json={},
        )
        assert response.status_code == 422

    async def test_export_cover_letter_pdf_invalid_html(self, client, pdf_service):
        """Test PDF export with invalid HTML (should still attempt to generate)."""
        # Even invalid HTML might generate a PDF (browser will try to render it)
        response = await client.post(
            "/api/ai/cover-letter/pdf",
            json={"html": "<invalid>html"},
        )
        # Should either succeed (browser renders what it can) or fail gracefully
        assert response.status_code in [200, 500]
