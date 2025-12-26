import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { act } from '@testing-library/react'
import * as profileService from '../../services/profileService'
import { renderProfileManager } from '../helpers/profileManager/testHelpers'
import {
  createMockCallbacks,
  setupWindowMocks,
  createProfileData,
} from '../helpers/profileManager/mocks'

vi.mock('../../services/profileService')
const mockedProfileService = profileService as any

describe('ProfileManager - Loading', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('loads existing profile on mount', async () => {
    const profileData = createProfileData()
    mockedProfileService.getProfile.mockResolvedValue(profileData)

    renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for loading to complete and form to render
    await waitFor(
      () => {
        expect(screen.queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    await waitFor(() => {
      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      expect(nameInput.value).toBe('John Doe')
    })
  })

  it('handles profile load error', async () => {
    mockedProfileService.getProfile.mockRejectedValue(new Error('Server error'))

    renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for loading to complete (even on error)
    await waitFor(
      () => {
        expect(screen.queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to load profile: Server error')
    })
  })

  it('opens profile selection modal when Load Profile button is clicked', async () => {
    const user = userEvent.setup()
    mockedProfileService.getProfile.mockResolvedValueOnce(null) // Initial load
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [
        { name: 'John Doe', updated_at: '2024-01-01T00:00:00' },
        { name: 'Jane Smith', updated_at: '2024-01-02T00:00:00' },
      ],
    })

    renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for initial load to complete
    await waitFor(
      () => {
        expect(screen.queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    await waitFor(() => {
      expect(screen.getByText('Load Profile')).toBeInTheDocument()
    })

    const loadButton = screen.getByRole('button', { name: /load profile/i })
    await act(async () => {
      await user.click(loadButton)
    })

    // Modal should appear
    await waitFor(() => {
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    // Profile list should be visible
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('loads selected profile from modal', async () => {
    const user = userEvent.setup()
    const selectedProfile = createProfileData({
      personal_info: { name: 'Jane Smith', email: 'jane@example.com' },
    })
    mockedProfileService.getProfile.mockResolvedValueOnce(null) // Initial load
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [
        { name: 'John Doe', updated_at: '2024-01-01T00:00:00' },
        { name: 'Jane Smith', updated_at: '2024-01-02T00:00:00' },
      ],
    })
    mockedProfileService.getProfileByUpdatedAt.mockResolvedValueOnce(selectedProfile)

    renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for initial load to complete
    await waitFor(
      () => {
        expect(screen.queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    const loadButton = screen.getByRole('button', { name: /load profile/i })
    await act(async () => {
      await user.click(loadButton)
    })

    // Wait for modal to appear
    await waitFor(() => {
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    // Click on Jane Smith profile
    const janeProfileButton = screen.getByText('Jane Smith').closest('button')
    expect(janeProfileButton).toBeInTheDocument()
    await act(async () => {
      await user.click(janeProfileButton!)
    })

    // Wait for modal to close and profile to load
    await waitFor(
      () => {
        expect(screen.queryByText('Select Profile to Load')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    await waitFor(() => {
      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      expect(nameInput.value).toBe('Jane Smith')
    })

    expect(mockOnSuccess).toHaveBeenCalledWith('Profile loaded successfully!')
  })
})
