import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import {
  mockCvData,
  mockCvDataMinimal,
  mockCvDataForUpdate,
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

describe('CVForm - Edit Mode', () => {
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
