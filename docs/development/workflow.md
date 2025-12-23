# Development Workflow

Best practices and common development tasks for the CV Generator.

## Daily Workflow

### Starting Development

1. Start Docker services: `docker-compose up -d`
2. Start frontend dev server: `npm run dev`
3. Access frontend at http://localhost:5173

### Making Changes

**Backend Changes**:
- Edit Python files in `backend/`
- Changes auto-reload in Docker container
- Check logs: `docker-compose logs -f app`

**Frontend Changes**:
- Edit TypeScript/React files in `frontend/src/`
- Vite HMR automatically updates browser
- No manual refresh needed

### Running Tests

**Backend tests** (in Docker):
```bash
npm run test:backend
```

**Frontend tests** (local):
```bash
npm run test:frontend
```

**All tests**:
```bash
npm test
```

### Code Quality

**Linting**:
```bash
npm run lint:backend   # Backend linting
npm run lint:frontend   # Frontend linting
```

**Formatting**:
```bash
npm run format:backend   # Backend formatting
npm run format:frontend  # Frontend formatting
```

## Git Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit
3. Pre-commit hooks run automatically (tests, linting)
4. Push and create pull request

## Code Organization

### Backend Structure

- `backend/app.py`: Main FastAPI application
- `backend/models.py`: Pydantic data models
- `backend/database/`: Database operations
- `backend/cv_generator/`: ODT generation logic
- `backend/tests/`: Test files

### Frontend Structure

- `frontend/src/App.tsx`: Main application component
- `frontend/src/components/`: React components
- `frontend/src/types/`: TypeScript type definitions
- `frontend/src/__tests__/`: Test files

## Best Practices

1. **Write tests** for new features
2. **Run linting** before committing
3. **Follow code style** (Black for Python, Prettier for TypeScript)
4. **Keep files small** (max 150 lines per file)
5. **Modularize code** into focused modules

## Stopping Development

```bash
# Stop frontend (Ctrl+C in terminal)
# Stop Docker services
docker-compose down
```

Or use the convenience script:
```bash
./scripts/stop-dev.sh
```
