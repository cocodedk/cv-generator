import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useHashRouting } from '../../app_helpers/useHashRouting'

describe('useHashRouting', () => {
  beforeEach(() => {
    window.location.hash = ''
  })

  it('derives view mode from hash', () => {
    window.location.hash = '#list'
    const { result } = renderHook(() => useHashRouting())

    expect(result.current.viewMode).toBe('list')
    expect(result.current.cvId).toBeNull()
  })

  it('derives edit mode and cvId from hash', () => {
    window.location.hash = '#edit/abc123'
    const { result } = renderHook(() => useHashRouting())

    expect(result.current.viewMode).toBe('edit')
    expect(result.current.cvId).toBe('abc123')
  })

  it('updates state on hash change', () => {
    const { result } = renderHook(() => useHashRouting())

    act(() => {
      window.location.hash = '#profile'
      window.dispatchEvent(new HashChangeEvent('hashchange'))
    })

    expect(result.current.viewMode).toBe('profile')
    expect(result.current.cvId).toBeNull()
  })
})
