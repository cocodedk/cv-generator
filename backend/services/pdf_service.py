"""Service for PDF generation using Playwright."""

import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

# A4 width in pixels at 96 DPI
A4_WIDTH_PX = 794  # 210mm = 8.2677 inches * 96 DPI
PADDING_BUFFER_PX = 50  # Extra padding to prevent clipping


class PDFService:
    """Service for generating long single-page PDFs."""

    def __init__(self, timeout: int = 60):
        """Initialize PDF service with timeout."""
        self.timeout = timeout * 1000  # Convert to milliseconds

    async def generate_long_pdf(self, html: str) -> bytes:
        """
        Generate a single-page PDF with A4 width and dynamic height.

        Args:
            html: HTML content to render

        Returns:
            PDF bytes

        Raises:
            ValueError: If HTML is empty
            RuntimeError: If PDF generation fails
        """
        if not html or not html.strip():
            raise ValueError("HTML content cannot be empty")

        async with async_playwright() as p:
            try:
                # Launch browser with --no-sandbox for Docker compatibility
                browser = await p.chromium.launch(
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
                try:
                    # Create page with A4 width viewport
                    page = await browser.new_page(
                        viewport={"width": A4_WIDTH_PX, "height": 800}
                    )

                    # Load HTML content
                    await page.set_content(html, wait_until="domcontentloaded")

                    # Inject CSS to override page break rules for single-page PDF
                    # This removes A4 page size constraints and min-height requirements
                    # Also enforces A4 width constraints and image constraints to prevent overflow
                    await page.add_style_tag(
                        content="""
                        @page {
                            size: auto;
                            margin: 0;
                        }
                        html, body {
                            height: auto !important;
                            min-height: auto !important;
                            max-width: 794px !important;
                            margin: 0 auto !important;
                            box-sizing: border-box !important;
                        }
                        .container, .page, .sheet, .page-content {
                            max-width: 794px !important;
                            width: 100% !important;
                            box-sizing: border-box !important;
                        }
                        .sheet {
                            min-height: auto !important;
                            height: auto !important;
                            margin: 0 auto !important;
                        }
                        .bg-text {
                            min-height: auto !important;
                            height: auto !important;
                        }
                        img, .cv-photo {
                            max-width: 100% !important;
                            height: auto !important;
                        }
                        * {
                            box-sizing: border-box !important;
                        }
                        """
                    )

                    # Wait for fonts to load (with timeout to prevent hanging)
                    try:
                        await asyncio.wait_for(
                            page.evaluate("() => document.fonts.ready"),
                            timeout=self.timeout / 1000,  # Convert milliseconds to seconds
                        )
                    except asyncio.TimeoutError:
                        logger.warning(
                            f"Font loading timed out after {self.timeout/1000}s, proceeding without font wait"
                        )

                    # Wait for network to be idle (images, etc.)
                    await page.wait_for_load_state("networkidle", timeout=self.timeout)

                    # Measure content height
                    height_px = await page.evaluate(
                        "() => document.documentElement.scrollHeight"
                    )
                    height_px += PADDING_BUFFER_PX

                    # Convert pixels to millimeters
                    # inches = px / 96, mm = inches * 25.4
                    height_mm = (height_px / 96) * 25.4

                    logger.info(
                        f"PDF dimensions: width=210mm, height={height_mm:.2f}mm "
                        f"(measured {height_px}px)"
                    )

                    # Generate PDF
                    pdf_bytes = await page.pdf(
                        width="210mm",
                        height=f"{height_mm}mm",
                        print_background=True,
                        display_header_footer=False,
                        margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
                    )

                    return pdf_bytes

                finally:
                    await browser.close()

            except PlaywrightTimeoutError as e:
                logger.error(f"PDF generation timeout: {e}")
                raise RuntimeError(f"PDF generation timed out after {self.timeout/1000}s") from e
            except Exception as e:
                logger.error(f"PDF generation failed: {e}", exc_info=True)
                raise RuntimeError(f"Failed to generate PDF: {str(e)}") from e
