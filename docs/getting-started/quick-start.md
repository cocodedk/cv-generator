# Quick Start Guide

Get the CV Generator up and running in minutes.

## Quick Start (Recommended)

The easiest way to run the application:

```bash
# Option 1: Using the convenience script
./scripts/run-dev.sh

# Option 2: Using npm
npm run dev:full
# or
npm start
```

This single command will:
- Start Docker services (backend + Neo4j)
- Install frontend dependencies if needed
- Start the frontend dev server with hot module replacement

## Access the Application

Once started, access:
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (username: neo4j, password: cvpassword)

## Stop the Application

```bash
# Option 1: Using the script
./scripts/stop-dev.sh

# Option 2: Press Ctrl+C in the terminal
# Then stop Docker services:
docker-compose down
```

## Full Docker Setup (Alternative)

If you prefer everything in Docker:

```bash
docker-compose up -d
```

Access at http://localhost:8000 (backend serves built frontend).

## Next Steps

- See [Development Setup](../development/setup.md) for detailed development environment configuration
- See [Architecture Overview](../architecture/system-overview.md) to understand the system design
- See [API Endpoints](../backend/api-endpoints.md) to explore the REST API
