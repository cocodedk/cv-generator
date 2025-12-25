import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { mockCvResponse } from '../helpers/cvForm/testData'
import { renderCVForm, fillNameField, submitForm } from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm - Render & Submit', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('renders form with all sections', () => {
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    expect(screen.getByText('Personal Information')).toBeInTheDocument()
    expect(screen.getByText('Work Experience')).toBeInTheDocument()
    expect(screen.getByText('Education')).toBeInTheDocument()
    expect(screen.getByText('Skills')).toBeInTheDocument()
  })

  it('submits form with valid data', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await fillNameField('John Doe')
    await submitForm()

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/save-cv',
        expect.objectContaining({
          personal_info: expect.objectContaining({
            name: 'John Doe',
          }),
        })
      )
    })

    expect(mockSetLoading).toHaveBeenCalledWith(true)
    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('handles form submission error', async () => {
    mockedAxios.post.mockRejectedValue({
      response: { data: { detail: 'Server error' } },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await fillNameField('John Doe')
    await submitForm()

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Server error')
    })
  })

  it('validates required name field', async () => {
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await submitForm()

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    expect(mockedAxios.post).not.toHaveBeenCalled()
  })

  it('allows theme selection', async () => {
    const user = userEvent.setup()

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    const themeSelect = screen.getByLabelText(/theme/i)
    await act(async () => {
      await user.selectOptions(themeSelect, 'modern')
    })

    expect(themeSelect).toHaveValue('modern')
  })
})
