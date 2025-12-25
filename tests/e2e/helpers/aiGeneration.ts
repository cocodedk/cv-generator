/**
 * AI generation test helpers
 */

import { Page, expect } from '@playwright/test'

/**
 * Wait for AI generation to complete
 * Handles success, profile not found, and generation failure cases
 * @param page - Playwright page object
 * @param timeout - Timeout in milliseconds (default: 15000)
 */
export async function waitForAiGeneration(
  page: Page,
  timeout: number = 15000
): Promise<void> {
  await Promise.any([
    page.waitForSelector('text=/Selected.*experience.*and.*skill.*for JD match/i', { timeout }),
    page.waitForSelector('text=/Profile not found/i', { timeout }),
    page.waitForSelector('text=/Failed to generate/i', { timeout }),
  ]).catch(() => null)

  // Check if there's an error
  const errorText = await page.textContent('body')
  if (errorText?.includes('Profile not found') || errorText?.includes('Failed to generate')) {
    throw new Error('AI generation failed - profile may not exist. Please create a profile first.')
  }
}

/**
 * Verify AI generation results are displayed
 * @param page - Playwright page object
 */
export async function verifyAiGenerationResults(page: Page): Promise<void> {
  await expect(
    page.getByText(/Selected.*experience.*and.*skill.*for JD match/i)
  ).toBeVisible({ timeout: 5000 })
  await expect(
    page.locator('.bg-gray-50, .bg-amber-50').getByText('Summary').first()
  ).toBeVisible()
  // Questions may not always appear (only if highlights don't have numbers)
  const questionsPanel = page.locator('.bg-amber-50').getByText('Questions').first()
  const questionsVisible = await questionsPanel.isVisible().catch(() => false)
  if (questionsVisible) {
    await expect(questionsPanel).toBeVisible()
  }
}

/**
 * Fill AI generation form
 * @param page - Playwright page object
 * @param options - Form options
 */
export async function fillAiGenerationForm(
  page: Page,
  options: {
    targetRole?: string
    jobDescription: string
    style?: string
  }
): Promise<void> {
  if (options.targetRole) {
    await page.getByRole('textbox', { name: 'Target role (optional)' }).fill(options.targetRole)
  }

  await page.getByRole('textbox', { name: 'Job description' }).fill(options.jobDescription)

  if (options.style) {
    const styleSelect = page.getByRole('combobox', { name: 'Style' })
    await styleSelect.selectOption(options.style)
  }
}

/**
 * Open AI generation modal
 * @param page - Playwright page object
 */
export async function openAiGenerationModal(page: Page): Promise<void> {
  await page.getByRole('button', { name: 'Create CV' }).click()
  await page.getByRole('button', { name: 'Generate from JD' }).click()
  await expect(
    page.getByRole('heading', { name: 'Generate CV from Job Description' })
  ).toBeVisible()
}
