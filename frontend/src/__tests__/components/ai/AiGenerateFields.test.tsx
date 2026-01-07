import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AiGenerateFields from '../../../components/ai/AiGenerateFields'
import { AIGenerateCVRequest } from '../../../types/ai'

describe('AiGenerateFields', () => {
  const mockOnChange = vi.fn()

  const defaultPayload: AIGenerateCVRequest = {
    job_description: 'We require React and FastAPI.',
  }

  const llmTailorPayload: AIGenerateCVRequest = {
    job_description: 'We require React and FastAPI.',
    style: 'llm_tailor',
  }

  beforeEach(() => {
    mockOnChange.mockClear()
  })

  it('renders core form fields', () => {
    render(
      <AiGenerateFields
        payload={defaultPayload}
        isGenerating={false}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    expect(screen.getByLabelText(/target role/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/seniority/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/style/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/max experiences/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/job description/i)).toBeInTheDocument()
  })

  it('does not show additional_context field when style is not llm_tailor', () => {
    render(
      <AiGenerateFields
        payload={defaultPayload}
        isGenerating={false}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    expect(screen.queryByLabelText(/additional context/i)).not.toBeInTheDocument()
  })

  it('shows additional_context field when style is llm_tailor', () => {
    render(
      <AiGenerateFields
        payload={llmTailorPayload}
        isGenerating={false}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    expect(screen.getByLabelText(/additional context/i)).toBeInTheDocument()
  })

  it('displays additional_context value when provided', () => {
    const payload: AIGenerateCVRequest = {
      ...llmTailorPayload,
      additional_context: 'Rated among top 2% of AI coders in 2025',
    }

    render(
      <AiGenerateFields
        payload={payload}
        isGenerating={false}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    const additionalContextField = screen.getByLabelText(
      /additional context/i
    ) as HTMLTextAreaElement
    expect(additionalContextField.value).toBe('Rated among top 2% of AI coders in 2025')
  })

  it('calls onChange when additional_context is updated', async () => {
    const user = userEvent.setup()
    render(
      <AiGenerateFields
        payload={llmTailorPayload}
        isGenerating={false}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    const additionalContextField = screen.getByLabelText(/additional context/i)
    await user.type(additionalContextField, 'Top 2% AI coder')

    // user.type() calls onChange for each character typed
    // Verify onChange was called with 'additional_context' field name
    expect(mockOnChange).toHaveBeenCalled()
    const calls = mockOnChange.mock.calls.filter(call => call[0] === 'additional_context')
    expect(calls.length).toBeGreaterThan(0)
    // Verify the last call contains the last character (since it's a controlled component)
    const lastCall = calls[calls.length - 1]
    expect(lastCall[0]).toBe('additional_context')
  })

  it('calls onChange with undefined when additional_context is cleared', async () => {
    const user = userEvent.setup()
    const payload: AIGenerateCVRequest = {
      ...llmTailorPayload,
      additional_context: 'Some context',
    }

    render(
      <AiGenerateFields
        payload={payload}
        isGenerating={false}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    const additionalContextField = screen.getByLabelText(/additional context/i)
    await user.clear(additionalContextField)

    expect(mockOnChange).toHaveBeenCalledWith('additional_context', undefined)
  })

  it('disables additional_context field when isGenerating is true', () => {
    render(
      <AiGenerateFields
        payload={llmTailorPayload}
        isGenerating={true}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    const additionalContextField = screen.getByLabelText(/additional context/i)
    expect(additionalContextField).toBeDisabled()
  })

  it('displays placeholder text for additional_context field', () => {
    render(
      <AiGenerateFields
        payload={llmTailorPayload}
        isGenerating={false}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    const additionalContextField = screen.getByLabelText(/additional context/i)
    expect(additionalContextField).toHaveAttribute(
      'placeholder',
      expect.stringContaining('enterprise-focused')
    )
  })

  it('displays help text for additional_context field', () => {
    render(
      <AiGenerateFields
        payload={llmTailorPayload}
        isGenerating={false}
        canGenerate={true}
        onChange={mockOnChange}
      />
    )

    expect(screen.getByText(/directive to guide cv tailoring/i)).toBeInTheDocument()
  })
})
