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
  - `neo4j_data:/data`: Main database data (persisted as `cv_neo4j_data` volume)
  - `neo4j_logs:/logs`: Log files (persisted as `cv_neo4j_logs` volume)
  - `neo4j_import:/var/lib/neo4j/import`: Import directory (persisted as `cv_neo4j_import` volume)
  - `neo4j_plugins:/plugins`: Plugin directory (persisted as `cv_neo4j_plugins` volume)
- **Restart policy**: `unless-stopped` (automatically restarts on system reboot)
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

**Stop and remove volumes** (⚠️ **WARNING: This deletes all database data**):
```bash
docker-compose down -v
```

## Data Persistence

⚠️ **IMPORTANT**: Neo4j database data is stored in Docker volumes and persists across container stops and rebuilds.

### How Data Persistence Works

- **`docker-compose down`**: Stops containers but **preserves** all data in volumes
- **`docker-compose down -v`**: Stops containers and **deletes** all volumes (⚠️ **permanently deletes all database data**)
- **`docker-compose build`**: Rebuilds images but **does not affect** volume data
- **`docker-compose up -d`**: Starts containers and **restores** data from existing volumes

### Volume Names

Neo4j data is stored in explicitly named volumes:
- `cv_neo4j_data`: Main database data (most important)
- `cv_neo4j_logs`: Log files
- `cv_neo4j_import`: Import directory
- `cv_neo4j_plugins`: Plugin directory

These volumes persist even if Docker Compose project name changes.

### Backup Recommendations

To backup your Neo4j data:

1. **List volumes**: `docker volume ls | grep cv_neo4j`
2. **Backup volume**: Use `docker run` with volume mount to export data
3. **Restore volume**: Copy backup data back to volume

Example backup:
```bash
# Create backup directory
mkdir -p ./backups

# Backup Neo4j data volume
docker run --rm -v cv_neo4j_data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/neo4j_data_backup_$(date +%Y%m%d).tar.gz -C /data .
```

### Restart Policy

The Neo4j service is configured with `restart: unless-stopped`, meaning it will automatically restart on system reboot or Docker daemon restart, ensuring data availability.

## Container Management

**View containers**: `docker-compose ps`
**View logs**: `docker-compose logs -f app` (backend), `docker-compose logs -f neo4j` (database), `docker-compose logs -f` (all)
**Execute commands**: `docker-compose exec app bash` (backend), `docker-compose exec neo4j bash` (database)

## Volume Management

**List volumes**: `docker volume ls | grep cv_neo4j`

**Inspect volume**:
```bash
docker volume inspect cv_neo4j_data
```

**View volume location**: Volumes are stored in Docker's volume directory (typically `/var/lib/docker/volumes/` on Linux)

**Remove volumes** (⚠️ **WARNING: This permanently deletes all database data**):
```bash
docker-compose down -v
```

**Manual volume removal** (if needed):
```bash
docker volume rm cv_neo4j_data cv_neo4j_logs cv_neo4j_import cv_neo4j_plugins
```

## Production Considerations

For production: use env vars for secrets, configure CORS, set up reverse proxy, use Docker secrets, configure health checks, set resource limits.

See [Production Deployment](production.md) for details.
