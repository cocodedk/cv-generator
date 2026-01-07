import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '@testing-library/react'
import CoverLetterModal from '../../../components/cover-letter/CoverLetterModal'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as any

describe('CoverLetterModal', () => {
  const mockOnClose = vi.fn()
  const mockOnError = vi.fn()
  const mockOnSuccess = vi.fn()
  const mockSetLoading = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the modal with form fields', () => {
    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

    expect(screen.getByText('Generate Cover Letter')).toBeInTheDocument()
    expect(screen.getByLabelText(/company name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/job description/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/tone/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/llm instructions/i)).toBeInTheDocument()
  })

  it('allows user to fill in form fields', async () => {
    const user = userEvent.setup()
    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

    const companyInput = screen.getByLabelText(/company name/i)
    const jdTextarea = screen.getByLabelText(/job description/i)

    await act(async () => {
      await user.type(companyInput, 'Tech Corp')
      await user.type(jdTextarea, 'We are looking for a Senior Developer with Python experience.')
    })

    expect(companyInput).toHaveValue('Tech Corp')
    expect(jdTextarea).toHaveValue('We are looking for a Senior Developer with Python experience.')
  })

  it('disables generate button when form is invalid', async () => {
    const user = userEvent.setup()
    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

    const generateButton = screen.getByRole('button', { name: /^generate$/i })
    expect(generateButton).toBeDisabled()

    const companyInput = screen.getByLabelText(/company name/i)
    await act(async () => {
      await user.type(companyInput, 'Tech Corp')
    })

    // Still disabled because job description is too short
    expect(generateButton).toBeDisabled()
  })

  it('enables generate button when form is valid', async () => {
    const user = userEvent.setup()
    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

    const companyInput = screen.getByLabelText(/company name/i)
    const jdTextarea = screen.getByLabelText(/job description/i)

    await act(async () => {
      await user.type(companyInput, 'Tech Corp')
      await user.type(jdTextarea, 'We are looking for a Senior Developer with Python experience.')
    })

    const generateButton = screen.getByRole('button', { name: /^generate$/i })
    expect(generateButton).not.toBeDisabled()
  })

  it('generates cover letter and shows preview', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({
      data: {
        cover_letter_html: '<div>Cover letter HTML</div>',
        cover_letter_text: 'Cover letter text',
        highlights_used: ['Highlight 1', 'Highlight 2'],
      },
    })

    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

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
      expect(screen.getByRole('button', { name: /download pdf/i })).toBeInTheDocument()
    })
  })

  it('handles generation error', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockRejectedValue({
      response: {
        data: { detail: 'LLM is not configured' },
      },
    })

    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

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
      expect(mockOnError).toHaveBeenCalled()
      const errorCall = mockOnError.mock.calls[0][0]
      expect(errorCall).toMatch(/LLM|Failed to generate/i)
    })
  })

  it('closes modal when cancel button is clicked', async () => {
    const user = userEvent.setup()
    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await act(async () => {
      await user.click(cancelButton)
    })

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('pre-fills job description when provided', () => {
    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
        initialJobDescription="Pre-filled job description"
      />
    )

    const jdTextarea = screen.getByLabelText(/job description/i)
    expect(jdTextarea).toHaveValue('Pre-filled job description')
  })

  it('shows regenerate button after generating cover letter', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({
      data: {
        cover_letter_html: '<div>Cover letter HTML</div>',
        cover_letter_text: 'Cover letter text',
        highlights_used: [],
        selected_experiences: [],
        selected_skills: [],
      },
    })

    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

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
      // Should have regenerate buttons (both in preview and footer)
      const regenerateButtons = screen.getAllByRole('button', { name: /regenerate/i })
      expect(regenerateButtons.length).toBeGreaterThan(0)
      // Generate button should be gone
      expect(screen.queryByRole('button', { name: /^generate$/i })).not.toBeInTheDocument()
    })
  })

  it('regenerates cover letter when regenerate button is clicked', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({
      data: {
        cover_letter_html: '<div>Cover letter HTML</div>',
        cover_letter_text: 'Cover letter text',
        highlights_used: [],
        selected_experiences: [],
        selected_skills: [],
      },
    })

    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

    const companyInput = screen.getByLabelText(/company name/i)
    const jdTextarea = screen.getByLabelText(/job description/i)

    await act(async () => {
      await user.type(companyInput, 'Tech Corp')
      await user.type(jdTextarea, 'We are looking for a Senior Developer with Python experience.')
    })

    // Generate first time
    const generateButton = screen.getByRole('button', { name: /^generate$/i })
    await act(async () => {
      await user.click(generateButton)
    })

    await waitFor(() => {
      const regenerateButtons = screen.getAllByRole('button', { name: /regenerate/i })
      expect(regenerateButtons.length).toBeGreaterThan(0)
    })

    // Regenerate using the first regenerate button (footer button)
    const regenerateButtons = screen.getAllByRole('button', { name: /regenerate/i })
    await act(async () => {
      await user.click(regenerateButtons[0])
    })

    await waitFor(() => {
      // Should have been called twice (generate + regenerate)
      expect(mockedAxios.post).toHaveBeenCalledTimes(2)
    })
  })

  it('saves cover letter successfully', async () => {
    const user = userEvent.setup()
    mockedAxios.post
      .mockResolvedValueOnce({
        data: {
          cover_letter_html: '<div>Cover letter HTML</div>',
          cover_letter_text: 'Cover letter text',
          highlights_used: [],
          selected_experiences: [],
          selected_skills: [],
        },
      })
      .mockResolvedValueOnce({
        data: { success: true },
      })

    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

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
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument()
    })

    const saveButton = screen.getByRole('button', { name: /save/i })
    await act(async () => {
      await user.click(saveButton)
    })

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('Cover letter saved successfully!')
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/cover-letters',
        expect.objectContaining({
          cover_letter_response: expect.objectContaining({
            cover_letter_html: '<div>Cover letter HTML</div>',
          }),
          request_data: expect.objectContaining({
            company_name: 'Tech Corp',
          }),
        })
      )
    })
  })

  it('handles save error', async () => {
    const user = userEvent.setup()
    mockedAxios.post
      .mockResolvedValueOnce({
        data: {
          cover_letter_html: '<div>Cover letter HTML</div>',
          cover_letter_text: 'Cover letter text',
          highlights_used: [],
          selected_experiences: [],
          selected_skills: [],
        },
      })
      .mockRejectedValueOnce({
        response: {
          data: { detail: 'Failed to save' },
        },
      })

    render(
      <CoverLetterModal
        onClose={mockOnClose}
        onError={mockOnError}
        onSuccess={mockOnSuccess}
        setLoading={mockSetLoading}
      />
    )

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
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument()
    })

    const saveButton = screen.getByRole('button', { name: /save/i })
    await act(async () => {
      await user.click(saveButton)
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to save')
    })
  })
})
