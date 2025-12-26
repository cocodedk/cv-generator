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
 * Delete profile via API (deletes latest profile - use with caution!)
 * @param request - Playwright API request context
 */
export async function deleteProfile(request: APIRequestContext): Promise<void> {
  try {
    await request.delete(`${BACKEND_URL}/api/profile`, {
      headers: { 'X-Confirm-Delete-Profile': 'true' },
    })
  } catch (_error) {
    // Ignore errors (profile might not exist)
  }
}

/**
 * Delete a specific profile by its updated_at timestamp
 * @param request - Playwright API request context
 * @param updatedAt - Profile's updated_at timestamp
 */
export async function deleteProfileByUpdatedAt(
  request: APIRequestContext,
  updatedAt: string
): Promise<void> {
  try {
    await request.delete(`${BACKEND_URL}/api/profile/${updatedAt}`, {
      headers: { 'X-Confirm-Delete-Profile': 'true' },
    })
  } catch (_error) {
    // Ignore errors (profile might not exist)
  }
}
