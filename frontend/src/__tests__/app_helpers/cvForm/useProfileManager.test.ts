import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import axios from 'axios'
import { useProfileManager } from '../../../app_helpers/cvForm/useProfileManager'
import { CVData } from '../../../types/cv'

vi.mock('axios')
const mockedAxios = axios as any

describe('useProfileManager', () => {
  const mockReset = vi.fn()
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()
  const mockSetLoading = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows profile selection modal', async () => {
    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    act(() => {
      result.current.loadProfile()
    })

    expect(result.current.showProfileSelection).toBe(true)
    expect(result.current.showProfileLoader).toBe(false)
  })

  it('handles profile selected from modal', async () => {
    const profileData = {
      personal_info: { name: 'John Doe' },
      experience: [{ title: 'Dev' }],
      education: [{ degree: 'BS' }],
      skills: [],
    }

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    act(() => {
      result.current.handleProfileSelected(profileData)
    })

    expect(result.current.showProfileSelection).toBe(false)
    expect(result.current.showProfileLoader).toBe(true)
    expect(result.current.profileData).toEqual(profileData)
    expect(result.current.selectedExperiences.has(0)).toBe(true)
    expect(result.current.selectedEducations.has(0)).toBe(true)
  })

  it('closes profile selection modal', async () => {
    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    act(() => {
      result.current.loadProfile() // Opens selection modal
    })

    expect(result.current.showProfileSelection).toBe(true)

    act(() => {
      result.current.closeProfileSelection()
    })

    expect(result.current.showProfileSelection).toBe(false)
  })

  it('applies selected profile', async () => {
    const profileData = {
      personal_info: { name: 'John Doe' },
      experience: [
        {
          title: 'Dev',
          company: 'ACME',
          start_date: '2020-01',
          projects: [{ name: 'Portal', highlights: ['Launched v2'] }],
        },
        { title: 'Lead' },
      ],
      education: [{ degree: 'BS' }],
      skills: [],
    }

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    // Simulate profile selection
    act(() => {
      result.current.handleProfileSelected(profileData)
    })

    expect(result.current.selectedExperiences.has(0)).toBe(true)
    expect(result.current.selectedExperiences.has(1)).toBe(true)

    act(() => {
      result.current.handleExperienceToggle(0, false)
    })

    expect(result.current.selectedExperiences.has(0)).toBe(false)
    expect(result.current.selectedExperiences.has(1)).toBe(true)

    act(() => {
      result.current.applySelectedProfile()
    })

    expect(mockReset).toHaveBeenCalledWith(
      expect.objectContaining({
        experience: [{ title: 'Lead' }],
      })
    )
    expect(mockOnSuccess).toHaveBeenCalledWith('Profile data loaded successfully!')
  })

  it('closes profile loader and resets selections', async () => {
    const profileData = {
      personal_info: { name: 'John Doe' },
      experience: [{ title: 'Dev' }],
      education: [{ degree: 'BS' }],
      skills: [],
    }

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    // Simulate profile selection to set up the state
    act(() => {
      result.current.handleProfileSelected(profileData)
    })

    expect(result.current.showProfileLoader).toBe(true)
    expect(result.current.profileData).toBeTruthy()

    act(() => {
      result.current.closeProfileLoader()
    })

    expect(result.current.showProfileLoader).toBe(false)
    expect(result.current.profileData).toBeNull()
    expect(result.current.selectedExperiences.size).toBe(0)
    expect(result.current.selectedEducations.size).toBe(0)
  })

  it('saves to profile', async () => {
    mockedAxios.post.mockResolvedValue({ data: { status: 'success' } })

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    const cvData: CVData = {
      personal_info: { name: 'John Doe' },
      experience: [],
      education: [],
      skills: [],
    }

    await act(async () => {
      result.current.saveToProfile(cvData)
    })

    expect(mockedAxios.post).toHaveBeenCalledWith('/api/profile', {
      personal_info: cvData.personal_info,
      experience: cvData.experience,
      education: cvData.education,
      skills: cvData.skills,
    })
    expect(mockOnSuccess).toHaveBeenCalledWith('Current form data saved to profile!')
  })

  it('handles save to profile error', async () => {
    mockedAxios.post.mockRejectedValue({
      response: { data: { detail: 'Save failed' } },
    })

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    const cvData: CVData = {
      personal_info: { name: 'John Doe' },
      experience: [],
      education: [],
      skills: [],
    }

    await act(async () => {
      result.current.saveToProfile(cvData)
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Save failed')
    })
  })

  it('toggles experience and education selections', () => {
    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    act(() => {
      result.current.handleExperienceToggle(1, true)
      result.current.handleEducationToggle(2, true)
    })

    expect(result.current.selectedExperiences.has(1)).toBe(true)
    expect(result.current.selectedEducations.has(2)).toBe(true)

    act(() => {
      result.current.handleExperienceToggle(1, false)
      result.current.handleEducationToggle(2, false)
    })

    expect(result.current.selectedExperiences.has(1)).toBe(false)
    expect(result.current.selectedEducations.has(2)).toBe(false)
  })
})
