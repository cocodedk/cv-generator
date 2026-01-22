import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { mockProfileDataWithMultipleExperiences } from '../helpers/cvForm/testData'
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

  it('shows profile selection modal when Load from Profile is clicked', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        profiles: [
          {
            name: 'John Doe',
            updated_at: '2024-01-01T00:00:00Z',
            language: 'en',
          },
        ],
      },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/profiles')
    })

    await waitFor(() => {
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })
  })

  it('handles profile load error when no profiles exist', async () => {
    mockedAxios.get.mockResolvedValue({
      data: { profiles: [] },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(
        screen.getByText('No profiles found. Please create a profile first.')
      ).toBeInTheDocument()
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

    // Mock profile list API
    mockedAxios.get
      .mockResolvedValueOnce({
        data: {
          profiles: [
            {
              name: 'John Doe',
              updated_at: '2024-01-01T00:00:00Z',
              language: 'en',
            },
          ],
        },
      })
      // Mock profile by ID API
      .mockResolvedValueOnce({ data: mockProfileDataWithMultipleExperiences })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    // Profile selection modal should appear
    await waitFor(() => {
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    // Click on the profile to select it
    const profileButton = screen.getByText('John Doe')
    await act(async () => {
      await user.click(profileButton)
    })

    // Profile loader modal should appear
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
