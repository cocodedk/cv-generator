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
npm run lint:backend   # Backend linting (flake8)
npm run lint:frontend   # Frontend linting (ESLint)
```

**Formatting**:
```bash
npm run format:backend   # Backend formatting (Black)
npm run format:frontend  # Frontend formatting (Prettier)
```

**Note**: All backend code must pass flake8 linting. Unused imports and variables are automatically flagged. Compatibility modules that re-export functions use `# noqa: F401` comments to suppress false positives.

## Git Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit
3. Pre-commit hooks run automatically (tests, linting, coverage check)
4. Ensure changelog entries exist (enforced by pre-push hook)
5. Use `/push` command for final push after manual review
6. Create pull request

### Commit Requirements

All commits must follow these mandatory rules:

1. **Commit all uncommitted files**: All uncommitted files must be committed in a single commit.

2. **Write a descriptive message**: Write a commit message that clearly describes all the changes made.

3. **Include codex identifier**: Every commit message must include a codex identifier per project standard. Use the format `[CODEX-XXX]` where XXX is a unique identifier for the change set.

4. **Ensure changelog entries exist**: Before pushing, ensure that appropriate changelog entries exist documenting the changes. This is enforced by a pre-push hook that will prevent pushing if changelog entries are missing.

5. **Use /push command for final push**: After committing, use the `/push` command for the final push after manual review. Do not auto-commit or auto-push.

#### Commit Message Template

```
[CODEX-XXX] Brief summary of changes

- Change 1: Description of first change
- Change 2: Description of second change
- Change 3: Description of third change
```

Example:
```
[CODEX-143] Expand commit guidance and improve test hook workflow

- Expand commit.md with comprehensive commit requirements and template
- Add mandatory codex identifier requirement to commit messages
- Require changelog entries before push (enforced by pre-push hook)
- Document use of /push command for final push after review
```

## Code Organization

### Backend Structure

- `backend/app.py`: Main FastAPI application
- `backend/models.py`: Pydantic data models
- `backend/database/`: Database operations
- `backend/cv_generator_docx/`: DOCX generation logic
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
