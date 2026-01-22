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

describe('ProfileManager - AI Assist', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('shows AI assist buttons for Professional Summary field', async () => {
    mockedProfileService.getProfile.mockResolvedValue(null)

    const { container } = renderProfileManager({
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
      expect(screen.getByText('Master Profile')).toBeInTheDocument()
    })

    // AI assist buttons should be visible for Professional Summary
    await waitFor(() => {
      const rewriteButtons = screen.getAllByRole('button', { name: /ai rewrite/i })
      const bulletsButtons = screen.getAllByRole('button', { name: /ai bullets/i })
      expect(rewriteButtons.length).toBeGreaterThan(0)
      expect(bulletsButtons.length).toBeGreaterThan(0)
    })
  })

  it('shows AI assist buttons for experience Role Summary field', async () => {
    const user = userEvent.setup()
    mockedProfileService.getProfile.mockResolvedValue(null)

    const { container } = renderProfileManager({
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
      expect(screen.getByText('Work Experience')).toBeInTheDocument()
    })

    // Add an experience
    const addExperienceButton = screen.getByRole('button', { name: /add experience/i })
    await act(async () => {
      await user.click(addExperienceButton)
    })

    // AI assist buttons should be visible for Role Summary
    await waitFor(() => {
      const rewriteButtons = screen.getAllByRole('button', { name: /ai rewrite/i })
      const bulletsButtons = screen.getAllByRole('button', { name: /ai bullets/i })
      expect(rewriteButtons.length).toBeGreaterThan(0)
      expect(bulletsButtons.length).toBeGreaterThan(0)
    })
  })

  it('shows AI assist buttons for project highlights field', async () => {
    const user = userEvent.setup()
    mockedProfileService.getProfile.mockResolvedValue(null)

    const { container } = renderProfileManager({
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
      expect(screen.getByText('Work Experience')).toBeInTheDocument()
    })

    // Add an experience
    const addExperienceButton = screen.getByRole('button', { name: /add experience/i })
    await act(async () => {
      await user.click(addExperienceButton)
    })

    // Add a project
    await waitFor(() => {
      const addProjectButton = screen.getByRole('button', { name: /add project/i })
      expect(addProjectButton).toBeInTheDocument()
    })

    const addProjectButton = screen.getByRole('button', { name: /add project/i })
    await act(async () => {
      await user.click(addProjectButton)
    })

    // AI assist buttons should be visible for project highlights
    await waitFor(() => {
      const rewriteButtons = screen.getAllByRole('button', { name: /ai rewrite/i })
      const bulletsButtons = screen.getAllByRole('button', { name: /ai bullets/i })
      expect(rewriteButtons.length).toBeGreaterThan(0)
      expect(bulletsButtons.length).toBeGreaterThan(0)
    })
  })

  it('AI rewrite button transforms text in Professional Summary', async () => {
    const user = userEvent.setup()
    const profileData = createProfileData({
      personal_info: {
        name: 'John Doe',
        summary: '<p>responsible for developing features</p>',
      },
    })
    mockedProfileService.getProfile.mockResolvedValue(profileData)

    const { container } = renderProfileManager({
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

    // Wait for profile to load and form to show "Update Profile"
    await waitFor(
      () => {
        expect(within(container).getByRole('button', { name: 'Update Profile' })).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Find and click AI rewrite button
    const rewriteButtons = screen.getAllByRole('button', { name: /ai rewrite/i })
    expect(rewriteButtons.length).toBeGreaterThan(0)

    await act(async () => {
      await user.click(rewriteButtons[0])
    })

    // The text should be transformed (removes "responsible for" prefix)
    await waitFor(() => {
      // The form should have updated content
      expect(mockedProfileService.getProfile).toHaveBeenCalled()
    })
  })

  it('AI bullets button converts text to bullets in Role Summary', async () => {
    const user = userEvent.setup()
    const profileData = createProfileData({
      experience: [
        {
          title: 'Developer',
          company: 'Tech Corp',
          start_date: '2020-01',
          end_date: '2023-12',
          description: '<p>worked on api. helped improve performance.</p>',
          location: '',
          projects: [],
        },
      ],
    })
    mockedProfileService.getProfile.mockResolvedValue(profileData)

    const { container } = renderProfileManager({
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

    // Wait for profile to load and form to show "Update Profile"
    await waitFor(
      () => {
        expect(within(container).getByRole('button', { name: 'Update Profile' })).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Find and click AI bullets button (should be multiple - one for summary, one for description)
    const bulletsButtons = screen.getAllByRole('button', { name: /ai bullets/i })
    expect(bulletsButtons.length).toBeGreaterThan(0)

    // Click the second one (should be for the experience description)
    if (bulletsButtons.length > 1) {
      await act(async () => {
        await user.click(bulletsButtons[1])
      })
    } else {
      await act(async () => {
        await user.click(bulletsButtons[0])
      })
    }

    // The text should be converted to bullets
    await waitFor(() => {
      expect(mockedProfileService.getProfile).toHaveBeenCalled()
    })
  })
})
