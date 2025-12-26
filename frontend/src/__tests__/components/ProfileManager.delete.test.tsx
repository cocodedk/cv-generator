import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as profileService from '../../services/profileService'
import { renderProfileManager } from '../helpers/profileManager/testHelpers'
import {
  createMockCallbacks,
  setupWindowMocks,
  createProfileData,
} from '../helpers/profileManager/mocks'

vi.mock('../../services/profileService')
const mockedProfileService = profileService as any

describe('ProfileManager - Delete and Validation', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('deletes profile successfully', async () => {
    const user = userEvent.setup()
    const profileData = createProfileData()
    mockedProfileService.getProfile.mockResolvedValue(profileData)
    mockedProfileService.deleteProfile.mockResolvedValue({ status: 'success' })

    renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for loading to complete
    await waitFor(
      () => {
        expect(screen.queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    await waitFor(() => {
      expect(screen.getByText('Delete Profile')).toBeInTheDocument()
    })

    const deleteButton = screen.getByRole('button', { name: /delete profile/i })
    await act(async () => {
      await user.click(deleteButton)
    })

    await waitFor(() => {
      expect(mockedProfileService.deleteProfile).toHaveBeenCalled()
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('validates required name field', async () => {
    const user = userEvent.setup()
    mockedProfileService.getProfile.mockResolvedValue(null)

    renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for loading to complete
    await waitFor(
      () => {
        expect(screen.queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    await waitFor(() => {
      expect(screen.getByText('Save Profile')).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /save profile/i })
    await act(async () => {
      await user.click(submitButton)
    })

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    expect(mockedProfileService.saveProfile).not.toHaveBeenCalled()
  })
})
