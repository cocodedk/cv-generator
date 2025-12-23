import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import CVForm from '../../components/CVForm'

vi.mock('../../app_helpers/cvForm/useCvLoader', () => ({
  useCvLoader: () => ({ isLoadingCv: false }),
}))

vi.mock('../../app_helpers/cvForm/useProfileManager', () => ({
  useProfileManager: () => ({
    showProfileLoader: false,
    profileData: null,
    selectedExperiences: new Set(),
    selectedEducations: new Set(),
    loadProfile: vi.fn(),
    applySelectedProfile: vi.fn(),
    saveToProfile: vi.fn(),
    closeProfileLoader: vi.fn(),
    handleExperienceToggle: vi.fn(),
    handleEducationToggle: vi.fn(),
  }),
}))

vi.mock('../../app_helpers/cvForm/useCvSubmit', () => ({
  useCvSubmit: () => ({
    isSubmitting: true,
    onSubmit: vi.fn(),
  }),
}))

describe('CVForm submit state', () => {
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()
  const mockSetLoading = vi.fn()

  it('shows Generating... when submitting new CV', () => {
    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    expect(screen.getByRole('button', { name: /generating/i })).toBeInTheDocument()
  })

  it('shows Updating... when submitting edited CV', () => {
    render(
      <CVForm
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        setLoading={mockSetLoading}
        cvId="cv-123"
      />
    )

    expect(screen.getByRole('button', { name: /updating/i })).toBeInTheDocument()
  })
})
