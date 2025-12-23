import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import axios from 'axios'
import { useCvSubmit } from '../../../app_helpers/cvForm/useCvSubmit'
import { CVData } from '../../../types/cv'

vi.mock('axios')
const mockedAxios = axios as any

describe('useCvSubmit', () => {
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()
  const mockSetLoading = vi.fn()
  const cvData: CVData = {
    personal_info: { name: 'John Doe' },
    experience: [],
    education: [],
    skills: [],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    window.open = vi.fn()
  })

  it('creates CV successfully', async () => {
    mockedAxios.post.mockResolvedValue({
      data: { cv_id: 'test-id', filename: 'cv_test.odt' },
    })

    const { result } = renderHook(() =>
      useCvSubmit({
        cvId: null,
        isEditMode: false,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockedAxios.post).toHaveBeenCalledWith('/api/generate-cv', cvData)
    expect(window.open).toHaveBeenCalledWith(
      expect.stringMatching(/^\/api\/download\/cv_test\.odt\?t=\d+$/),
      '_blank'
    )
    expect(mockOnSuccess).toHaveBeenCalledWith('CV generated and downloaded successfully!')
  })

  it('updates CV successfully with download', async () => {
    mockedAxios.put.mockResolvedValue({
      data: { cv_id: 'test-id', filename: 'cv_test.odt' },
    })

    const { result } = renderHook(() =>
      useCvSubmit({
        cvId: 'test-id',
        isEditMode: true,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockedAxios.put).toHaveBeenCalledWith('/api/cv/test-id', cvData)
    expect(window.open).toHaveBeenCalledWith(
      expect.stringMatching(/^\/api\/download\/cv_test\.odt\?t=\d+$/),
      '_blank'
    )
    expect(mockOnSuccess).toHaveBeenCalledWith('CV updated and downloaded successfully!')
  })

  it('updates CV successfully without filename', async () => {
    mockedAxios.put.mockResolvedValue({ data: { cv_id: 'test-id' } })

    const { result } = renderHook(() =>
      useCvSubmit({
        cvId: 'test-id',
        isEditMode: true,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockedAxios.put).toHaveBeenCalledWith('/api/cv/test-id', cvData)
    expect(window.open).not.toHaveBeenCalled()
    expect(mockOnSuccess).toHaveBeenCalledWith('CV updated successfully!')
  })

  it('handles create error', async () => {
    const error = {
      response: { data: { detail: 'Create failed' } },
    }
    mockedAxios.post.mockRejectedValue(error)

    const { result } = renderHook(() =>
      useCvSubmit({
        cvId: null,
        isEditMode: false,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockOnError).toHaveBeenCalledWith('Create failed')
  })

  it('handles update error', async () => {
    const error = {
      response: { data: { detail: 'Update failed' } },
    }
    mockedAxios.put.mockRejectedValue(error)

    const { result } = renderHook(() =>
      useCvSubmit({
        cvId: 'test-id',
        isEditMode: true,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockOnError).toHaveBeenCalledWith('Update failed')
  })
})
