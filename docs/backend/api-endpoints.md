# API Endpoints

Complete REST API endpoint documentation for the CV Generator backend.

## Base URL

- **Development**: http://localhost:8000
- **API Prefix**: `/api`

## Endpoints

### Health Check

**GET** `/api/health` - Check API and database connectivity. Returns status and database connection state.

### Generate CV (DOCX)

**POST** `/api/generate-cv-docx` - Generate DOCX file from CV data and save to Neo4j.
**Request**: `CVData`
**Response**: `CVResponse` with cv_id and filename

### Save CV

**POST** `/api/save-cv` - Save CV data to Neo4j without generating file.
**Request**: `CVData`
**Response**: `CVResponse` with cv_id

### Get CV

**GET** `/api/cv/{cv_id}` - Retrieve CV data by ID. Returns CV data object or 404 if not found.

### List CVs

**GET** `/api/cvs` - List all saved CVs with pagination and search.
**Query params**: `limit` (default: 50, max: 100), `offset` (default: 0), `search` (optional)
**Response**: `CVListResponse` with cvs array and total count

### Update CV

**PUT** `/api/cv/{cv_id}` - Update existing CV data.
**Request**: `CVData`
**Response**: `CVResponse`
**Errors**: 404 if CV not found

### Delete CV

**DELETE** `/api/cv/{cv_id}` - Delete CV from Neo4j. Returns success message or 404.

### Download CV File (DOCX)

**GET** `/api/download-docx/{filename}` - Download generated DOCX file.
**Path param**: `filename` (e.g., `cv_12345678.docx`)
**Response**: File download
**Errors**: 400 (invalid filename/type), 404 (file not found)

### Generate DOCX for Existing CV

**POST** `/api/cv/{cv_id}/generate-docx` - Generate DOCX file for an existing CV.
**Response**: `CVResponse`
**Errors**: 404 if CV not found

### Print HTML Endpoints

**POST** `/api/render-print-html` - Render browser-printable HTML from CV data payload.
**Request**: `CVData` (theme defaults to "classic" if not provided)
**Response**: HTML content (A4 print-ready format)
**Errors**: 500 (server error)

**GET** `/api/cv/{cv_id}/print-html` - Render browser-printable HTML for existing CV.
**Response**: HTML content (A4 print-ready format)
**Errors**: 404 (CV not found), 500 (server error)

See [Print HTML Generation](print-html-generation.md) for details.

### Profile Endpoints

**POST** `/api/profile` - Save or update master profile.
**Request**: `ProfileData` (see [Models](models.md))
**Response**: `ProfileResponse` with status and message
**Errors**: 422 (validation error), 500 (server error)

**GET** `/api/profile` - Get master profile.
**Response**: `ProfileData` object or 404 if not found
**Errors**: 404 (profile not found), 500 (server error)

**DELETE** `/api/profile` - Delete master profile.
**Response**: `ProfileResponse` with status and message
**Errors**: 404 (profile not found), 500 (server error)

## Rate Limiting

Rate limits (per IP): Profile (30/min), CV save/list (20/min), DOCX generation (10/min), Print HTML (20-30/min). Returns 429 when exceeded.

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See [Data Models](models.md) for request/response structures.
