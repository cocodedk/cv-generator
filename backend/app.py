"""FastAPI application for CV generator."""
import logging
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from backend.app_helpers.lifespan import lifespan
from backend.app_helpers.middleware import setup_rate_limiting, setup_cors
from backend.app_helpers.exception_handlers import validation_exception_handler
from backend.app_helpers.routes import (
    health,
    cv,
    profile,
    docx,
    html,
    print_html,
    ai,
    pdf,
    cover_letter,
)
from backend.services.cv_file_service import CVFileService
from backend.services.pdf_service import PDFService

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create FastAPI app
app = FastAPI(title="CV Generator API", version="1.0.0", lifespan=lifespan)

# Setup middleware
limiter = setup_rate_limiting(app)
setup_cors(app)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Create output directory
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)

# Store in app.state for router/test access
app.state.output_dir = output_dir

# Initialize PDF service
pdf_service = PDFService()

# Initialize CV file service
showcase_dir_env = os.getenv("CV_SHOWCASE_OUTPUT_DIR")
showcase_keys_dir_env = os.getenv("CV_SHOWCASE_KEYS_DIR")
showcase_enabled = os.getenv("CV_SHOWCASE_ENABLED", "true").lower() in {
    "1",
    "true",
    "yes",
}
showcase_dir = Path(showcase_dir_env) if showcase_dir_env else output_dir / "showcase"
showcase_keys_dir = (
    Path(showcase_keys_dir_env)
    if showcase_keys_dir_env
    else output_dir / "showcase_keys"
)
scramble_key = os.getenv("CV_SHOWCASE_SCRAMBLE_KEY")
cv_file_service = CVFileService(
    output_dir=output_dir,
    showcase_dir=showcase_dir,
    showcase_keys_dir=showcase_keys_dir,
    showcase_enabled=showcase_enabled,
    scramble_key=scramble_key,
    pdf_service=pdf_service,
)

# Clean up old download files on startup
try:
    cleaned_count = cv_file_service.cleanup_old_download_files(max_age_hours=24)
    if cleaned_count > 0:
        print(f"Cleaned up {cleaned_count} old download files on startup")
except Exception as e:
    print(f"Warning: Failed to clean up old download files: {e}")

# Register routes
app.include_router(health.create_health_router(cv_file_service))
cv_router = cv.create_cv_router(limiter, cv_file_service, output_dir)
app.include_router(cv_router)
html_router = html.create_html_router(limiter, cv_file_service, output_dir)
app.include_router(html_router)
docx_router = docx.create_docx_router(limiter, cv_file_service, output_dir)
app.include_router(docx_router)
print_html_router = print_html.create_print_html_router(limiter, cv_file_service)
app.include_router(print_html_router)
pdf_router = pdf.create_pdf_router(limiter, cv_file_service, pdf_service)
app.include_router(pdf_router)
profile_router = profile.create_profile_router(limiter, cv_file_service)
app.include_router(profile_router)
ai_router = ai.create_ai_router(limiter)
app.include_router(ai_router)
cover_letter_router = cover_letter.create_cover_letter_router(limiter, pdf_service)
app.include_router(cover_letter_router)

# Mount static files for frontend (only in production/Docker)
# This must be after all API routes to ensure routes are checked first
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists() and (frontend_path / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
