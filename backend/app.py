"""FastAPI application for CV generator."""
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.models import (
    CVData,
    CVResponse,
    CVListResponse,
    ProfileData,
    ProfileResponse,
)
from backend.database.connection import Neo4jConnection
from backend.database import queries
from backend.cv_generator.generator import CVGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting up CV Generator API...")
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        if Neo4jConnection.verify_connectivity():
            logger.info("Successfully connected to Neo4j database")
            break
        retry_count += 1
        logger.warning(
            f"Failed to connect to Neo4j database (attempt {retry_count}/{max_retries})"
        )
        if retry_count < max_retries:
            await asyncio.sleep(2)

    if retry_count >= max_retries:
        logger.error("Failed to connect to Neo4j database after multiple attempts")
        raise Exception("Failed to connect to Neo4j database")

    yield

    # Shutdown
    Neo4jConnection.close()


app = FastAPI(title="CV Generator API", version="1.0.0", lifespan=lifespan)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:8000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create output directory
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)


# Validation error handler for user-friendly messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors to user-friendly messages."""
    error_messages = []
    error_mapping = {
        "value_error.email": "Email format invalid",
        "value_error.missing": "Field is required",
        "type_error.str": "Expected text value",
        "type_error.integer": "Expected number value",
        "value_error.str.min_length": "Value is too short",
        "value_error.str.max_length": "Value is too long",
    }

    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_type = error.get("type", "")
        error_msg = error.get("msg", "")

        # Try to map to friendly message
        friendly_msg = error_mapping.get(error_type, error_msg)

        # Extract field name (last part of path)
        if field_path:
            field_name = field_path.split(" -> ")[-1]
            if field_name.startswith("body."):
                field_name = field_name[5:]  # Remove "body." prefix
        else:
            field_name = "unknown field"

        error_messages.append(f"{field_name}: {friendly_msg}")

    return JSONResponse(
        status_code=422,
        content={"detail": error_messages, "errors": exc.errors()},
    )


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    db_connected = Neo4jConnection.verify_connectivity()
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": "connected" if db_connected else "disconnected",
    }


# Generate CV endpoint
@app.post("/api/generate-cv", response_model=CVResponse)
@limiter.limit("10/minute")
async def generate_cv(request: Request, cv_data: CVData):
    """Generate ODT file from CV data and save to Neo4j."""
    try:
        # Convert Pydantic model to dict
        cv_dict = cv_data.model_dump()

        # Save to Neo4j
        cv_id = queries.create_cv(cv_dict)

        # Generate ODT file
        generator = CVGenerator()
        filename = f"cv_{cv_id[:8]}.odt"
        output_path = output_dir / filename
        generator.generate(cv_dict, str(output_path))

        # Persist generated filename for download listing
        queries.set_cv_filename(cv_id, filename)

        return CVResponse(cv_id=cv_id, filename=filename, status="success")
    except Exception as e:
        logger.error("Failed to generate CV", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to generate CV")


# Save CV endpoint (without generating file)
@app.post("/api/save-cv", response_model=CVResponse)
@limiter.limit("20/minute")
async def save_cv(request: Request, cv_data: CVData):
    """Save CV data to Neo4j without generating file."""
    try:
        cv_dict = cv_data.model_dump()
        cv_id = queries.create_cv(cv_dict)
        return CVResponse(cv_id=cv_id, status="success")
    except Exception as e:
        logger.error("Failed to save CV", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to save CV")


# Get CV by ID
@app.get("/api/cv/{cv_id}")
async def get_cv(cv_id: str):
    """Retrieve CV data from Neo4j."""
    cv = queries.get_cv_by_id(cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


# List CVs
@app.get("/api/cvs", response_model=CVListResponse)
async def list_cvs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
):
    """List all saved CVs with pagination."""
    result = queries.list_cvs(limit=limit, offset=offset, search=search)
    return CVListResponse(**result)


# Delete CV
@app.delete("/api/cv/{cv_id}")
async def delete_cv(cv_id: str):
    """Delete CV from Neo4j."""
    success = queries.delete_cv(cv_id)
    if not success:
        raise HTTPException(status_code=404, detail="CV not found")
    return {"status": "success", "message": "CV deleted"}


# Download CV file
@app.get("/api/download/{filename}")
async def download_cv(filename: str):
    """Download generated CV file."""
    # Validate filename to prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Only allow .odt files
    if not filename.endswith(".odt"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_path = output_dir / filename

    # Ensure file is within output directory (prevent path traversal)
    try:
        file_path.resolve().relative_to(output_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.oasis.opendocument.text",
    )


# Update CV endpoint
@app.put("/api/cv/{cv_id}", response_model=CVResponse)
async def update_cv_endpoint(cv_id: str, cv_data: CVData):
    """Update CV data."""
    try:
        cv_dict = cv_data.model_dump()
        success = queries.update_cv(cv_id, cv_dict)
        if not success:
            raise HTTPException(status_code=404, detail="CV not found")
        return CVResponse(cv_id=cv_id, status="success")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update CV %s", cv_id, exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to update CV")


# Profile endpoints
@app.post("/api/profile", response_model=ProfileResponse)
@limiter.limit("30/minute")
async def save_profile_endpoint(request: Request, profile_data: ProfileData):
    """Save or update master profile."""
    try:
        profile_dict = profile_data.model_dump()
        success = queries.save_profile(profile_dict)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save profile")
        return ProfileResponse(status="success", message="Profile saved successfully")
    except Exception as e:
        logger.error("Failed to save profile", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to save profile")


@app.get("/api/profile")
async def get_profile_endpoint():
    """Get master profile."""
    try:
        profile = queries.get_profile()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get profile", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to get profile")


@app.delete("/api/profile", response_model=ProfileResponse)
async def delete_profile_endpoint():
    """Delete master profile."""
    try:
        success = queries.delete_profile()
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        return ProfileResponse(status="success", message="Profile deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete profile", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to delete profile")


# Mount static files for frontend (only in production/Docker)
# This must be after all API routes to ensure routes are checked first
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists() and (frontend_path / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
