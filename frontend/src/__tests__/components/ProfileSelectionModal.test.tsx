import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { act } from '@testing-library/react'
import ProfileSelectionModal from '../../components/ProfileSelectionModal'
import * as profileService from '../../services/profileService'

vi.mock('../../services/profileService')
const mockedProfileService = profileService as any

describe('ProfileSelectionModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSelect = vi.fn()
  const mockOnError = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('does not render when isOpen is false', () => {
    render(
      <ProfileSelectionModal
        isOpen={false}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    expect(screen.queryByText('Select Profile to Load')).not.toBeInTheDocument()
  })

  it('renders modal when isOpen is true', async () => {
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [
        { name: 'John Doe', updated_at: '2024-01-01T00:00:00' },
        { name: 'Jane Smith', updated_at: '2024-01-02T00:00:00' },
      ],
    })

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('shows loading state while fetching profiles', async () => {
    mockedProfileService.listProfiles.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ profiles: [] }), 100))
    )

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    expect(screen.getByText('Loading profiles...')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.queryByText('Loading profiles...')).not.toBeInTheDocument()
    })
  })

  it('shows empty state when no profiles found', async () => {
    mockedProfileService.listProfiles.mockResolvedValueOnce({ profiles: [] })

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('No profiles found.')).toBeInTheDocument()
    })
  })

  it('calls onClose when Cancel button is clicked', async () => {
    const user = userEvent.setup()
    mockedProfileService.listProfiles.mockResolvedValueOnce({ profiles: [] })

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Cancel')).toBeInTheDocument()
    })

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await act(async () => {
      await user.click(cancelButton)
    })

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('calls onClose when close button (X) is clicked', async () => {
    const user = userEvent.setup()
    mockedProfileService.listProfiles.mockResolvedValueOnce({ profiles: [] })

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    await waitFor(() => {
      expect(screen.getByLabelText('Close')).toBeInTheDocument()
    })

    const closeButton = screen.getByLabelText('Close')
    await act(async () => {
      await user.click(closeButton)
    })

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('calls onSelect with profile data when profile is clicked', async () => {
    const user = userEvent.setup()
    const profileData = {
      personal_info: { name: 'John Doe', email: 'john@example.com' },
      experience: [],
      education: [],
      skills: [],
    }
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [{ name: 'John Doe', updated_at: '2024-01-01T00:00:00' }],
    })
    mockedProfileService.getProfileByUpdatedAt.mockResolvedValueOnce(profileData)

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const profileButton = screen.getByText('John Doe').closest('button')
    expect(profileButton).toBeInTheDocument()
    await act(async () => {
      await user.click(profileButton!)
    })

    await waitFor(() => {
      expect(mockOnSelect).toHaveBeenCalledWith(profileData)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })

  it('calls onError when profile list fails to load', async () => {
    mockedProfileService.listProfiles.mockRejectedValueOnce(new Error('Failed to load'))

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to load')
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })

  it('calls onError when profile selection fails', async () => {
    const user = userEvent.setup()
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [{ name: 'John Doe', updated_at: '2024-01-01T00:00:00' }],
    })
    mockedProfileService.getProfileByUpdatedAt.mockRejectedValueOnce(new Error('Failed to load'))

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const profileButton = screen.getByText('John Doe').closest('button')
    await act(async () => {
      await user.click(profileButton!)
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to load')
    })
  })

  it('formats dates correctly', async () => {
    mockedProfileService.listProfiles.mockResolvedValueOnce({
      profiles: [{ name: 'John Doe', updated_at: '2024-01-15T10:30:00' }],
    })

    render(
      <ProfileSelectionModal
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        onError={mockOnError}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    // Check that date is formatted (should contain month abbreviation)
    const dateText = screen.getByText(/Jan/i)
    expect(dateText).toBeInTheDocument()
  })
})
