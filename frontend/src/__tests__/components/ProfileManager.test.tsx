import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import axios from 'axios'
import ProfileManager from '../../components/ProfileManager'

// Mock axios
vi.mock('axios')
const mockedAxios = axios as any

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
    mockedAxios.get.mockResolvedValue({ status: 404 })
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
    mockedAxios.get.mockResolvedValue({ data: profileData })

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/profile')
    })

    await waitFor(() => {
      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      expect(nameInput.value).toBe('John Doe')
    })
  })

  it('saves profile successfully', async () => {
    const user = userEvent.setup()
    mockedAxios.get.mockResolvedValue({ status: 404 })
    mockedAxios.post.mockResolvedValue({ data: { status: 'success' } })

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
    mockedAxios.get.mockResolvedValue({ data: profileData })
    mockedAxios.post.mockResolvedValue({ data: { status: 'success' } })

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(screen.getByText('Update Profile')).toBeInTheDocument()
    })

    const submitButton = screen.getByRole('button', { name: /update profile/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalled()
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
    mockedAxios.get.mockResolvedValue({ data: profileData })
    mockedAxios.delete.mockResolvedValue({ data: { status: 'success' } })

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(screen.getByText('Delete Profile')).toBeInTheDocument()
    })

    const deleteButton = screen.getByRole('button', { name: /delete profile/i })
    await user.click(deleteButton)

    await waitFor(() => {
      expect(mockedAxios.delete).toHaveBeenCalledWith('/api/profile')
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('handles profile load error', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { status: 500, data: { detail: 'Server error' } },
    })

    render(
      <ProfileManager onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />
    )

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to load profile')
    })
  })

  it('validates required name field', async () => {
    const user = userEvent.setup()
    mockedAxios.get.mockResolvedValue({ status: 404 })

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

    expect(mockedAxios.post).not.toHaveBeenCalled()
  })
})
