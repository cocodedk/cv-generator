import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { mockCvDataMinimal } from '../helpers/cvForm/testData'
import {
  renderCVForm,
  waitForFormToLoad,
  waitForEditModeToLoad,
} from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm - AI Assist', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('does not show per-field AI buttons in create mode', async () => {
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: null,
    })

    await waitForFormToLoad()
    expect(screen.queryByRole('button', { name: /ai rewrite/i })).not.toBeInTheDocument()
  })

  it('shows per-field AI buttons in edit mode', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockCvDataMinimal })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    await waitForEditModeToLoad()
    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: /ai rewrite/i }).length).toBeGreaterThan(0)
    })
  })
})
