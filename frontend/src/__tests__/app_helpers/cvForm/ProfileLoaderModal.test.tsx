import { describe, it, expect, vi } from 'vitest'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ProfileLoaderModal from '../../../app_helpers/cvForm/ProfileLoaderModal'
import { ProfileData } from '../../../types/cv'

describe('ProfileLoaderModal', () => {
  const mockOnApply = vi.fn()
  const mockOnCancel = vi.fn()
  const mockOnExpToggle = vi.fn()
  const mockOnEduToggle = vi.fn()

  const profileData: ProfileData = {
    personal_info: { name: 'John Doe' },
    experience: [
      { title: 'Developer', company: 'Corp', start_date: '2020-01' },
      { title: 'Lead', company: 'Tech', start_date: '2021-01' },
    ],
    education: [{ degree: 'BS', institution: 'University' }],
    skills: [],
  }

  it('renders with profile data', () => {
    render(
      <ProfileLoaderModal
        profileData={profileData}
        selectedExperiences={new Set([0, 1])}
        selectedEducations={new Set([0])}
        onExperienceToggle={mockOnExpToggle}
        onEducationToggle={mockOnEduToggle}
        onApply={mockOnApply}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByText('Select Items to Include')).toBeInTheDocument()
    expect(screen.getByText('Developer')).toBeInTheDocument()
    expect(screen.getByText('Lead')).toBeInTheDocument()
    expect(screen.getByText('BS')).toBeInTheDocument()
  })

  it('toggles experience selection', async () => {
    const user = userEvent.setup()
    render(
      <ProfileLoaderModal
        profileData={profileData}
        selectedExperiences={new Set([0])}
        selectedEducations={new Set()}
        onExperienceToggle={mockOnExpToggle}
        onEducationToggle={mockOnEduToggle}
        onApply={mockOnApply}
        onCancel={mockOnCancel}
      />
    )

    const checkboxes = screen.getAllByRole('checkbox')
    await act(async () => {
      await user.click(checkboxes[1])
    })

    expect(mockOnExpToggle).toHaveBeenCalledWith(1, true)
  })

  it('calls onApply when Load Selected clicked', async () => {
    const user = userEvent.setup()
    render(
      <ProfileLoaderModal
        profileData={profileData}
        selectedExperiences={new Set()}
        selectedEducations={new Set()}
        onExperienceToggle={mockOnExpToggle}
        onEducationToggle={mockOnEduToggle}
        onApply={mockOnApply}
        onCancel={mockOnCancel}
      />
    )

    const applyButton = screen.getByText('Load Selected')
    await act(async () => {
      await user.click(applyButton)
    })

    expect(mockOnApply).toHaveBeenCalledOnce()
  })

  it('calls onCancel when Cancel clicked', async () => {
    const user = userEvent.setup()
    render(
      <ProfileLoaderModal
        profileData={profileData}
        selectedExperiences={new Set()}
        selectedEducations={new Set()}
        onExperienceToggle={mockOnExpToggle}
        onEducationToggle={mockOnEduToggle}
        onApply={mockOnApply}
        onCancel={mockOnCancel}
      />
    )

    const cancelButton = screen.getByText('Cancel')
    await act(async () => {
      await user.click(cancelButton)
    })

    expect(mockOnCancel).toHaveBeenCalledOnce()
  })
})
