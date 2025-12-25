import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { mockCvData, mockCvDataMinimal } from '../helpers/cvForm/testData'
import { renderCVForm, waitForEditModeToLoad } from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm - Edit Mode (Load)', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('loads CV data when cvId prop is provided', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockCvData })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/cv/test-cv-id')
    })

    await waitFor(() => {
      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      expect(nameInput.value).toBe('Jane Doe')
    })
  })

  it('shows loading state while fetching CV data', async () => {
    mockedAxios.get.mockImplementation(
      () =>
        new Promise(resolve => {
          setTimeout(() => resolve({ data: { personal_info: { name: 'Test' } } }), 100)
        })
    )

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    expect(screen.getByText('Loading CV data...')).toBeInTheDocument()
  })

  it('shows Edit CV title in edit mode', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockCvDataMinimal })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    await waitForEditModeToLoad()
  })
})
