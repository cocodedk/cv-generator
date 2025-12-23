import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import axios from 'axios'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import {
  mockProfileData,
  mockProfileDataWithMultipleExperiences,
  mockCvResponse,
} from '../helpers/cvForm/testData'
import {
  renderCVForm,
  fillNameField,
  submitForm,
  clickLoadProfileButton,
  clickSaveToProfileButton,
  waitForFormToLoad,
} from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm', () => {
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
        '/api/generate-cv',
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

  it('loads profile data when Load from Profile is clicked', async () => {
    mockedAxios.get.mockResolvedValue({ data: mockProfileData })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/profile')
    })

    await waitFor(() => {
      expect(screen.getByText('Select Items to Include')).toBeInTheDocument()
    })
  })

  it('handles profile load error when no profile exists', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { status: 404 },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('No profile found. Please save a profile first.')
    })
  })

  it('saves current form data to profile', async () => {
    mockedAxios.post.mockResolvedValue({ data: { status: 'success' } })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await fillNameField('John Doe')
    await clickSaveToProfileButton()

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/profile',
        expect.objectContaining({
          personal_info: expect.objectContaining({
            name: 'John Doe',
          }),
        })
      )
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('allows selecting experiences and educations from profile', async () => {
    const user = userEvent.setup()
    mockedAxios.get.mockResolvedValue({ data: mockProfileDataWithMultipleExperiences })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(screen.getByText('Select Items to Include')).toBeInTheDocument()
    })

    expect(screen.getByText(/developer/i)).toBeInTheDocument()
    expect(screen.getByText(/senior dev/i)).toBeInTheDocument()

    const checkboxes = screen.getAllByRole('checkbox')
    await act(async () => {
      await user.click(checkboxes[0])
    })

    const loadSelectedButton = screen.getByRole('button', { name: /load selected/i })
    await act(async () => {
      await user.click(loadSelectedButton)
    })

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })
})
