"""FastAPI application for CV generator."""
import os
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.models import CVData, CVResponse, CVListResponse
from backend.database.connection import Neo4jConnection
from backend.database import queries
from backend.cv_generator.generator import CVGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CV Generator API", version="1.0.0")

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


# Initialize database connection
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    logger.info("Starting up CV Generator API...")
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        if Neo4jConnection.verify_connectivity():
            logger.info("Successfully connected to Neo4j database")
            return
        retry_count += 1
        logger.warning(
            f"Failed to connect to Neo4j database (attempt {retry_count}/{max_retries})"
        )
        if retry_count < max_retries:
            import time

            time.sleep(2)

    logger.error("Failed to connect to Neo4j database after multiple attempts")
    raise Exception("Failed to connect to Neo4j database")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    Neo4jConnection.close()


# Create output directory
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)


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
async def generate_cv(cv_data: CVData):
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
async def save_cv(cv_data: CVData):
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


# Mount static files for frontend (only in production/Docker)
# This must be after all API routes to ensure routes are checked first
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists() and (frontend_path / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
