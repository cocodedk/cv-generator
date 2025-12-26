# Testing

Testing strategy and how to run tests for the CV Generator.

## Test Structure

### Backend Tests

**Location**: `backend/tests/`

**Test Files**:
- `test_models.py`: Pydantic model validation tests
- `test_generator.py`: CVGenerator class tests
- `test_database/test_queries.py`: Database query tests
- `test_database/test_profile_queries.py`: Profile query tests documentation (refactored)
- `test_database/test_profile_queries_save.py`: Profile save and update tests (mocked)
- `test_database/test_profile_queries_get.py`: Profile retrieval tests (mocked)
- `test_database/test_profile_queries_delete.py`: Profile deletion tests (mocked)
- `test_database/test_profile_queries_integration.py`: Profile CRUD integration (live Neo4j)
- `test_api/test_health.py`: Health check endpoint tests
- `test_api/test_cv_endpoints.py`: CV CRUD endpoint tests
- `test_api/test_profile_endpoints.py`: Profile endpoint tests
- `test_api/test_download.py`: File download endpoint tests

**Test Helpers**:
- `test_database/helpers/profile_queries/mocks.py`: Shared mock setup utilities for profile query tests

**Framework**: pytest

**Configuration**: `backend/pytest.ini`

### Frontend Tests

**Location**: `frontend/src/__tests__/`

**Test Files**:
- `components/CVForm.test.tsx`: Main form component tests
- `components/PersonalInfo.test.tsx`: Personal info form tests
- `components/Experience.test.tsx`: Experience array management tests
- `components/Education.test.tsx`: Education array management tests
- `components/Skills.test.tsx`: Skills array management tests
- `components/ProfileManager.test.tsx`: Profile management tests (documentation only)
- `components/ProfileManager.render.test.tsx`: ProfileManager rendering tests
- `components/ProfileManager.load.test.tsx`: Profile loading tests
- `components/ProfileManager.save.test.tsx`: Profile save/update tests
- `components/ProfileManager.delete.test.tsx`: Profile delete and validation tests
- `components/ProfileManager.aiAssist.test.tsx`: AI assist functionality tests

**Test Helpers**:
- `helpers/profileManager/mocks.ts`: Shared mocks and test data factories
- `helpers/profileManager/testHelpers.tsx`: Shared test rendering utilities

**Framework**: Vitest with React Testing Library

**Configuration**: `frontend/vitest.config.ts`

### End-to-End Tests

**Location**: `tests/e2e/`

**Test Files**:
- `ai-cv-generation.spec.ts`: AI CV generation end-to-end flow tests

**Helpers**: `tests/e2e/helpers/`
- `constants.ts`: Test constants (URLs, timeouts)
- `urlUtils.ts`: URL parsing utilities
- `apiCleanup.ts`: API cleanup functions
- `cleanupManager.ts`: Resource cleanup management
- `aiGeneration.ts`: AI generation test helpers

**Framework**: Playwright

**Configuration**: `playwright.config.ts`

## Running Tests

### Backend Tests

**In Docker container** (recommended):
```bash
npm run test:backend
# or
docker-compose exec -T app pytest
```

**With coverage**:
```bash
docker-compose exec -T app pytest --cov=backend --cov-report=html
```

### Frontend Tests

**Run once**:
```bash
npm run test:frontend
# or
cd frontend && npx vitest run
```

**Watch mode**: `cd frontend && npx vitest`
**With coverage**: `cd frontend && npx vitest run --coverage`

### End-to-End Tests

**Prerequisites**: Backend and frontend must be running, and a profile must exist in the database.

**Run all E2E tests**:
```bash
npx playwright test
```

**Run specific test file**:
```bash
npx playwright test tests/e2e/ai-cv-generation.spec.ts
```

**Run in headed mode** (see browser):
```bash
npx playwright test --headed
```

### All Tests

```bash
npm test
```

## Test Database

Most backend tests mock the Neo4j driver. Integration tests run against the live
Neo4j database in Docker and should clean up after themselves.

**Test Isolation**: Integration tests use test data prefixed with "test" to ensure
they don't accidentally modify real profile data. Tests verify profiles are test
profiles before updating or deleting them.

## Writing Tests

**Backend Example**:
```python
def test_create_cv():
    cv_data = {"personal_info": {"name": "Test"}, "experience": [], "education": [], "skills": []}
    cv_id = queries.create_cv(cv_data)
    assert cv_id is not None
```

**Frontend Example**:
```typescript
test('renders form', () => {
  render(<PersonalInfo register={mockRegister} errors={{}} />)
  expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
})
```

## Pre-commit Hooks

Tests and coverage checks run automatically before each commit. The pre-commit hooks will:

1. Run all backend and frontend tests
2. Check test coverage requirements
3. Run linting and formatting checks

If tests fail or coverage is insufficient, the commit will be blocked. See [Development Workflow](workflow.md) for commit requirements.

### Post-Commit Hooks

After task completion, the `update-tests-docs` hook automatically:
1. Runs tests and coverage checks
2. Provides guidance on updating documentation
3. Prompts for manual commit (auto-commit has been removed)

The hook will guide you through:
- Fixing any failing tests
- Improving coverage if needed
- Updating documentation in `docs/`
- Committing changes with proper format (including codex identifier)

## Recent Test Additions

### Backend Tests
- HTML content validation tests for `Experience.description` field
- Plain text length validation (HTML stripping)
- HTML entity handling in validation
- Profile query tests refactored into smaller, focused test files:
  - Save and update tests separated into `test_profile_queries_save.py`
  - Retrieval tests separated into `test_profile_queries_get.py`
  - Deletion tests separated into `test_profile_queries_delete.py`
  - Shared test helpers and mocks in `helpers/profile_queries/mocks.py`

### Frontend Tests
- RichTextarea component tests (25 tests: rendering, onChange, validation, character counting, line break preservation, HTML formatting preservation)
- HTML stripping utility tests
- Updated component tests to reflect RichTextarea usage
- ProfileManager tests refactored into smaller, focused test files:
  - Rendering tests separated from functionality tests
  - Loading, saving, deleting, and AI assist tests in separate files
  - Keyboard shortcut tests (`ProfileManager.keyboardShortcut.test.tsx`)
  - Shared test helpers and mocks in `helpers/profileManager/`
- Hash routing tests with URL encoding/decoding support
