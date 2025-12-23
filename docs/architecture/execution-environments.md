# Execution Environments

The CV Generator uses a hybrid development architecture where different components run in different environments for optimal development experience.

## Architecture Overview

- **Backend (FastAPI)**: Runs in Docker container
- **Neo4j Database**: Runs in Docker container
- **Frontend (React/Vite)**: Runs locally on host machine
- **Tests**: Backend tests run in Docker, frontend tests run locally

## Docker Containers

### Backend Container (`cv-app`)

- **Service name**: `app` in docker-compose.yml
- **Container name**: `cv-app`
- **Port**: 8000 (mapped to host)
- **What runs here**:
  - FastAPI backend application
  - Python dependencies (from requirements.txt)
  - Backend tests (pytest)
  - Backend linting (flake8)
  - Backend formatting (black)

### Neo4j Container (`cv-neo4j`)

- **Service name**: `neo4j` in docker-compose.yml
- **Container name**: `cv-neo4j`
- **Ports**: 7474 (HTTP), 7687 (Bolt)
- **What runs here**:
  - Neo4j database server
  - Database storage and operations

## Local Host Machine

### Frontend Development

- **What runs here**:
  - Vite dev server (port 5173)
  - Frontend tests (Vitest)
  - Frontend linting (ESLint)
  - Frontend formatting (Prettier)
  - Node.js dependencies (from package.json)

## Command Execution Locations

### Backend Commands (Run in Docker Container)

All backend commands should be executed inside the Docker container:

```bash
# Tests
docker-compose exec -T app pytest
# or via npm script: npm run test:backend

# Linting
docker-compose exec -T app flake8 backend
# or via npm script: npm run lint:backend

# Formatting
docker-compose exec -T app black backend
# or via npm script: npm run format:backend

# Interactive shell
docker-compose exec app bash
```

**Note**: If container is not running, use `docker-compose run --rm app <command>` instead of `exec`.

### Frontend Commands (Run Locally)

```bash
npm run dev              # Development server
npm run test:frontend    # Tests
npm run lint:frontend    # Linting
npm run format:frontend  # Formatting
```

### Database Commands

Neo4j access: Browser UI (http://localhost:7474), Bolt (bolt://localhost:7687), Cypher shell (`docker-compose exec neo4j cypher-shell`).

## Important Notes

1. Backend dependencies: Installed in Docker image. Rebuild if requirements.txt changes.
2. Frontend dependencies: Installed locally with `npm install`.
3. Volume mounts: Backend code mounted for auto-reload.

See [Development Workflow](../development/workflow.md) for details.
