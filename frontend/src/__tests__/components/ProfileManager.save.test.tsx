import { describe, it, expect, beforeEach, vi } from 'vitest'
import { waitFor, act } from '@testing-library/react'
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

    const submitButtons = within(container).getAllByRole('button', {
      name: /Save Profile|Update Profile/i,
    })
    const submitButton = submitButtons[0] // Use the top save button
    await act(async () => {
      await user.click(submitButton)
    })

    await waitFor(() => {
      const calls = mockedProfileService.saveProfile.mock.calls
      expect(calls.length).toBe(1)
      const calledData = calls[0][0]
      expect(calledData.personal_info.name).toBe('John Doe')
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

    // Wait for profile to load and button to show "Update Profile"
    await waitFor(
      () => {
        within(container).getAllByRole('button', { name: /Update Profile/i })
      },
      { timeout: 3000 }
    )

    const submitButtons = within(container).getAllByRole('button', {
      name: /Save Profile|Update Profile/i,
    })
    const submitButton = submitButtons[0] // Use the top save button
    await act(async () => {
      await user.click(submitButton)
    })

    await waitFor(() => {
      expect(mockedProfileService.saveProfile).toHaveBeenCalled()
    })
  })
})
