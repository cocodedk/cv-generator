import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ProfileManager from '../../components/ProfileManager'
import * as profileService from '../../services/profileService'

// Mock profile service
vi.mock('../../services/profileService')
const mockedProfileService = profileService as any

describe('ProfileManager', () => {
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()
  const mockSetLoading = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock window.confirm
    global.window.confirm = vi.fn(() => true)
  })

  it('renders profile form with all sections', async () => {
    mockedProfileService.getProfile.mockResolvedValue(null)
    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(screen.getByText('Master Profile')).toBeInTheDocument()
    })

    expect(screen.getByText('Personal Information')).toBeInTheDocument()
    expect(screen.getByText('Work Experience')).toBeInTheDocument()
    expect(screen.getByText('Education')).toBeInTheDocument()
    expect(screen.getByText('Skills')).toBeInTheDocument()
  })

  it('loads existing profile on mount', async () => {
    const profileData = {
      personal_info: {
        name: 'John Doe',
        email: 'john@example.com',
      },
      experience: [],
      education: [],
      skills: [],
    }
    mockedProfileService.getProfile.mockResolvedValue(profileData)

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(mockedProfileService.getProfile).toHaveBeenCalled()
    })

    await waitFor(() => {
      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      expect(nameInput.value).toBe('John Doe')
    })
  })

  it('saves profile successfully', async () => {
    const user = userEvent.setup()
    mockedProfileService.getProfile.mockResolvedValue(null)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(screen.getByText('Save Profile')).toBeInTheDocument()
    })

    const nameInput = screen.getByLabelText(/full name/i)
    await user.type(nameInput, 'John Doe')

    const submitButton = screen.getByRole('button', { name: /save profile/i })
    await user.click(submitButton)

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
    const profileData = {
      personal_info: {
        name: 'John Doe',
        email: 'john@example.com',
      },
      experience: [],
      education: [],
      skills: [],
    }
    mockedProfileService.getProfile.mockResolvedValue(profileData)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(screen.getByText('Update Profile')).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /update profile/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockedProfileService.saveProfile).toHaveBeenCalled()
    })
  })

  it('deletes profile successfully', async () => {
    const user = userEvent.setup()
    const profileData = {
      personal_info: {
        name: 'John Doe',
      },
      experience: [],
      education: [],
      skills: [],
    }
    mockedProfileService.getProfile.mockResolvedValue(profileData)
    mockedProfileService.deleteProfile.mockResolvedValue({ status: 'success' })

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(screen.getByText('Delete Profile')).toBeInTheDocument()
    })

    const deleteButton = screen.getByRole('button', { name: /delete profile/i })
    await user.click(deleteButton)

    await waitFor(() => {
      expect(mockedProfileService.deleteProfile).toHaveBeenCalled()
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('handles profile load error', async () => {
    mockedProfileService.getProfile.mockRejectedValue(new Error('Server error'))

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to load profile: Server error')
    })
  })

  it('validates required name field', async () => {
    const user = userEvent.setup()
    mockedProfileService.getProfile.mockResolvedValue(null)

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(screen.getByText('Save Profile')).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /save profile/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    expect(mockedProfileService.saveProfile).not.toHaveBeenCalled()
  })

  it('loads profile when Load Profile button is clicked', async () => {
    const user = userEvent.setup()
    const profileData = {
      personal_info: {
        name: 'Jane Doe',
        email: 'jane@example.com',
      },
      experience: [],
      education: [],
      skills: [],
    }
    mockedProfileService.getProfile
      .mockResolvedValueOnce(null) // Initial load
      .mockResolvedValueOnce(profileData) // After button click

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(screen.getByText('Load Profile')).toBeInTheDocument()
    })

    const loadButton = screen.getByRole('button', { name: /load profile/i })
    await user.click(loadButton)

    await waitFor(() => {
      expect(mockedProfileService.getProfile).toHaveBeenCalledTimes(2)
    })

    await waitFor(() => {
      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      expect(nameInput.value).toBe('Jane Doe')
    })
  })
})
