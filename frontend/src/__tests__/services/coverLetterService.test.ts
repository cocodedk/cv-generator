import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { generateCoverLetter, downloadCoverLetterPDF } from '../../services/coverLetterService'

vi.mock('axios')
const mockedAxios = axios as any

describe('coverLetterService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('generateCoverLetter', () => {
    it('calls the API and returns cover letter response', async () => {
      const mockResponse = {
        cover_letter_html: '<div>Cover letter HTML</div>',
        cover_letter_text: 'Cover letter text',
        highlights_used: ['Highlight 1'],
        selected_experiences: ['Software Engineer'],
        selected_skills: ['Python', 'Django'],
      }

      mockedAxios.post.mockResolvedValue({ data: mockResponse })

      const request = {
        job_description: 'We need a developer.',
        company_name: 'Tech Corp',
        tone: 'professional' as const,
      }

      const result = await generateCoverLetter(request)

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/ai/generate-cover-letter', request)
      expect(result).toEqual(mockResponse)
    })

    it('passes LLM instructions through to the API', async () => {
      const mockResponse = {
        cover_letter_html: '<div>Cover letter HTML</div>',
        cover_letter_text: 'Cover letter text',
        highlights_used: [],
        selected_experiences: [],
        selected_skills: [],
      }

      mockedAxios.post.mockResolvedValue({ data: mockResponse })

      const request = {
        job_description: 'We need a developer.',
        company_name: 'Tech Corp',
        tone: 'professional' as const,
        llm_instructions: 'Write in Spanish and keep it under 200 words',
      }

      await generateCoverLetter(request)

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/ai/generate-cover-letter', request)
    })

    it('handles API errors', async () => {
      mockedAxios.post.mockRejectedValue({
        response: {
          data: { detail: 'LLM is not configured' },
        },
      })

      const request = {
        job_description: 'We need a developer.',
        company_name: 'Tech Corp',
      }

      await expect(generateCoverLetter(request)).rejects.toThrow()
    })
  })

  describe('downloadCoverLetterPDF', () => {
    beforeEach(() => {
      // Mock DOM methods
      global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
      global.URL.revokeObjectURL = vi.fn()
      global.document.createElement = vi.fn(() => {
        const link = {
          href: '',
          download: '',
          click: vi.fn(),
        } as any
        return link
      })
      global.document.body.appendChild = vi.fn()
      global.document.body.removeChild = vi.fn()
    })

    it('downloads PDF successfully', async () => {
      const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' })
      mockedAxios.post.mockResolvedValue({ data: mockBlob })

      await downloadCoverLetterPDF('<html>Cover letter</html>')

      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/ai/cover-letter/pdf',
        { html: '<html>Cover letter</html>' },
        { responseType: 'blob' }
      )
      expect(global.URL.createObjectURL).toHaveBeenCalled()
    })

    it('handles blob error responses', async () => {
      // Create a mock blob-like object with text() method
      const mockBlob = {
        text: vi.fn().mockResolvedValue('{"detail": "PDF generation failed"}'),
      }

      // Make it pass instanceof Blob check
      Object.setPrototypeOf(mockBlob, Blob.prototype)

      mockedAxios.post.mockRejectedValue({
        response: {
          data: mockBlob,
        },
      })

      await expect(downloadCoverLetterPDF('<html>Cover letter</html>')).rejects.toThrow()
    })

    it('handles non-blob error responses', async () => {
      mockedAxios.post.mockRejectedValue({
        response: {
          data: { detail: 'Server error' },
        },
      })

      await expect(downloadCoverLetterPDF('<html>Cover letter</html>')).rejects.toThrow(
        'Server error'
      )
    })
  })
})
