/**
 * End-to-end tests for AI CV Generation feature
 *
 * These tests verify the complete flow of generating a CV from a job description
 * using the AI feature, from opening the modal to saving the final CV.
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend running on http://localhost:5173
 * - A profile must exist in the database (created via Profile page)
 *
 * Run with: npx playwright test tests/e2e/ai-cv-generation.spec.ts
 */

import { test, expect } from '@playwright/test'
import { FRONTEND_URL } from './helpers/constants'
import { extractCvIdFromUrl } from './helpers/urlUtils'
import { CleanupManager } from './helpers/cleanupManager'
import {
  openAiGenerationModal,
  fillAiGenerationForm,
  waitForAiGeneration,
  verifyAiGenerationResults,
} from './helpers/aiGeneration'
import { createTestProfile } from './helpers/profileSetup'

test.describe.serial('AI CV Generation - End to End', () => {
  const cleanupManager = new CleanupManager()

  test.beforeEach(async ({ page, request }, testInfo) => {
    if (testInfo.title === 'should show error when profile is missing') {
      // Don't create profile for this test
    } else {
      // Create test profile before each test and track it for cleanup
      const updatedAt = await createTestProfile(request)
      if (updatedAt) {
        cleanupManager.trackTestProfile(updatedAt)
      }
    }

    await page.goto(FRONTEND_URL)
    await page.waitForLoadState('networkidle')
  })

  test.afterEach(async ({ page, request }) => {
    cleanupManager.trackCvIdFromUrl(page)
    // Clean up CVs and profile
    await cleanupManager.cleanupWithProfile(request)
  })

  test('should generate CV from job description and save it', async ({ page }) => {
    await openAiGenerationModal(page)

    const jobDescription = `We are looking for a Senior Full Stack Developer to join our team.

Requirements:
- 5+ years of experience with React and TypeScript
- Strong experience with Python and FastAPI
- Experience with Neo4j or graph databases
- Knowledge of Docker and containerization
- Experience with RESTful API design
- Strong problem-solving skills and attention to detail

Responsibilities:
- Develop and maintain web applications using React and TypeScript
- Build and maintain backend APIs using Python and FastAPI
- Design and implement database schemas
- Collaborate with cross-functional teams
- Write clean, maintainable code following best practices`

    await fillAiGenerationForm(page, {
      targetRole: 'Senior Full Stack Developer',
      jobDescription,
    })

    const generateButton = page.getByRole('button', { name: 'Generate', exact: true })
    await expect(generateButton).toBeEnabled()
    await generateButton.click()

    await waitForAiGeneration(page)
    await expect(page.getByText(/Target role:/)).toBeVisible({ timeout: 5000 })
    await verifyAiGenerationResults(page)

    const applyButton = page.getByRole('button', { name: 'Apply draft to form' })
    await expect(applyButton).toBeVisible()
    await applyButton.click()

    await expect(page.getByRole('textbox', { name: /full name/i })).not.toHaveValue('')
    await expect(page.getByRole('textbox', { name: /professional summary/i })).not.toHaveValue('')
    await expect(page.getByText(/Draft applied/i)).toBeVisible()

    const saveButton = page.getByRole('button', { name: 'Generate CV' })
    await expect(saveButton).toBeVisible()
    const printablePagePromise = page.context().waitForEvent('page').catch(() => null)
    await saveButton.click()

    await expect(page).toHaveURL(/.*#edit\/[a-f0-9-]+/, { timeout: 10000 })
    await expect(page.getByText(/CV saved/i)).toBeVisible()

    const cvId = extractCvIdFromUrl(page.url())
    if (cvId) {
      cleanupManager.trackCvId(cvId)
    }

    const printablePage = await printablePagePromise
    if (printablePage) {
      await printablePage.close().catch(() => null)
    }
  })

  test('should show error when profile is missing', async ({ page }) => {
    await page.getByRole('button', { name: 'Create CV' }).click()
    await page.getByRole('button', { name: 'Generate from JD' }).click()

    await page.getByRole('textbox', { name: 'Job description' }).fill(
      'We require React and FastAPI developers.'
    )

    await page.getByRole('button', { name: 'Generate', exact: true }).click()

    await expect(page.getByText(/Profile not found/i)).toBeVisible({ timeout: 10000 })
  })

  test('should validate job description minimum length', async ({ page }) => {
    await page.getByRole('button', { name: 'Create CV' }).click()
    await page.getByRole('button', { name: 'Generate from JD' }).click()

    await page.getByRole('textbox', { name: 'Job description' }).fill('Short')

    const generateButton = page.getByRole('button', { name: 'Generate', exact: true })
    await expect(generateButton).toBeDisabled()
    await expect(page.getByText(/minimum.*20.*characters/i)).toBeVisible()
  })

  test('should allow changing AI generation style', async ({ page }) => {
    await openAiGenerationModal(page)

    const styleSelect = page.getByRole('combobox', { name: 'Style' })
    await expect(styleSelect).toHaveValue('select_and_reorder')
    await styleSelect.selectOption('rewrite_bullets')

    await fillAiGenerationForm(page, {
      jobDescription:
        'We need a developer with React and FastAPI experience. Must have Docker knowledge.',
    })

    await page.getByRole('button', { name: 'Generate', exact: true }).click()

    await waitForAiGeneration(page)
    await verifyAiGenerationResults(page)
  })

  test('should verify CV appears in My CVs list after generation', async ({ page }) => {
    await openAiGenerationModal(page)

    await fillAiGenerationForm(page, {
      targetRole: 'Test Role',
      jobDescription: 'We need a developer with React and FastAPI experience.',
    })

    await page.getByRole('button', { name: 'Generate', exact: true }).click()

    await waitForAiGeneration(page)
    await expect(page.getByText(/Target role:/)).toBeVisible({ timeout: 10000 })

    await page.getByRole('button', { name: 'Apply draft to form' }).click()
    const printablePagePromise = page.context().waitForEvent('page').catch(() => null)
    await page.getByRole('button', { name: 'Generate CV' }).click()
    const printablePage = await printablePagePromise
    if (printablePage) {
      await printablePage.close().catch(() => null)
    }

    await expect(page).toHaveURL(/.*#edit\/[a-f0-9-]+/, { timeout: 10000 })

    const cvId = extractCvIdFromUrl(page.url())
    if (cvId) {
      cleanupManager.trackCvId(cvId)
    }

    await page.getByRole('button', { name: 'My CVs' }).click()
    await expect(page).toHaveURL(/.*#list/)
    await expect(page.getByRole('heading', { name: /My CVs/ })).toBeVisible()

    const cvCards = page.locator('[class*="CV"]').or(page.getByText(/Created:/))
    await expect(cvCards.first()).toBeVisible()
  })
})
