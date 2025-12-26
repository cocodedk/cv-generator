/**
 * URL utility functions for E2E tests
 */

/**
 * Extract CV ID from URL hash pattern like #edit/{cv_id}
 * @param url - The URL to extract CV ID from
 * @returns CV ID if found, null otherwise
 */
export function extractCvIdFromUrl(url: string): string | null {
  const match = url.match(/#edit\/([a-f0-9-]+)/i)
  return match ? match[1] : null
}
