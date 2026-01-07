# Testing

Testing strategy and how to run tests for the CV Generator.

## Test Structure

### Backend Tests

**Location**: `backend/tests/`

**Test Files**:

#### API Tests (`test_api/`)
- `test_health.py`: Health check endpoint tests
- `test_cv_endpoints.py`: CV CRUD endpoint tests
- `test_profile_endpoints.py`: Profile endpoint tests
- `test_download.py`: File download endpoint tests
- `cover_letter_endpoints/`: Cover letter API endpoint tests (refactored):
  - `test_generate_cover_letter.py`: Cover letter generation endpoint tests
  - `test_export_pdf.py`: PDF export endpoint tests
  - `test_save_cover_letter.py`: Cover letter saving endpoint tests
  - `test_list_cover_letters.py`: Cover letter listing endpoint tests
  - `test_get_cover_letter.py`: Cover letter retrieval endpoint tests
  - `test_delete_cover_letter.py`: Cover letter deletion endpoint tests
- `exception_handlers/`: Exception handler tests (refactored):
  - `test_field_names.py`: Friendly field name generation tests
  - `test_field_paths.py`: Field path generation tests
  - `test_validation_handler.py`: Validation exception handler tests
- `ai_endpoints/`: AI endpoint tests (refactored):
  - `test_generate_cv_draft.py`: CV draft generation endpoint tests
  - `test_ai_rewrite.py`: Text rewrite endpoint tests

#### Database Tests (`test_database/`)
- `test_queries.py`: Database query tests
- `test_profile_queries.py`: Profile query tests documentation (refactored)
- `test_profile_queries_save/`: Profile save and update tests (mocked, refactored into subfolder):
  - `test_save_profile.py`: save_profile function tests
  - `test_create_profile.py`: create_profile function tests
  - `test_update_profile.py`: update_profile function tests
- `test_profile_queries_get.py`: Profile retrieval tests (mocked)
- `test_profile_queries_delete.py`: Profile deletion tests (mocked)
- `test_profile_queries_integration/`: Profile CRUD integration tests (live Neo4j, refactored into subfolder):
  - `test_crud.py`: CRUD roundtrip tests
  - `test_duplicate_person_regression.py`: Duplicate Person node prevention regression tests
  - `helpers.py`: Shared helper functions (skip_if_no_neo4j, is_test_profile)

#### Service Tests (`test_services/`)
- `cover_letter_selection_tests/content_selection/`: Content selection tests (refactored):
  - `test_basic_selection.py`: Basic content selection functionality
  - `test_validation.py`: Content selection validation
  - `test_error_handling.py`: Error handling in content selection
  - `test_edge_cases.py`: Edge cases in content selection
  - `conftest.py`: Shared fixtures for content selection tests
- `pipeline_cv_assembler/`: CV assembler pipeline tests (refactored):
  - `test_assemble_cv.py`: CV assembly functionality
  - `test_apply_context_incorporation.py`: Context incorporation functionality
- `pipeline_content_incorporator/`: Content incorporator pipeline tests (refactored):
  - `test_incorporate_context.py`: Context incorporation logic
  - `test_build_incorporation.py`: Incorporation building logic
  - `test_apply_incorporation.py`: Incorporation application logic

#### CV Generator Tests (`test_cv_generator_docx/`)
- `scramble/`: Scramble utility tests (refactored):
  - `test_derive_offsets.py`: Offset derivation for scrambling
  - `test_scramble_text.py`: Text scrambling functionality
  - `test_scramble_html_text.py`: HTML-aware text scrambling
  - `test_scramble_personal_info.py`: Personal info scrambling

#### Model Tests
- `test_models.py`: Pydantic model validation tests

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

**Note**: Coverage reports are generated in `frontend/coverage/` and are ignored by git (see `.gitignore`). Coverage files include HTML reports and JSON data files.

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

### Test Cleanup Safety

**Profile Deletion Protection**: Tests implement safety mechanisms to prevent
accidental deletion of real user profiles:

1. **Integration Tests** (`backend/tests/test_database/test_profile_queries_integration/`):
   - Use `is_test_profile()` helper to verify profiles have "test" prefix before deletion
   - Only delete profiles that pass the test profile verification
   - Example: `test_duplicate_person_regression.py` checks both old and new profile
     timestamps before cleanup

