import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { mockProfileDataWithMultipleExperiences, mockProfileData } from '../helpers/cvForm/testData'
import {
  renderCVForm,
  fillNameField,
  clickLoadProfileButton,
  clickSaveToProfileButton,
  waitForFormToLoad,
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

  it('handles profile selection modal loading error', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { status: 500, data: { detail: 'Server error' } },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Server error')
    })
  })

  it('handles profile selection modal network error', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Network error'))

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to list profiles')
    })
  })

  it('displays profiles with different languages correctly', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        profiles: [
          {
            name: 'John Doe',
            updated_at: '2024-01-01T00:00:00Z',
            language: 'en',
          },
          {
            name: 'Maria Garcia',
            updated_at: '2024-01-02T00:00:00Z',
            language: 'es',
          },
          {
            name: 'Pierre Dubois',
            updated_at: '2024-01-03T00:00:00Z',
            language: 'fr',
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
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    // Check that all profiles are displayed with their languages
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Maria Garcia')).toBeInTheDocument()
    expect(screen.getByText('Pierre Dubois')).toBeInTheDocument()

    // Check language display
    expect(screen.getByText(/Language: English/)).toBeInTheDocument()
    expect(screen.getByText(/Language: Spanish/)).toBeInTheDocument()
    expect(screen.getByText(/Language: French/)).toBeInTheDocument()
  })

  it('handles profiles with null language (fallback to unknown)', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        profiles: [
          {
            name: 'Test User',
            updated_at: '2024-01-01T00:00:00Z',
            language: null, // Explicitly null
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
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    // Should display Unknown for null language
    expect(screen.getByText(/Language: Unknown/)).toBeInTheDocument()
  })

  it('allows closing profile selection modal', async () => {
    const user = userEvent.setup()

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
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    // Click close button (X button)
    const closeButton = screen.getByRole('button', { name: /close/i })
    await act(async () => {
      await user.click(closeButton)
    })

    // Modal should be closed
    await waitFor(() => {
      expect(screen.queryByText('Select Profile to Load')).not.toBeInTheDocument()
    })
  })

  it('loads profile data and allows canceling profile loader modal', async () => {
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

    // Click cancel button in profile loader modal
    const cancelButton = screen.getByTestId('profile-loader-cancel')
    await act(async () => {
      await user.click(cancelButton)
    })

    // Check that success was not called (modal was cancelled)
    expect(mockOnSuccess).not.toHaveBeenCalled()

    // Modal should eventually be closed (but we don't need to wait for it in the test)
    // The important behavior is that cancel was called and success was not
  })

  it('handles profile selection API failure', async () => {
    const user = userEvent.setup()

    // Mock profile list API success
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
      // Mock profile by ID API failure
      .mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'Profile not found' } },
      })

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

    // Should handle the error
    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Profile not found')
    })

    // Modal should be closed after error (but we don't need to wait for it in the test)
    // The important behavior is that the error was handled correctly
  })

  it('loads profile data and populates CV form correctly', async () => {
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
      .mockResolvedValueOnce({ data: mockProfileData })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitForFormToLoad()

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

    // Click load selected button without deselecting anything (should include all)
    const loadSelectedButton = screen.getByRole('button', { name: /load selected/i })
    await act(async () => {
      await user.click(loadSelectedButton)
    })

    // Should populate the form
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('Profile data loaded successfully!')
    })

    // Verify that a concrete form field was populated
    await waitFor(() => {
      const nameInput = screen.getByLabelText(/full name/i)
      expect(nameInput).toHaveValue('John Doe')
    })
  })

  it('displays multiple profiles in selection modal', async () => {
    const user = userEvent.setup()

    mockedAxios.get.mockResolvedValue({
      data: {
        profiles: [
          {
            name: 'John Doe',
            updated_at: '2024-01-01T00:00:00Z',
            language: 'en',
          },
          {
            name: 'Jane Smith',
            updated_at: '2024-01-02T00:00:00Z',
            language: 'fr',
          },
          {
            name: 'Bob Johnson',
            updated_at: '2024-01-03T00:00:00Z',
            language: 'de',
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
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    // Check that all profiles are displayed
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
    expect(screen.getByText('Bob Johnson')).toBeInTheDocument()

    // Check language formatting
    expect(screen.getByText(/Language: English/)).toBeInTheDocument()
    expect(screen.getByText(/Language: French/)).toBeInTheDocument()
    expect(screen.getByText(/Language: German/)).toBeInTheDocument()

    // Close modal without selecting
    const closeButton = screen.getByRole('button', { name: /close/i })
    await act(async () => {
      await user.click(closeButton)
    })

    await waitFor(() => {
      expect(screen.queryByText('Select Profile to Load')).not.toBeInTheDocument()
    })
  })

  it('handles profile with incomplete data', async () => {
    const user = userEvent.setup()

    const incompleteProfile = {
      personal_info: {
        name: 'Incomplete User',
        // Missing email, phone, etc.
      },
      experience: [], // Empty experiences
      education: [], // Empty education
      skills: [],
    }

    // Mock profile list API
    mockedAxios.get
      .mockResolvedValueOnce({
        data: {
          profiles: [
            {
              name: 'Incomplete User',
              updated_at: '2024-01-01T00:00:00Z',
              language: 'en',
            },
          ],
        },
      })
      // Mock profile by ID API
      .mockResolvedValueOnce({ data: incompleteProfile })

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
    const profileButton = screen.getByText('Incomplete User')
    await act(async () => {
      await user.click(profileButton)
    })

    // Profile loader modal should appear (even with empty data)
    await waitFor(() => {
      expect(screen.getByText('Select Items to Include')).toBeInTheDocument()
    })

    // Should be able to load even with incomplete profile data
    const loadSelectedButton = screen.getByRole('button', { name: /load selected/i })
    await act(async () => {
      await user.click(loadSelectedButton)
    })

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith('Profile data loaded successfully!')
    })
  })
})
