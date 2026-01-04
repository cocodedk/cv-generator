import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AiGeneratePanels from '../../../components/ai/AiGeneratePanels'
import { AIGenerateCVResponse } from '../../../types/ai'

describe('AiGeneratePanels', () => {
  const mockDraftCv = {
    personal_info: { name: 'Test User' },
    experience: [],
    education: [],
    skills: [],
    theme: 'classic',
  }

  const mockOnRegenerateWithAnswers = vi.fn()

  beforeEach(() => {
    mockOnRegenerateWithAnswers.mockClear()
  })

  it('renders summary when present', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [],
      summary: ['Selected 2 experience(s) and 5 skill(s) for JD match.'],
      evidence_map: null,
    }

    render(<AiGeneratePanels result={result} />)

    expect(screen.getByText('Summary')).toBeInTheDocument()
    expect(screen.getByText(/selected 2 experience/i)).toBeInTheDocument()
  })

  it('does not render summary when empty', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [],
      summary: [],
      evidence_map: null,
    }

    render(<AiGeneratePanels result={result} />)

    expect(screen.queryByText('Summary')).not.toBeInTheDocument()
  })

  it('renders questions when present', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [
        'Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?',
      ],
      summary: [],
      evidence_map: null,
    }

    render(<AiGeneratePanels result={result} />)

    expect(screen.getByText('Questions')).toBeInTheDocument()
    expect(screen.getByText(/any measurable outcomes/i)).toBeInTheDocument()
  })

  it('does not render questions section when empty', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [],
      summary: [],
      evidence_map: null,
    }

    render(<AiGeneratePanels result={result} />)

    expect(screen.queryByText('Questions')).not.toBeInTheDocument()
  })

  it('shows textarea and regenerate button when questions are present and callback is provided', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [
        'Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?',
      ],
      summary: [],
      evidence_map: null,
    }

    render(
      <AiGeneratePanels result={result} onRegenerateWithAnswers={mockOnRegenerateWithAnswers} />
    )

    const textarea = screen.getByPlaceholderText(/provide your answers here/i)
    expect(textarea).toBeInTheDocument()

    const regenerateButton = screen.getByRole('button', {
      name: /regenerate with this context/i,
    })
    expect(regenerateButton).toBeInTheDocument()
  })

  it('does not show textarea and button when callback is not provided', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [
        'Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?',
      ],
      summary: [],
      evidence_map: null,
    }

    render(<AiGeneratePanels result={result} />)

    expect(screen.queryByPlaceholderText(/provide your answers here/i)).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /regenerate with this context/i })
    ).not.toBeInTheDocument()
  })

  it('disables regenerate button when textarea is empty', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [
        'Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?',
      ],
      summary: [],
      evidence_map: null,
    }

    render(
      <AiGeneratePanels result={result} onRegenerateWithAnswers={mockOnRegenerateWithAnswers} />
    )

    const regenerateButton = screen.getByRole('button', {
      name: /regenerate with this context/i,
    })
    expect(regenerateButton).toBeDisabled()
  })

  it('enables regenerate button when textarea has content', async () => {
    const user = userEvent.setup()
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [
        'Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?',
      ],
      summary: [],
      evidence_map: null,
    }

    render(
      <AiGeneratePanels result={result} onRegenerateWithAnswers={mockOnRegenerateWithAnswers} />
    )

    const textarea = screen.getByPlaceholderText(/provide your answers here/i)
    await act(async () => {
      await user.type(textarea, 'Reduced latency by 40%')
    })

    const regenerateButton = screen.getByRole('button', {
      name: /regenerate with this context/i,
    })
    expect(regenerateButton).not.toBeDisabled()
  })

  it('calls onRegenerateWithAnswers with textarea value when button is clicked', async () => {
    const user = userEvent.setup()
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [
        'Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?',
      ],
      summary: [],
      evidence_map: null,
    }

    render(
      <AiGeneratePanels result={result} onRegenerateWithAnswers={mockOnRegenerateWithAnswers} />
    )

    const textarea = screen.getByPlaceholderText(/provide your answers here/i)
    await act(async () => {
      await user.type(
        textarea,
        'Reduced API latency by 40%, increased test coverage from 50% to 85%'
      )
    })

    const regenerateButton = screen.getByRole('button', {
      name: /regenerate with this context/i,
    })
    await act(async () => {
      await user.click(regenerateButton)
    })

    expect(mockOnRegenerateWithAnswers).toHaveBeenCalledWith(
      'Reduced API latency by 40%, increased test coverage from 50% to 85%'
    )
  })

  it('disables textarea and button when isGenerating is true', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [
        'Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?',
      ],
      summary: [],
      evidence_map: null,
    }

    render(
      <AiGeneratePanels
        result={result}
        isGenerating={true}
        onRegenerateWithAnswers={mockOnRegenerateWithAnswers}
      />
    )

    const textarea = screen.getByPlaceholderText(/provide your answers here/i)
    expect(textarea).toBeDisabled()

    const regenerateButton = screen.getByRole('button', {
      name: /regenerating/i,
    })
    expect(regenerateButton).toBeDisabled()
  })

  it('shows "Regenerating..." text on button when isGenerating is true', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: [
        'Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?',
      ],
      summary: [],
      evidence_map: null,
    }

    render(
      <AiGeneratePanels
        result={result}
        isGenerating={true}
        onRegenerateWithAnswers={mockOnRegenerateWithAnswers}
      />
    )

    expect(screen.getByText('Regenerating...')).toBeInTheDocument()
  })

  it('renders multiple questions when present', () => {
    const result: AIGenerateCVResponse = {
      draft_cv: mockDraftCv,
      warnings: [],
      questions: ['Question 1: Add measurable outcomes?', 'Question 2: Any specific achievements?'],
      summary: [],
      evidence_map: null,
    }

    render(<AiGeneratePanels result={result} />)

    expect(screen.getByText(/question 1/i)).toBeInTheDocument()
    expect(screen.getByText(/question 2/i)).toBeInTheDocument()
  })
})