**Why This Matters**: The `delete_profile()` function deletes the most recently updated
profile (by `updated_at`), which could be a real user profile if tests don't properly
isolate their test data. These safety mechanisms ensure tests only delete profiles
they created, protecting real user data.

## Writing Tests

**Backend Example**:
```python
def test_create_cv():
    cv_data = {"personal_info": {"name": "Test"}, "experience": [], "education": [], "skills": []}
    cv_id = queries.create_cv(cv_data)
    assert cv_id is not None
    # create_cv makes multiple tx.run() calls (CV, Person, Experience, Education, Skills)
    # Each call is made within a single transaction for atomicity
```

**Note**: When testing database operations that make multiple query calls (like `create_cv`), tests should account for multiple `tx.run()` invocations. The implementation uses modular functions that each make their own query call, improving maintainability while keeping operations atomic within a transaction.

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

## Test Organization and Refactoring

### Large Test File Refactoring

To improve maintainability and reduce cognitive load, large test files (>300 lines) have been refactored into smaller, modular files organized in subfolders. Each refactored file targets 135-160 lines with proper test isolation and shared fixtures.

**Refactoring Pattern**:
- Create subfolder with descriptive name under parent test directory
- Split test classes into separate files based on functionality
- Extract shared fixtures to `conftest.py` if needed
- Maintain all original test functionality and coverage
- Verify all tests pass before removing original file

### Recently Refactored Test Files

#### 1. Content Selection Tests (`backend/tests/test_services/cover_letter_selection_tests/`)
- **Original**: `content_selection_tests.py` (583 lines, 10 tests)
- **Refactored into**: `content_selection/` subfolder
- **Files**:
  - `test_basic_selection.py` (~150 lines) - Basic selection tests (Django/Node.js jobs, JSON parsing)
  - `test_validation.py` (~150 lines) - Validation tests (indices, skills, empty profile)
  - `test_error_handling.py` (~150 lines) - Error handling (invalid JSON, HTTP errors, malformed responses)
  - `test_edge_cases.py` (~133 lines) - Edge cases (case-insensitive matching, markdown JSON)
  - `conftest.py` - Shared fixtures (sample_profile, job_description_django, job_description_nodejs)

#### 2. Cover Letter API Endpoints (`backend/tests/test_api/`)
- **Original**: `test_cover_letter_endpoints.py` (473 lines, 23 tests)
- **Refactored into**: `cover_letter_endpoints/` subfolder
- **Files**:
  - `test_generate_cover_letter.py` (~100 lines) - TestGenerateCoverLetter class
  - `test_export_pdf.py` (~80 lines) - TestExportCoverLetterPDF class
  - `test_save_cover_letter.py` (~90 lines) - TestSaveCoverLetter class
  - `test_list_cover_letters.py` (~90 lines) - TestListCoverLetters class
  - `test_get_cover_letter.py` (~80 lines) - TestGetCoverLetter class
  - `test_delete_cover_letter.py` (~80 lines) - TestDeleteCoverLetter class

#### 3. CV Assembler Pipeline (`backend/tests/test_services/pipeline_cv_assembler/`)
- **Original**: `test_pipeline_cv_assembler.py` (451 lines, 11 tests)
- **Refactored into**: `pipeline_cv_assembler/` subfolder
- **Files**:
  - `test_assemble_cv.py` (~250 lines) - TestCVAssembler class (6 tests)
  - `test_apply_context_incorporation.py` (~200 lines) - TestApplyContextIncorporation class (5 tests)

#### 4. Content Incorporator Pipeline (`backend/tests/test_services/pipeline_content_incorporator/`)
- **Original**: `test_pipeline_content_incorporator.py` (418 lines, 14 tests)
- **Refactored into**: `pipeline_content_incorporator/` subfolder
- **Files**:
  - `test_incorporate_context.py` (~80 lines) - TestContentIncorporator class (2 tests)
  - `test_build_incorporation.py` (~180 lines) - TestBuildIncorporation class (6 tests)
  - `test_apply_incorporation.py` (~158 lines) - TestApplyIncorporation class (6 tests)

