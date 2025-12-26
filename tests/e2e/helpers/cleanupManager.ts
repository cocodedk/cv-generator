/**
 * Cleanup manager for E2E tests
 * Tracks and cleans up CVs and profiles created during tests
 */

import { Page, APIRequestContext } from '@playwright/test'
import { extractCvIdFromUrl } from './urlUtils'
import { deleteCv, deleteProfileByUpdatedAt } from './apiCleanup'

export class CleanupManager {
  private createdCvIds: string[] = []
  private testProfileUpdatedAt: string | null = null

  /**
   * Track a CV ID for cleanup
   * @param cvId - CV ID to track
   */
  trackCvId(cvId: string): void {
    if (cvId && !this.createdCvIds.includes(cvId)) {
      this.createdCvIds.push(cvId)
    }
  }

  /**
   * Extract and track CV ID from current page URL
   * @param page - Playwright page object
   */
  trackCvIdFromUrl(page: Page): void {
    const currentUrl = page.url()
    const cvId = extractCvIdFromUrl(currentUrl)
    if (cvId) {
      this.trackCvId(cvId)
    }
  }

  /**
   * Clean up all tracked CVs
   * @param request - Playwright API request context
   */
  async cleanup(request: APIRequestContext): Promise<void> {
    // Clean up all created CVs
    for (const id of this.createdCvIds) {
      await deleteCv(request, id)
    }
    this.createdCvIds.length = 0
  }

  /**
   * Track the test profile's updated_at timestamp for safe cleanup
   * @param updatedAt - Profile's updated_at timestamp
   */
  trackTestProfile(updatedAt: string): void {
    this.testProfileUpdatedAt = updatedAt
  }

  /**
   * Clean up all tracked CVs and the tracked test profile
   * @param request - Playwright API request context
   */
  async cleanupWithProfile(request: APIRequestContext): Promise<void> {
    await this.cleanup(request)
    // Only delete the specific test profile we tracked, not just any profile
    if (this.testProfileUpdatedAt) {
      await deleteProfileByUpdatedAt(request, this.testProfileUpdatedAt)
      this.testProfileUpdatedAt = null
    }
  }

  /**
   * Reset the cleanup manager (clear tracked CVs and profile)
   */
  reset(): void {
    this.createdCvIds.length = 0
    this.testProfileUpdatedAt = null
  }
}
