import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useMessage } from '../../app_helpers/useMessage'

describe('useMessage', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('initializes with null message', () => {
    const { result } = renderHook(() => useMessage())
    expect(result.current.message).toBe(null)
  })

  it('sets success message', () => {
    const { result } = renderHook(() => useMessage())

    act(() => {
      result.current.showMessage('success', 'Test success message')
    })

    expect(result.current.message).toEqual({
      type: 'success',
      text: 'Test success message',
    })
  })

  it('sets error message', () => {
    const { result } = renderHook(() => useMessage())

    act(() => {
      result.current.showMessage('error', 'Test error message')
    })

    expect(result.current.message).toEqual({
      type: 'error',
      text: 'Test error message',
    })
  })

  it('clears message when clearMessage is called', () => {
    const { result } = renderHook(() => useMessage())

    act(() => {
      result.current.showMessage('success', 'Test message')
    })

    expect(result.current.message).not.toBe(null)

    act(() => {
      result.current.clearMessage()
    })

    expect(result.current.message).toBe(null)
  })

  it('replaces message when new one is shown', () => {
    const { result } = renderHook(() => useMessage())

    act(() => {
      result.current.showMessage('success', 'First message')
    })

    act(() => {
      result.current.showMessage('error', 'Second message')
    })

    expect(result.current.message).toEqual({
      type: 'error',
      text: 'Second message',
    })
  })
})
