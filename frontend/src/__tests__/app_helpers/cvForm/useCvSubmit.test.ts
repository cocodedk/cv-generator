import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import axios from 'axios'
import { UseFormSetError } from 'react-hook-form'
import { useCvSubmit } from '../../../app_helpers/cvForm/useCvSubmit'
import { CVData } from '../../../types/cv'

vi.mock('axios')
const mockedAxios = axios as any

describe('useCvSubmit', () => {
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()
  const mockSetLoading = vi.fn()
  const mockSetError = vi.fn() as unknown as UseFormSetError<CVData>
  const cvData: CVData = {
    personal_info: { name: 'John Doe' },
    experience: [
      {
        title: 'Developer',
        company: 'ACME',
        start_date: '2020-01',
        end_date: '2021-01',
        description: 'Short role summary.',
        location: 'Remote',
        projects: [
          {
            name: 'Platform',
            description: 'Internal tooling',
            url: 'https://example.com',
            technologies: ['FastAPI'],
            highlights: ['Reduced build times'],
          },
        ],
      },
    ],
    education: [],
    skills: [],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    window.open = vi.fn()
    window.location.hash = '#form'
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('creates CV successfully', async () => {
    mockedAxios.post.mockResolvedValue({
      data: { cv_id: 'test-id', status: 'success' },
    })

    const { result } = renderHook(() =>
      useCvSubmit({
        cvId: null,
        isEditMode: false,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
        setError: mockSetError,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockedAxios.post).toHaveBeenCalledWith('/api/save-cv', cvData)
    expect(window.location.hash).toBe('#edit/test-id')

    // openPrintable uses setTimeout with 100ms delay
    await act(async () => {
      vi.advanceTimersByTime(150)
    })

    expect(window.open).toHaveBeenCalledWith(
      expect.stringMatching(/^\/api\/cv\/test-id\/print-html\?t=\d+$/),
      '_blank',
      'noopener,noreferrer'
    )
    expect(mockOnSuccess).toHaveBeenCalledWith('CV saved. Printable view opened.')
  })

  it('updates CV successfully and opens printable view', async () => {
    mockedAxios.put.mockResolvedValue({
      data: { cv_id: 'test-id' },
    })

    const { result } = renderHook(() =>
      useCvSubmit({
        cvId: 'test-id',
        isEditMode: true,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
        setError: mockSetError,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockedAxios.put).toHaveBeenCalledWith('/api/cv/test-id', cvData)

    // openPrintable uses setTimeout with 100ms delay
    await act(async () => {
      vi.advanceTimersByTime(150)
    })

    expect(window.open).toHaveBeenCalledWith(
      expect.stringMatching(/^\/api\/cv\/test-id\/print-html\?t=\d+$/),
      '_blank',
      'noopener,noreferrer'
    )
    expect(mockOnSuccess).toHaveBeenCalledWith('CV updated. Printable view opened.')
  })

  it('updates CV successfully without download', async () => {
    mockedAxios.put.mockResolvedValue({ data: { cv_id: 'test-id' } })

    const { result } = renderHook(() =>
      useCvSubmit({
        cvId: 'test-id',
        isEditMode: true,
        onSuccess: mockOnSuccess,
        onError: mockOnError,
        setLoading: mockSetLoading,
        setError: mockSetError,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockedAxios.put).toHaveBeenCalledWith('/api/cv/test-id', cvData)

    // openPrintable uses setTimeout with 100ms delay
    await act(async () => {
      vi.advanceTimersByTime(150)
    })

    expect(window.open).toHaveBeenCalled()
    expect(mockOnSuccess).toHaveBeenCalledWith('CV updated. Printable view opened.')
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
        setError: mockSetError,
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
        setError: mockSetError,
      })
    )

    await act(async () => {
      await result.current.onSubmit(cvData)
    })

    expect(mockOnError).toHaveBeenCalledWith('Update failed')
  })
})
