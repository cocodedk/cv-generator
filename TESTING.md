# Testing and Pre-commit Hooks Setup

This document describes the testing infrastructure and pre-commit hooks that have been set up for the CV Generator project.

## Testing Setup

### Backend Tests (Python)

Backend tests use **pytest** with the following structure:

- **Location**: `backend/tests/`
- **Configuration**: `backend/pytest.ini`
- **Test files**:
  - `test_models.py` - Pydantic model validation tests
  - `test_generator.py` - CVGenerator class tests
  - `test_database/test_queries.py` - Database query tests
  - `test_api/test_health.py` - Health check endpoint tests
  - `test_api/test_cv_endpoints.py` - CV CRUD endpoint tests
  - `test_api/test_download.py` - File download endpoint tests

**Run backend tests (in Docker container):**
```bash
npm run test:backend
# This runs: docker-compose exec -T app pytest

# Or run locally (if you have Python environment set up):
npm run test:backend:local
# or
cd backend && pytest
```

**Run with coverage:**
```bash
cd backend && pytest --cov=backend --cov-report=html
```

### Frontend Tests (TypeScript/React)

Frontend tests use **Vitest** with React Testing Library:

- **Location**: `frontend/src/__tests__/`
- **Configuration**: `frontend/vitest.config.ts`
- **Test files**:
  - `components/CVForm.test.tsx` - Main form component tests
  - `components/PersonalInfo.test.tsx` - Personal info form tests
  - `components/Experience.test.tsx` - Experience array management tests
  - `components/Education.test.tsx` - Education array management tests
  - `components/Skills.test.tsx` - Skills array management tests

**Run frontend tests:**
```bash
npm run test:frontend
# or
cd frontend && npx vitest run
```

**Run in watch mode:**
```bash
cd frontend && npx vitest
```

**Run with coverage:**
```bash
cd frontend && npx vitest run --coverage
```

### Run All Tests

```bash
npm test
```

## Linting and Formatting

### Backend (Python)

**Linting with flake8 (in Docker container):**
```bash
npm run lint:backend
# This runs: docker-compose exec -T app flake8 backend

# Or run locally:
npm run lint:backend:local
# or
flake8 backend
```

**Formatting with Black (in Docker container):**
```bash
npm run format:backend
# This runs: docker-compose exec -T app black backend

# Or run locally:
npm run format:backend:local
# or
black backend
```

### Frontend (TypeScript/React)

**Linting with ESLint:**
```bash
npm run lint:frontend
# or
eslint frontend/src --ext .ts,.tsx
```

**Formatting with Prettier:**
```bash
npm run format:frontend
# or
prettier --write "frontend/src/**/*.{ts,tsx,css}"
```

## Pre-commit Hooks

Pre-commit hooks automatically run tests, linting, and formatting before each commit.

### Installation

1. Install pre-commit (if not already installed):
```bash
pip install pre-commit
```

2. Install the git hooks:
```bash
pre-commit install
```

### What Runs on Commit

The pre-commit hooks will:

1. **General checks**:
   - Remove trailing whitespace
   - Ensure files end with newline
   - Validate YAML and JSON files
   - Check for large files

2. **Python**:
   - Format code with Black
   - Lint code with flake8
   - Run pytest tests

3. **TypeScript/React**:
   - Format code with Prettier
   - Lint code with ESLint
   - Run Vitest tests

### Bypassing Hooks (Not Recommended)

If you need to bypass hooks for an emergency commit:
```bash
git commit --no-verify
```

**Note**: This should only be used in exceptional circumstances.

### Updating Hooks

To update pre-commit hooks to latest versions:
```bash
pre-commit autoupdate
```

## Configuration Files

- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `.flake8` - Python linting rules
- `.eslintrc.json` - ESLint configuration
- `.prettierrc` - Prettier formatting rules
- `.prettierignore` - Files to exclude from Prettier
- `backend/pytest.ini` - Pytest configuration
- `frontend/vitest.config.ts` - Vitest configuration

## Troubleshooting

### Tests Fail in Pre-commit

If tests fail during pre-commit:
1. Ensure Docker is running: `docker ps`
2. Ensure containers are up: `docker-compose ps`
3. Run tests manually to see the error: `npm test`
4. Fix the failing tests
5. Try committing again

### Docker Container Not Running

If you see "container not found" errors:
1. Start the containers: `docker-compose up -d`
2. Wait for services to be ready
3. Try running tests again: `npm run test:backend`

### Dependencies Not Found

**Backend (in container):**
- Dependencies are installed in the Docker image
- If missing, rebuild: `docker-compose build`

**Frontend (local):**
- Install frontend dependencies: `npm install`

**Local Python environment (optional):**
- If running tests locally: `pip install -r requirements.txt` (in a virtual environment)

### Pre-commit Hooks Not Running

If hooks don't run on commit:
1. Verify installation: `pre-commit --version`
2. Reinstall hooks: `pre-commit uninstall && pre-commit install`
3. Test manually: `pre-commit run --all-files`
