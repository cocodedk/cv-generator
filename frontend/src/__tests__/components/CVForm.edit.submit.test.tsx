import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import {
  mockCvDataForUpdate,
  mockCvDataMinimal,
  mockUpdateResponse,
} from '../helpers/cvForm/testData'
import {
  renderCVForm,
  fillNameField,
  clearNameField,
  submitForm,
  waitForEditModeToLoad,
} from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm - Edit Mode (Submit)', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('uses PUT request to update CV in edit mode', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockCvDataForUpdate })
    mockedAxios.put.mockResolvedValue({ data: mockUpdateResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    await waitForEditModeToLoad()

    await clearNameField()
    await fillNameField('John Doe')
    await submitForm(/update cv/i)

    await waitFor(() => {
      expect(mockedAxios.put).toHaveBeenCalledWith(
        '/api/cv/test-cv-id',
        expect.objectContaining({
          personal_info: expect.objectContaining({
            name: 'John Doe',
          }),
        })
      )
    })

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('CV updated. Printable view opened.')
    })
  })

  it('shows Update CV button text in edit mode', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockCvDataMinimal })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /update cv/i })).toBeInTheDocument()
    })
  })

  it('handles CV not found error in edit mode', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { status: 404 },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'non-existent',
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('CV not found')
    })
  })

  it('handles CV load error in edit mode', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { data: { detail: 'Server error' } },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Server error')
    })
  })

  it('validates form in edit mode', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockCvDataForUpdate })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    await waitForEditModeToLoad()

    await clearNameField()
    await submitForm(/update cv/i)

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    expect(mockedAxios.put).not.toHaveBeenCalled()
  })
})