#### 5. Scramble Utilities (`backend/tests/test_cv_generator_docx/`)
- **Original**: `test_scramble.py` (372 lines, 32 tests)
- **Refactored into**: `scramble/` subfolder
- **Files**:
  - `test_derive_offsets.py` (~60 lines) - TestDeriveOffsets class (3 tests)
  - `test_scramble_text.py` (~120 lines) - TestScrambleText class (12 tests)
  - `test_scramble_html_text.py` (~100 lines) - TestScrambleHtmlText class (5 tests)
  - `test_scramble_personal_info.py` (~92 lines) - TestScramblePersonalInfo class (12 tests)

#### 6. Exception Handlers (`backend/tests/test_api/`)
- **Original**: `test_exception_handlers.py` (355 lines, 25 tests)
- **Refactored into**: `exception_handlers/` subfolder
- **Files**:
  - `test_field_names.py` (~120 lines) - TestBuildFriendlyFieldName class (8 tests)
  - `test_field_paths.py` (~80 lines) - TestBuildFieldPath class (5 tests)
  - `test_validation_handler.py` (~155 lines) - TestValidationExceptionHandler class (12 async tests)

#### 7. AI Endpoints (`backend/tests/test_api/`)
- **Original**: `test_ai_endpoints.py` (343 lines, 12 tests)
- **Refactored into**: `ai_endpoints/` subfolder
- **Files**:
  - `test_generate_cv_draft.py` (~200 lines) - TestGenerateCvDraft class (8 tests)
  - `test_ai_rewrite.py` (~143 lines) - TestAIRewrite class (4 tests)

### Benefits of Refactoring

- **Improved Maintainability**: Smaller files are easier to understand and modify
- **Better Test Isolation**: Related tests grouped together, reducing cognitive load
- **Faster Test Execution**: Can run specific test groups independently
- **Reduced Merge Conflicts**: Smaller files have fewer conflicts during team development
- **Enhanced Debugging**: Issues easier to locate in focused test files

### Test Execution After Refactoring

All refactored tests maintain their original functionality and can be run using the same commands:

```bash
# Run all tests in a refactored subfolder
docker-compose exec -T app pytest backend/tests/test_services/cover_letter_selection_tests/content_selection/ -v

# Run specific test file
docker-compose exec -T app pytest backend/tests/test_api/exception_handlers/test_field_names.py -v
```

## Recent Test Additions

### Backend Tests
- HTML content validation tests for `Experience.description` field
- Plain text length validation (HTML stripping)
- HTML entity handling in validation
- Profile query tests refactored into smaller, focused test files:
  - Save and update tests separated into `test_profile_queries_save/` subfolder:
    - `test_save_profile.py`: save_profile tests (142 lines)
    - `test_create_profile.py`: create_profile tests (40 lines)
    - `test_update_profile.py`: update_profile tests (52 lines)
  - Retrieval tests separated into `test_profile_queries_get.py`
  - Deletion tests separated into `test_profile_queries_delete.py`
  - Integration tests separated into `test_profile_queries_integration/` subfolder:
    - `test_crud.py`: CRUD roundtrip tests (153 lines)
    - `test_duplicate_person_regression.py`: Duplicate Person prevention regression tests (115 lines)
    - `helpers.py`: Shared helper functions (50 lines)
  - Shared test helpers and mocks in `helpers/profile_queries/mocks.py`
- Fixed test file naming conflict: Removed duplicate `test_profile_queries_integration.py` file that conflicted with `test_profile_queries_integration/` directory, resolving pytest import errors

### Frontend Tests
- RichTextarea component tests (30 tests: rendering, onChange, validation, character counting, line break preservation, HTML formatting preservation, list preservation)
- RichTextarea AI assist tests (5 tests: modal, rewrite, bullets)
- HTML stripping utility tests (`stripHtml`, `normalizeHtmlForComparison` in `app_helpers/richTextarea/htmlUtils.ts`)
- Updated component tests to reflect RichTextarea usage
- RichTextarea refactored into modular helpers (`app_helpers/richTextarea/`) - all tests pass
- ProfileManager tests refactored into smaller, focused test files:
  - Rendering tests separated from functionality tests
  - Loading, saving, deleting, and AI assist tests in separate files
  - Keyboard shortcut tests (`ProfileManager.keyboardShortcut.test.tsx`)
  - Shared test helpers and mocks in `helpers/profileManager/`
- Hash routing tests with URL encoding/decoding support
