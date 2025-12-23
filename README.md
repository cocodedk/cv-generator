# CV Generator

A full-stack application for generating professional DOCX CV documents with a modern web interface. Built with React + TypeScript + Tailwind CSS frontend, Python FastAPI backend, and Neo4j database for CV storage.

## Features

- **Web Interface**: Modern React UI with Tailwind CSS for creating CVs
- **DOCX Generation**: Generate professional Word-compatible documents
- **CV Storage**: Neo4j graph database for storing and managing CVs
- **CRUD Operations**: Create, read, update, and delete CVs
- **Search**: Search CVs by name, email, or other criteria
- **Dockerized**: Easy setup with Docker Compose

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: Neo4j 5.15
- **Document Generation**: Pandoc + python-docx
- **Containerization**: Docker, Docker Compose

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Start all services with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474 (username: neo4j, password: cvpassword)

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Stop services:**
   ```bash
   docker-compose down
   ```

6. **Stop and remove volumes (clean database):**
   ```bash
   docker-compose down -v
   ```

## Project Structure

```
cv/
├── backend/           # Python FastAPI backend
│   ├── app.py        # Main FastAPI application
│   ├── database/     # Neo4j database operations
│   ├── cv_generator_docx/ # DOCX document generation
│   ├── themes/       # Theme definitions
│   └── models.py     # Pydantic models
├── frontend/          # React TypeScript frontend
│   └── src/
│       ├── components/ # React components
│       └── types/     # TypeScript types
├── docker-compose.yml # Docker Compose configuration
└── Dockerfile        # Application Dockerfile
```

## API Endpoints

- `POST /api/generate-cv-docx` - Generate DOCX file from CV data and save to Neo4j
- `POST /api/save-cv` - Save CV data to Neo4j without generating file
- `GET /api/cv/{cv_id}` - Retrieve CV data by ID
- `GET /api/cvs` - List all CVs (with pagination and search)
- `DELETE /api/cv/{cv_id}` - Delete CV
- `GET /api/download-docx/{filename}` - Download generated DOCX file
- `GET /api/health` - Health check endpoint

## Environment Variables

Create a `.env` file (or use `.env.example` as a template):

```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=cvpassword
NEO4J_DATABASE=neo4j
```

## Development

### Quick Start (Recommended)

**Easiest way to run the app:**

```bash
# Option 1: Using the script
./scripts/run-dev.sh

# Option 2: Using npm
npm run dev:full
# or
npm start
```

This single command will:
- Start Docker services (backend + Neo4j)
- Install frontend dependencies if needed
- Start the frontend dev server with HMR

**To stop everything:**
```bash
./scripts/stop-dev.sh
# or press Ctrl+C in the terminal running the script
```

### Manual Setup

For the best development experience with hot module replacement (HMR) and auto-reload:

**Architecture:**
- **Frontend**: Run locally with Vite dev server (port 5173) - provides instant HMR/livereload
- **Backend**: Run in Docker with auto-reload enabled (port 8000)
- **Neo4j**: Run in Docker (ports 7474, 7687)

**Manual Setup Steps:**

1. **Start backend and database services:**
   ```bash
   docker-compose up -d
   ```
   This starts Neo4j and the FastAPI backend with auto-reload enabled.

2. **Install frontend dependencies (one-time):**
   ```bash
   npm install
   ```

3. **Start frontend dev server:**
   ```bash
   npm run dev
   ```
   The Vite dev server will start on http://localhost:5173 with HMR enabled.

4. **Access the application:**
   - Frontend (with HMR): http://localhost:5173
   - API Documentation: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474

**Benefits:**
- Frontend changes reload instantly with Vite HMR
- Backend Python changes auto-reload in Docker
- Better IDE integration and debugging
- Faster development cycle

### Alternative: Full Docker Development

If you prefer everything in Docker (slower HMR, but no local Node.js needed):

1. Start all services:
   ```bash
   docker-compose up -d
   ```

2. Access at http://localhost:8000 (backend serves built frontend)

### Local Development (No Docker)

If you want to run everything locally:

1. **Neo4j** (still in Docker):
   ```bash
   docker run -p 7474:7474 -p 7687:7687 neo4j:5.15-community
   ```

2. **Backend:**
   ```bash
   pip install -r requirements.txt
   uvicorn backend.app:app --reload --port 8000
   ```

3. **Frontend:**
   ```bash
   npm install
   npm run dev
   ```

## Building for Production

```bash
docker-compose -f docker-compose.yml up -d --build
```

## License

MIT
