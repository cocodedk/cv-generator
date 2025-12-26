/**
 * API cleanup functions for E2E tests
 */

import { APIRequestContext } from '@playwright/test'
import { BACKEND_URL } from './constants'

/**
 * Delete CV via API
 * @param request - Playwright API request context
 * @param cvId - CV ID to delete
 */
export async function deleteCv(request: APIRequestContext, cvId: string): Promise<void> {
  try {
    await request.delete(`${BACKEND_URL}/api/cv/${cvId}`)
  } catch (_error) {
    // Ignore errors (CV might not exist)
  }
}

/**
 * Delete profile via API
 * @param request - Playwright API request context
 */
export async function deleteProfile(request: APIRequestContext): Promise<void> {
  try {
    await request.delete(`${BACKEND_URL}/api/profile`)
  } catch (_error) {
    // Ignore errors (profile might not exist)
  }
}
