import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { renderCVForm } from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm - Cover Letter', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('shows cover letter button in header', () => {
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    expect(screen.getByRole('button', { name: /cover letter/i })).toBeInTheDocument()
  })

  it('opens cover letter modal when button is clicked', async () => {
    const user = userEvent.setup()
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    const coverLetterButton = screen.getByRole('button', { name: /cover letter/i })
    await act(async () => {
      await user.click(coverLetterButton)
    })

    await waitFor(() => {
      expect(screen.getByText('Generate Cover Letter')).toBeInTheDocument()
    })
  })

  it('generates cover letter and shows preview', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({
      data: {
        cover_letter_html: '<div>Cover letter HTML</div>',
        cover_letter_text: 'Cover letter text',
        highlights_used: ['Highlight 1'],
        selected_experiences: ['Software Engineer'],
        selected_skills: ['Python', 'Django'],
      },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    const coverLetterButton = screen.getByRole('button', { name: /cover letter/i })
    await act(async () => {
      await user.click(coverLetterButton)
    })

    await waitFor(() => {
      expect(screen.getByText('Generate Cover Letter')).toBeInTheDocument()
    })

    const companyInput = screen.getByLabelText(/company name/i)
    const jdTextarea = screen.getByLabelText(/job description/i)

    await act(async () => {
      await user.type(companyInput, 'Tech Corp')
      await user.type(jdTextarea, 'We are looking for a Senior Developer with Python experience.')
    })

    const generateButton = screen.getByRole('button', { name: /^generate$/i })
    await act(async () => {
      await user.click(generateButton)
    })

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/ai/generate-cover-letter',
        expect.objectContaining({
          company_name: 'Tech Corp',
          job_description: expect.stringContaining('Senior Developer'),
        })
      )
    })

    await waitFor(() => {
      expect(screen.getByText(/preview/i)).toBeInTheDocument()
    })
  })

  it('closes cover letter modal when cancel is clicked', async () => {
    const user = userEvent.setup()
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    const coverLetterButton = screen.getByRole('button', { name: /cover letter/i })
    await act(async () => {
      await user.click(coverLetterButton)
    })

    await waitFor(() => {
      expect(screen.getByText('Generate Cover Letter')).toBeInTheDocument()
    })

    // Find cancel button within the modal (more specific query)
    const modal = screen.getByText('Generate Cover Letter').closest('div[class*="max-w-3xl"]')
    const cancelButtons = screen.getAllByRole('button', { name: /cancel/i })
    const modalCancelButton = cancelButtons.find(btn => modal?.contains(btn)) || cancelButtons[0]

    await act(async () => {
      await user.click(modalCancelButton!)
    })

    await waitFor(() => {
      expect(screen.queryByText('Generate Cover Letter')).not.toBeInTheDocument()
    })
  })
})
