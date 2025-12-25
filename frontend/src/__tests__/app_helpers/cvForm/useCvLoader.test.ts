import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import axios from 'axios'
import { useCvLoader } from '../../../app_helpers/cvForm/useCvLoader'

vi.mock('axios')
const mockedAxios = axios as any

describe('useCvLoader', () => {
  const mockReset = vi.fn()
  const mockOnError = vi.fn()
  const mockSetLoading = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads CV successfully', async () => {
    const cvData = {
      personal_info: { name: 'John Doe' },
      experience: [
        {
          title: 'Dev',
          company: 'ACME',
          start_date: '2020-01',
          projects: [
            {
              name: 'Billing Revamp',
              technologies: ['React', 'TypeScript'],
              highlights: ['Shipped new checkout'],
            },
          ],
        },
      ],
      education: [],
      skills: [],
    }
    mockedAxios.get.mockResolvedValue({ data: cvData })

    renderHook(() =>
      useCvLoader({
        cvId: 'test-id',
        reset: mockReset,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/cv/test-id')
      expect(mockReset).toHaveBeenCalledWith(
        expect.objectContaining({
          experience: [
            expect.objectContaining({
              projects: [
                expect.objectContaining({
                  name: 'Billing Revamp',
                }),
              ],
            }),
          ],
        })
      )
    })
  })

  it('handles 404 error', async () => {
    const error = { response: { status: 404 } }
    mockedAxios.get.mockRejectedValue(error)

    renderHook(() =>
      useCvLoader({
        cvId: 'non-existent',
        reset: mockReset,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('CV not found')
    })
  })

  it('handles other errors', async () => {
    const error = {
      response: { status: 500, data: { detail: 'Server error' } },
    }
    mockedAxios.get.mockRejectedValue(error)

    renderHook(() =>
      useCvLoader({
        cvId: 'test-id',
        reset: mockReset,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Server error')
    })
  })

  it('does not load when cvId is null', () => {
    renderHook(() =>
      useCvLoader({
        cvId: null,
        reset: mockReset,
        onError: mockOnError,
        setLoading: mockSetLoading,
      })
    )

    expect(mockedAxios.get).not.toHaveBeenCalled()
  })
})
