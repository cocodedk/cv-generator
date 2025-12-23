# Testing

Testing strategy and how to run tests for the CV Generator.

## Test Structure

### Backend Tests

**Location**: `backend/tests/`

**Test Files**:
- `test_models.py`: Pydantic model validation tests
- `test_generator.py`: CVGenerator class tests
- `test_database/test_queries.py`: Database query tests
- `test_api/test_health.py`: Health check endpoint tests
- `test_api/test_cv_endpoints.py`: CV CRUD endpoint tests
- `test_api/test_download.py`: File download endpoint tests

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

**Framework**: Vitest with React Testing Library

**Configuration**: `frontend/vitest.config.ts`

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

### All Tests

```bash
npm test
```

## Test Database

Backend tests use the same Neo4j database. Tests should clean up after themselves.

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

Tests run automatically before each commit. See [Development Workflow](workflow.md).
