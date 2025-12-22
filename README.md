# CV Generator

A full-stack application for generating professional LibreOffice Writer (.odt) CV documents with a modern web interface. Built with React + TypeScript + Tailwind CSS frontend, Python FastAPI backend, and Neo4j database for CV storage.

## Features

- **Web Interface**: Modern React UI with Tailwind CSS for creating CVs
- **ODT Generation**: Generate professional LibreOffice Writer documents
- **CV Storage**: Neo4j graph database for storing and managing CVs
- **CRUD Operations**: Create, read, update, and delete CVs
- **Search**: Search CVs by name, email, or other criteria
- **Dockerized**: Easy setup with Docker Compose

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: Neo4j 5.15
- **Document Generation**: odfpy
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
│   ├── cv_generator/ # ODT document generation
│   └── models.py     # Pydantic models
├── frontend/          # React TypeScript frontend
│   └── src/
│       ├── components/ # React components
│       └── types/     # TypeScript types
├── docker-compose.yml # Docker Compose configuration
└── Dockerfile        # Application Dockerfile
```

## API Endpoints

- `POST /api/generate-cv` - Generate ODT file from CV data and save to Neo4j
- `POST /api/save-cv` - Save CV data to Neo4j without generating file
- `GET /api/cv/{cv_id}` - Retrieve CV data by ID
- `GET /api/cvs` - List all CVs (with pagination and search)
- `DELETE /api/cv/{cv_id}` - Delete CV
- `GET /api/download/{filename}` - Download generated ODT file
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

### Using Docker (Recommended)

All dependencies are installed automatically in containers. No local installation needed.

### Local Development (Optional)

If you want to develop locally without Docker:

1. **Backend:**
   ```bash
   pip install -r requirements.txt
   uvicorn backend.app:app --reload --port 8000
   ```

2. **Frontend:**
   ```bash
   npm install
   npm run dev
   ```

3. **Neo4j:**
   ```bash
   docker run -p 7474:7474 -p 7687:7687 neo4j:5.15-community
   ```

## Building for Production

```bash
docker-compose -f docker-compose.yml up -d --build
```

## License

MIT
