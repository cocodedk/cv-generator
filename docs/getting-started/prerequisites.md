# Prerequisites

Before setting up the CV Generator, ensure you have the following installed and configured.

## Required Software

### Docker and Docker Compose

- **Docker Engine**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

Verify installation:
```bash
docker --version
docker-compose --version
```

### Node.js and npm (for frontend development)

- **Node.js**: Version 18 or higher
- **npm**: Version 9 or higher (comes with Node.js)

Verify installation:
```bash
node --version
npm --version
```

## Optional Software

### Python (for local backend development)

- **Python**: Version 3.11 or higher
- **pip**: Python package manager

Only required if you want to run the backend locally without Docker.

## System Requirements

- **Operating System**: Linux, macOS, or Windows (with WSL2 for Windows)
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 2GB free space
- **Network**: Internet connection for downloading Docker images and npm packages

## Docker Resources

Ensure Docker has sufficient resources allocated:
- **Memory**: At least 2GB allocated to Docker
- **CPU**: At least 2 CPU cores
- **Disk**: Docker should have at least 10GB available

## Environment Variables

The application uses environment variables for configuration. See [Development Setup](../development/setup.md) for details on configuring these.
