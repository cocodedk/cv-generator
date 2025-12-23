# API Endpoints

Complete REST API endpoint documentation for the CV Generator backend.

## Base URL

- **Development**: http://localhost:8000
- **API Prefix**: `/api`

## Endpoints

### Health Check

**GET** `/api/health` - Check API and database connectivity. Returns status and database connection state.

### Generate CV

**POST** `/api/generate-cv` - Generate ODT file from CV data and save to Neo4j.
**Request**: `CVData` (see [Models](models.md))
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

### Download CV File

**GET** `/api/download/{filename}` - Download generated ODT file.
**Path param**: `filename` (e.g., `cv_12345678.odt`)
**Response**: File download
**Errors**: 400 (invalid filename/type), 404 (file not found)

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See [Data Models](models.md) for request/response structures.
