import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { renderCVForm, clickGenerateFromJdButton } from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm - AI Draft', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('generates a draft from job description and applies it to the form', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({
      data: {
        draft_cv: {
          personal_info: { name: 'AI Draft Name' },
          experience: [],
          education: [],
          skills: [],
          theme: 'classic',
        },
        warnings: [],
        questions: [],
        summary: ['Selected 0 experience(s) and 0 skill(s) for JD match.'],
        evidence_map: null,
      },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickGenerateFromJdButton()

    const jdTextarea = await screen.findByLabelText(/job description/i)
    await act(async () => {
      await user.type(
        jdTextarea,
        'We require React and FastAPI. You will build web features and improve reliability.'
      )
    })

    const generateButton = screen.getByRole('button', { name: /^generate$/i })
    await act(async () => {
      await user.click(generateButton)
    })

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/ai/generate-cv',
        expect.objectContaining({
          job_description: expect.stringContaining('We require React and FastAPI'),
        })
      )
    })

    await screen.findByText(/selected 0 experience/i)

    const applyButton = screen.getByRole('button', { name: /apply draft to form/i })
    await act(async () => {
      await user.click(applyButton)
    })

    const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
    expect(nameInput.value).toBe('AI Draft Name')
    expect(mockOnSuccess).toHaveBeenCalledWith('Draft applied. Review and save when ready.')
  })

  it('includes additional_context in the API request when provided with llm_tailor style', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({
      data: {
        draft_cv: {
          personal_info: { name: 'AI Draft Name' },
          experience: [],
          education: [],
          skills: [],
          theme: 'classic',
        },
        warnings: [],
        questions: [],
        summary: ['Selected 0 experience(s) and 0 skill(s) for JD match.'],
        evidence_map: null,
      },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickGenerateFromJdButton()

    // Select llm_tailor style to enable additional_context field
    const styleSelect = await screen.findByLabelText(/style/i)
    await act(async () => {
      await user.selectOptions(styleSelect, 'llm_tailor')
    })

    const jdTextarea = await screen.findByLabelText(/job description/i)
    await act(async () => {
      await user.type(
        jdTextarea,
        'We require React and FastAPI. You will build web features and improve reliability.'
      )
    })

    const additionalContextTextarea = await screen.findByLabelText(/additional context/i)
    await act(async () => {
      await user.type(additionalContextTextarea, 'Rated among top 2% of AI coders in 2025')
    })

    const generateButton = screen.getByRole('button', { name: /^generate$/i })
    await act(async () => {
      await user.click(generateButton)
    })

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/ai/generate-cv',
        expect.objectContaining({
          job_description: expect.stringContaining('We require React and FastAPI'),
          style: 'llm_tailor',
          additional_context: 'Rated among top 2% of AI coders in 2025',
        })
      )
    })
  })

  it('does not include additional_context in API request when empty', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({
      data: {
        draft_cv: {
          personal_info: { name: 'AI Draft Name' },
          experience: [],
          education: [],
          skills: [],
          theme: 'classic',
        },
        warnings: [],
        questions: [],
        summary: ['Selected 0 experience(s) and 0 skill(s) for JD match.'],
        evidence_map: null,
      },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickGenerateFromJdButton()

    const jdTextarea = await screen.findByLabelText(/job description/i)
    await act(async () => {
      await user.type(
        jdTextarea,
        'We require React and FastAPI. You will build web features and improve reliability.'
      )
    })

    const generateButton = screen.getByRole('button', { name: /^generate$/i })
    await act(async () => {
      await user.click(generateButton)
    })

    await waitFor(() => {
      const callArgs = mockedAxios.post.mock.calls[0]
      const requestPayload = callArgs[1]
      // additional_context should be undefined or not present when empty
      expect(requestPayload.job_description).toBeDefined()
      expect(requestPayload.additional_context).toBeUndefined()
    })
  })

  it('renders additional_context textarea field when llm_tailor style is selected', async () => {
    const user = userEvent.setup()
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickGenerateFromJdButton()

    // additional_context field should not be visible by default
    expect(screen.queryByLabelText(/additional context/i)).not.toBeInTheDocument()

    // Select llm_tailor style
    const styleSelect = await screen.findByLabelText(/style/i)
    await act(async () => {
      await user.selectOptions(styleSelect, 'llm_tailor')
    })

    // Now additional_context field should be visible
    const additionalContextField = await screen.findByLabelText(/additional context/i)
    expect(additionalContextField).toBeInTheDocument()
    expect(additionalContextField).toHaveAttribute('placeholder', expect.stringContaining('top 2%'))
  })
})
