import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as profileService from '../../services/profileService'
import { renderProfileManager } from '../helpers/profileManager/testHelpers'
import { within } from '@testing-library/react'
import {
  createMockCallbacks,
  setupWindowMocks,
  createProfileData,
} from '../helpers/profileManager/mocks'

vi.mock('../../services/profileService')
const mockedProfileService = profileService as any

describe('ProfileManager - Save and Update', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('saves profile successfully', async () => {
    const user = userEvent.setup()
    mockedProfileService.getProfile.mockResolvedValue(null)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for loading to complete
    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    const nameInput = within(container).getByLabelText(/full name/i)
    await act(async () => {
      await user.type(nameInput, 'John Doe')
    })

    const submitButton = within(container).getByRole('button', { type: 'submit' })
    await act(async () => {
      await user.click(submitButton)
    })

    await waitFor(() => {
      expect(mockedProfileService.saveProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          personal_info: expect.objectContaining({
            name: 'John Doe',
          }),
        })
      )
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('updates existing profile', async () => {
    const user = userEvent.setup()
    const profileData = createProfileData()
    mockedProfileService.getProfile.mockResolvedValue(profileData)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for loading to complete
    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Wait for profile to load and form to show "Update Profile"
    await waitFor(
      () => {
        expect(within(container).getByRole('button', { name: /update profile/i, hidden: false })).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    const submitButton = within(container).getByRole('button', { type: 'submit' })
    await act(async () => {
      await user.click(submitButton)
    })

    await waitFor(() => {
      expect(mockedProfileService.saveProfile).toHaveBeenCalled()
    })
  })
})
