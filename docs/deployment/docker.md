# Docker Setup

Docker configuration and setup for the CV Generator.

## Docker Compose Services

The application uses Docker Compose with two services:

### Backend Service (`app`)

- **Image**: Built from `Dockerfile`
- **Container name**: `cv-app`
- **Port**: 8000 (mapped to host)
- **Volumes**:
  - `./backend:/app/backend`: Backend code (for development)
  - `./backend/output:/app/backend/output`: Generated ODT files
- **Environment variables**: From `.env` file or docker-compose.yml
- **Depends on**: `neo4j` service

### Neo4j Service (`neo4j`)

- **Image**: `neo4j:5.15-community`
- **Container name**: `cv-neo4j`
- **Ports**:
  - 7474: HTTP interface (Neo4j Browser)
  - 7687: Bolt protocol
- **Volumes**:
  - `neo4j_data`: Database persistence
- **Environment variables**:
  - `NEO4J_AUTH`: Authentication (neo4j/cvpassword)

## Dockerfile

Multi-stage build process:

1. **Base stage**: Python 3.11 with system dependencies
2. **Dependencies stage**: Install Python packages
3. **Frontend stage**: Build React frontend
4. **Final stage**: Combine backend and frontend

## Building Images

**Build all services**:
```bash
docker-compose build
```

**Build specific service**:
```bash
docker-compose build app
```

**Build without cache**:
```bash
docker-compose build --no-cache
```

## Running Containers

**Start in background**:
```bash
docker-compose up -d
```

**Start with logs**:
```bash
docker-compose up
```

**Stop containers**:
```bash
docker-compose down
```

**Stop and remove volumes** (clean database):
```bash
docker-compose down -v
```

## Container Management

**View containers**: `docker-compose ps`
**View logs**: `docker-compose logs -f app` (backend), `docker-compose logs -f neo4j` (database), `docker-compose logs -f` (all)
**Execute commands**: `docker-compose exec app bash` (backend), `docker-compose exec neo4j bash` (database)

## Volume Management

**List**: `docker volume ls`
**Inspect**: `docker volume inspect cv_neo4j_data`
**Remove** (deletes data): `docker-compose down -v`

## Production Considerations

For production: use env vars for secrets, configure CORS, set up reverse proxy, use Docker secrets, configure health checks, set resource limits.

See [Production Deployment](production.md) for details.
