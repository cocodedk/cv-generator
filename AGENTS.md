# AGENTS.md

## Commands
- **Dev**: `npm run dev:full` (starts Docker backend + local frontend)
- **Build**: `npm run build` (Vite build)
- **Type check**: `npm run type-check`
- **Test all**: `npm test`
- **Backend test**: `npm run test:backend` (runs pytest in Docker)
- **Backend single test**: `docker-compose exec -T app pytest tests/test_file.py::test_name -v`
- **Frontend test**: `npm run test:frontend` (runs Vitest locally)
- **Frontend single test**: `cd frontend && vitest run src/path/to/test.test.ts`
- **Lint**: `npm run lint:backend` (Docker) / `npm run lint:frontend` (local)
- **Format**: `npm run format:backend` (Docker) / `npm run format:frontend` (local)

## Architecture
- **Frontend**: React 18 + TypeScript + Vite + Tailwind (`frontend/src/`)
- **Backend**: Python FastAPI in Docker (`backend/`), Neo4j database
- **Hybrid setup**: Backend runs in Docker (`cv-app`), frontend runs locally

## Code Style
- Max 150 lines per file; one class per file; DRY principle
- TypeScript: strict types, no `any`, unused vars prefixed with `_`
- Python: flake8 + black formatting, pytest for tests (70% coverage min)
- No console.log in production; modular, reusable components
