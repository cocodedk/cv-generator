import axios from 'axios'
import {
  CoverLetterRequest,
  CoverLetterResponse,
  CoverLetterPDFRequest,
  CoverLetterSaveRequest,
  CoverLetterListResponse,
  CoverLetterData,
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

export async function saveCoverLetter(
  coverLetterResponse: CoverLetterResponse,
  requestData: CoverLetterRequest
): Promise<{ cover_letter_id: string; status: string }> {
  const payload: CoverLetterSaveRequest = {
    cover_letter_response: coverLetterResponse,
    request_data: requestData,
  }
  const response = await axios.post('/api/cover-letters', payload)
  return response.data
}

export async function listCoverLetters(
  limit = 50,
  offset = 0,
  search?: string
): Promise<CoverLetterListResponse> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  })
  if (search) params.append('search', search)

  const response = await axios.get<CoverLetterListResponse>(`/api/cover-letters?${params}`)
  return response.data
}

export async function getCoverLetter(coverLetterId: string): Promise<CoverLetterData> {
  const response = await axios.get<CoverLetterData>(`/api/cover-letters/${coverLetterId}`)
  return response.data
}

export async function deleteCoverLetter(coverLetterId: string): Promise<void> {
  await axios.delete(`/api/cover-letters/${coverLetterId}`)
}
