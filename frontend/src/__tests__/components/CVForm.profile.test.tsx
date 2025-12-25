import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { mockProfileData, mockProfileDataWithMultipleExperiences } from '../helpers/cvForm/testData'
import {
  renderCVForm,
  fillNameField,
  clickLoadProfileButton,
  clickSaveToProfileButton,
} from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm - Profile', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
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
