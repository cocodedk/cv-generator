"""Tests for PDF service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.pdf_service import PDFService, PADDING_BUFFER_PX


@pytest.fixture
def pdf_service():
    """Create PDF service instance for testing."""
    return PDFService(timeout=10)  # Shorter timeout for tests


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
            h1 { margin: 0 0 20px 0; }
            p { margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Test CV</h1>
        <p>This is a test CV content.</p>
    </body>
    </html>
    """


@pytest.fixture
def long_html():
    """Long HTML content for testing (> 5000px height)."""
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
            .section { margin: 50px 0; min-height: 500px; }
        </style>
    </head>
    <body>
    """
    # Add many sections to create long content
    for i in range(15):
        content += f'<div class="section"><h2>Section {i+1}</h2><p>Content for section {i+1}</p></div>'
    content += """
    </body>
    </html>
    """
    return content


@pytest.fixture
def html_with_images():
    """HTML with embedded base64 images."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; padding: 20px; }
            img { width: 200px; height: 200px; }
        </style>
    </head>
    <body>
        <h1>CV with Images</h1>
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" alt="Test">
    </body>
    </html>
    """


class TestGenerateLongPDF:
    """Test PDF generation functionality."""

    @pytest.mark.asyncio
    async def test_generate_long_pdf_short_content(self, pdf_service, sample_html):
        """Test PDF generation with short content."""
        pdf_bytes = await pdf_service.generate_long_pdf(sample_html)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")  # PDF magic bytes

    @pytest.mark.asyncio
    async def test_generate_long_pdf_long_content(self, pdf_service, long_html):
        """Test PDF generation with long content."""
        pdf_bytes = await pdf_service.generate_long_pdf(long_html)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_generate_long_pdf_with_images(self, pdf_service, html_with_images):
        """Test PDF generation with embedded images."""
        pdf_bytes = await pdf_service.generate_long_pdf(html_with_images)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_generate_long_pdf_empty_html(self, pdf_service):
        """Test PDF generation with empty HTML raises ValueError."""
        with pytest.raises(ValueError, match="HTML content cannot be empty"):
            await pdf_service.generate_long_pdf("")

        with pytest.raises(ValueError, match="HTML content cannot be empty"):
            await pdf_service.generate_long_pdf("   ")

    @pytest.mark.asyncio
    async def test_generate_long_pdf_timeout(self, pdf_service, sample_html):
        """Test PDF generation timeout handling."""
        # Create service with very short timeout
        short_timeout_service = PDFService(timeout=1)  # 1 second

        # Mock page.wait_for_load_state to raise timeout
        with patch("backend.services.pdf_service.async_playwright") as mock_playwright:
            mock_p = MagicMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            # Make wait_for_load_state raise timeout error
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError

            async def timeout_wait(*args, **kwargs):
                raise PlaywrightTimeoutError("Timeout")

            mock_page.wait_for_load_state = timeout_wait
            mock_page.set_content = AsyncMock()
            mock_page.evaluate = AsyncMock(return_value=1000)

            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
            mock_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(RuntimeError, match="timed out"):
                await short_timeout_service.generate_long_pdf(sample_html)

    @pytest.mark.asyncio
    async def test_generate_long_pdf_browser_cleanup(self, pdf_service, sample_html):
        """Test that browser instances are properly closed."""
        with patch("backend.services.pdf_service.async_playwright") as mock_playwright:
            mock_p = MagicMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_page.set_content = AsyncMock()
            mock_page.evaluate = AsyncMock(return_value=1000)
            mock_page.pdf = AsyncMock(return_value=b"PDF bytes")

            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
            mock_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            await pdf_service.generate_long_pdf(sample_html)

            # Verify browser was closed
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_long_pdf_playwright_error(self, pdf_service, sample_html):
        """Test handling of Playwright errors."""
        with patch("backend.services.pdf_service.async_playwright") as mock_playwright:
            # Make async_playwright() raise an exception when called
            # This happens before the try/except block, so it's not wrapped
            mock_playwright.side_effect = Exception("Playwright error")

            # The exception is raised directly, not wrapped, since it happens
            # when calling async_playwright() before entering the try/except block
            with pytest.raises(Exception, match="Playwright error"):
                await pdf_service.generate_long_pdf(sample_html)

    @pytest.mark.asyncio
    async def test_generate_long_pdf_height_calculation(self, pdf_service, sample_html):
        """Test that height is calculated correctly."""
        with patch("backend.services.pdf_service.async_playwright") as mock_playwright:
            mock_p = MagicMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            test_height_px = 2000
            expected_height_mm = ((test_height_px + PADDING_BUFFER_PX) / 96) * 25.4

            mock_page.set_content = AsyncMock()
            mock_page.evaluate = AsyncMock(return_value=test_height_px)
            mock_page.pdf = AsyncMock(return_value=b"PDF bytes")

            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_browser.close = AsyncMock()

            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
            mock_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            await pdf_service.generate_long_pdf(sample_html)

            # Verify PDF was called with correct height
            pdf_call = mock_page.pdf.call_args
            assert pdf_call is not None
            assert pdf_call.kwargs["width"] == "210mm"
            assert (
                abs(
                    float(pdf_call.kwargs["height"].replace("mm", ""))
                    - expected_height_mm
                )
                < 0.1
            )
