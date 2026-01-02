/**
 * PDF download helper function.
 *
 * Downloads a PDF file for a given CV ID by calling the PDF export API endpoint.
 * Handles blob response and triggers browser download.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export interface PdfDownloadOptions {
  theme?: string
  layout?: string
}

/**
 * Download PDF for a CV.
 *
 * @param cvId - The CV ID to generate PDF for
 * @param options - Optional theme and layout overrides
 * @throws Error if PDF generation fails
 */
export const downloadPdf = async (cvId: string, options?: PdfDownloadOptions): Promise<void> => {
  // Build URL with optional query parameters
  const params = new URLSearchParams()
  if (options?.theme) {
    params.append('theme', options.theme)
  }
  if (options?.layout) {
    params.append('layout', options.layout)
  }

  const url = `${API_BASE_URL}/api/cv/${cvId}/export-pdf/long${
    params.toString() ? `?${params.toString()}` : ''
  }`

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      // Try to get error message from response
      let errorMessage = `PDF generation failed: ${response.statusText}`
      try {
        const errorData = await response.json()
        if (errorData.detail) {
          errorMessage = errorData.detail
        }
      } catch {
        // If JSON parsing fails, use default message
      }

      // Handle specific status codes
      if (response.status === 404) {
        throw new Error('CV not found')
      } else if (response.status === 429) {
        throw new Error('Too many requests. Please wait a moment.')
      } else if (response.status === 500) {
        throw new Error(errorMessage || 'PDF generation service unavailable')
      }

      throw new Error(errorMessage)
    }

    // Get PDF as blob
    const blob = await response.blob()

    // Create download link
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `cv_${cvId.slice(0, 8)}_long.pdf`
    document.body.appendChild(link)
    link.click()

    // Clean up
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  } catch (error) {
    // Re-throw with more context if it's not already an Error
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Failed to download PDF. Please try again.')
  }
}
