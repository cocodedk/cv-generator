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

  it('loads profile successfully', async () => {
    const profileData = {
      personal_info: { name: 'John Doe' },
      experience: [{ title: 'Dev' }],
      education: [{ degree: 'BS' }],
      skills: [],
    }
    mockedAxios.get.mockResolvedValue({ data: profileData })

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      result.current.loadProfile()
    })

    await waitFor(() => {
      expect(result.current.profileData).toEqual(profileData)
      expect(result.current.showProfileLoader).toBe(true)
    })
  })

  it('handles profile not found', async () => {
    const error = { response: { status: 404 } }
    mockedAxios.get.mockRejectedValue(error)

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      result.current.loadProfile()
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('No profile found. Please save a profile first.')
    })
  })

  it('handles empty profile response', async () => {
    mockedAxios.get.mockResolvedValue({ data: null })

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      result.current.loadProfile()
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('No profile found. Please save a profile first.')
    })
  })

  it('handles unexpected load error', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Boom'))

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      result.current.loadProfile()
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to load profile')
    })
  })

  it('applies selected profile', async () => {
    const profileData = {
      personal_info: { name: 'John Doe' },
      experience: [{ title: 'Dev' }, { title: 'Lead' }],
      education: [{ degree: 'BS' }],
      skills: [],
    }
    mockedAxios.get.mockResolvedValue({ data: profileData })

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      result.current.loadProfile()
    })

    await act(async () => {
      result.current.handleExperienceToggle(0, false)
      result.current.applySelectedProfile()
    })

    expect(mockReset).toHaveBeenCalled()
    expect(mockOnSuccess).toHaveBeenCalledWith('Profile data loaded successfully!')
  })

  it('closes profile loader and resets selections', async () => {
    const profileData = {
      personal_info: { name: 'John Doe' },
      experience: [{ title: 'Dev' }],
      education: [{ degree: 'BS' }],
      skills: [],
    }
    mockedAxios.get.mockResolvedValue({ data: profileData })

    const { result } = renderHook(() =>
      useProfileManager({
        reset: mockReset,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      result.current.loadProfile()
    })

    await act(async () => {
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
