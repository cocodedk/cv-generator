"""FastAPI application for CV generator."""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from backend.app_helpers.lifespan import lifespan
from backend.app_helpers.middleware import setup_rate_limiting, setup_cors
from backend.app_helpers.exception_handlers import validation_exception_handler
from backend.app_helpers.routes import health, cv, profile, docx, print_html
from backend.services.cv_file_service import CVFileService

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

# Initialize CV file service
cv_file_service = CVFileService(output_dir)

# Register routes
app.include_router(health.router)
cv_router = cv.create_cv_router(limiter, cv_file_service, output_dir)
app.include_router(cv_router)
docx_router = docx.create_docx_router(limiter, cv_file_service, output_dir)
app.include_router(docx_router)
print_html_router = print_html.create_print_html_router(limiter, cv_file_service)
app.include_router(print_html_router)
profile_router = profile.create_profile_router(limiter)
app.include_router(profile_router)

# Mount static files for frontend (only in production/Docker)
# This must be after all API routes to ensure routes are checked first
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists() and (frontend_path / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
