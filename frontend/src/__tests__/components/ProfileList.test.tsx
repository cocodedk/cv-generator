import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as profileService from '../../services/profileService'
import ProfileList from '../../components/ProfileList'

vi.mock('../../services/profileService')
const mockedProfileService = profileService as any

// Mock window.location.hash
Object.defineProperty(window, 'location', {
  value: {
    hash: '',
  },
  writable: true,
})

describe('ProfileList', () => {
  const mockOnError = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock window.location.hash setter
    let hashValue = ''
    Object.defineProperty(window, 'location', {
      value: {
        get hash() {
          return hashValue
        },
        set hash(value) {
          hashValue = value
        },
      },
      writable: true,
    })
  })

  it('renders profile list with Edit and Delete buttons', async () => {
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [
        { name: 'John Doe', updated_at: '2024-01-01T00:00:00' },
        { name: 'Jane Smith', updated_at: '2024-01-02T00:00:00' },
      ],
    })

    render(<ProfileList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('My Profiles (2)')).toBeInTheDocument()
    })

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()

    const editButtons = screen.getAllByText('Edit')
    expect(editButtons.length).toBe(2)

    const deleteButtons = screen.getAllByText('Delete')
    expect(deleteButtons.length).toBe(2)
  })

  it('shows loading state', () => {
    mockedProfileService.listProfiles.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ profiles: [] }), 100))
    )

    render(<ProfileList onError={mockOnError} />)

    expect(screen.getByText('Loading profiles...')).toBeInTheDocument()
  })

  it('shows empty state when no profiles', async () => {
    mockedProfileService.listProfiles.mockResolvedValueOnce({ profiles: [] })

    render(<ProfileList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('No profiles found.')).toBeInTheDocument()
    })
  })

  it('handles search functionality', async () => {
    const user = userEvent.setup()
    mockedProfileService.listProfiles.mockResolvedValue({
      profiles: [
        { name: 'John Doe', updated_at: '2024-01-01T00:00:00' },
        { name: 'Jane Smith', updated_at: '2024-01-02T00:00:00' },
      ],
    })

    render(<ProfileList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText('Search profiles...')
    await act(async () => {
      await user.clear(searchInput)
      await user.type(searchInput, 'John')
    })

    const searchButton = screen.getByText('Search')
    await act(async () => {
      await user.click(searchButton)
    })

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument()
    })
  })

  it('handles delete profile', async () => {
    const user = userEvent.setup()
    window.confirm = vi.fn(() => true)
    mockedProfileService.listProfiles
      .mockResolvedValueOnce({
        profiles: [{ name: 'John Doe', updated_at: '2024-01-01T00:00:00' }],
      })
      .mockResolvedValueOnce({ profiles: [] })
    mockedProfileService.deleteProfileByUpdatedAt.mockResolvedValueOnce({
      status: 'success',
    })

    render(<ProfileList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const deleteButton = screen.getByText('Delete')
    await act(async () => {
      await user.click(deleteButton)
    })

    await waitFor(() => {
      expect(mockedProfileService.deleteProfileByUpdatedAt).toHaveBeenCalledWith(
        '2024-01-01T00:00:00'
      )
      expect(mockedProfileService.listProfiles).toHaveBeenCalledTimes(2)
    })
  })

  it('handles edit profile navigation', async () => {
    const user = userEvent.setup()
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [{ name: 'John Doe', updated_at: '2024-01-01T00:00:00' }],
    })

    render(<ProfileList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const editButton = screen.getByText('Edit')
    await act(async () => {
      await user.click(editButton)
    })

    // URL encoding encodes colons as %3A
    expect(window.location.hash).toBe('#profile-edit/2024-01-01T00%3A00%3A00')
  })

  it('handles error when loading profiles', async () => {
    mockedProfileService.listProfiles.mockRejectedValueOnce({
      response: { data: { detail: 'Failed to load' } },
    })

    render(<ProfileList onError={mockOnError} />)

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to load')
    })
  })

  it('handles error when deleting profile', async () => {
    const user = userEvent.setup()
    window.confirm = vi.fn(() => true)
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [{ name: 'John Doe', updated_at: '2024-01-01T00:00:00' }],
    })
    mockedProfileService.deleteProfileByUpdatedAt.mockRejectedValueOnce({
      response: { data: { detail: 'Failed to delete' } },
    })

    render(<ProfileList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const deleteButton = screen.getByText('Delete')
    await act(async () => {
      await user.click(deleteButton)
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to delete')
    })
  })

  it('refreshes list when navigating back', async () => {
    mockedProfileService.listProfiles.mockResolvedValue({
      profiles: [{ name: 'John Doe', updated_at: '2024-01-01T00:00:00' }],
    })

    render(<ProfileList onError={mockOnError} />)

    await waitFor(() => {
      expect(mockedProfileService.listProfiles).toHaveBeenCalledTimes(1)
    })

    // Simulate hash change
    await act(async () => {
      window.location.hash = '#profile-list'
      window.dispatchEvent(new HashChangeEvent('hashchange'))
    })

    await waitFor(() => {
      expect(mockedProfileService.listProfiles).toHaveBeenCalledTimes(2)
    })
  })
})
