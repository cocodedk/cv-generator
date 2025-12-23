# Development Setup

Complete guide for setting up the CV Generator development environment.

## Quick Setup

For the fastest setup, use the convenience script:

```bash
./scripts/run-dev.sh
```

This handles all setup steps automatically.

## Manual Setup

### Step 1: Start Docker Services

Start backend and database services:

```bash
docker-compose up -d
```

This starts:
- Neo4j database (ports 7474, 7687)
- FastAPI backend (port 8000)

### Step 2: Install Frontend Dependencies

Install Node.js dependencies:

```bash
npm install
```

### Step 3: Start Frontend Dev Server

Start the Vite development server:

```bash
npm run dev
```

Frontend will be available at http://localhost:5173 with hot module replacement.

## Environment Variables

Create a `.env` file in the project root (optional, defaults provided):

```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=cvpassword
NEO4J_DATABASE=neo4j
CORS_ORIGINS=http://localhost:5173,http://localhost:8000
```

## Verify Setup

1. **Backend**: http://localhost:8000/docs (API documentation)
2. **Frontend**: http://localhost:5173 (Web interface)
3. **Database**: http://localhost:7474 (Neo4j Browser)

## Development Workflow

See [Development Workflow](workflow.md) for best practices and common tasks.

## Troubleshooting

See [Troubleshooting Guide](../troubleshooting/common-issues.md) for common setup issues.
