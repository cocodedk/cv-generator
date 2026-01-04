import axios from 'axios'
import {
  CoverLetterRequest,
  CoverLetterResponse,
  CoverLetterPDFRequest,
} from '../types/coverLetter'

export async function generateCoverLetter(
  payload: CoverLetterRequest
): Promise<CoverLetterResponse> {
  const response = await axios.post<CoverLetterResponse>('/api/ai/generate-cover-letter', payload)
  return response.data
}

export async function downloadCoverLetterPDF(html: string): Promise<void> {
  const payload: CoverLetterPDFRequest = { html }

  try {
    const response = await axios.post('/api/ai/cover-letter/pdf', payload, {
      responseType: 'blob',
    })

    // Create download link
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = 'cover_letter.pdf'
    document.body.appendChild(link)
    link.click()

    // Clean up
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  } catch (error: any) {
    // Handle blob error responses
    if (error.response?.data instanceof Blob) {
      try {
        const text = await error.response.data.text()
        const json = JSON.parse(text)
        throw new Error(json.detail || 'Failed to download PDF')
      } catch {
        throw new Error('Failed to download PDF')
      }
    }
    throw new Error(error.response?.data?.detail || error.message || 'Failed to download PDF')
  }
}
