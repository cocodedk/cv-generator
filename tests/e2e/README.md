# End-to-End Tests

E2E tests for the CV Generator application using Playwright.

## Prerequisites

1. Install Playwright:
```bash
npm install -D @playwright/test
npx playwright install
```

2. Ensure the application is running:
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:5173`

3. A profile must exist in the database (create one via the Profile page)

## Running Tests

Run all E2E tests:
```bash
npx playwright test
```

Run specific test file:
```bash
npx playwright test tests/e2e/ai-cv-generation.spec.ts
```

Run in headed mode (see browser):
```bash
npx playwright test --headed
```

Run in debug mode:
```bash
npx playwright test --debug
```

## Test Files

- `ai-cv-generation.spec.ts` - Tests for AI CV generation feature end-to-end flow

## Test Helpers

The E2E tests use a modular helper structure located in `tests/e2e/helpers/`:

- `constants.ts` - Test constants (URLs, timeouts, etc.)
- `urlUtils.ts` - URL parsing utilities (e.g., extracting CV IDs from URLs)
- `apiCleanup.ts` - API cleanup functions for deleting CVs and profiles
- `cleanupManager.ts` - Cleanup manager class for tracking and cleaning up test resources
- `aiGeneration.ts` - AI generation test helpers (form filling, waiting for results, etc.)

These helpers promote code reuse and make tests more maintainable.

## Test Coverage

### AI CV Generation Tests

1. **Full flow test**: Generates CV from job description and saves it
   - Opens AI generation modal
   - Fills in job description
   - Generates draft
   - Applies draft to form
   - Saves CV
   - Verifies CV appears in list

2. **Error handling**: Tests error when profile is missing

3. **Validation**: Tests job description minimum length validation

4. **Style options**: Tests different AI generation styles

5. **CV listing**: Verifies generated CV appears in My CVs list

## Configuration

Create `playwright.config.ts` in the project root:

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev:full',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```
