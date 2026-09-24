import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTheme } from '../../app_helpers/useTheme'

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  afterEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('initializes from localStorage dark theme', () => {
    localStorage.setItem('theme', 'dark')
    const { result } = renderHook(() => useTheme())
    expect(result.current.isDark).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('initializes from localStorage light theme', () => {
    localStorage.setItem('theme', 'light')
    const { result } = renderHook(() => useTheme())
    expect(result.current.isDark).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('initializes from system preference when no localStorage', () => {
    const mockMatchMedia = vi.fn((query: string) => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }))
    window.matchMedia = mockMatchMedia

    const { result } = renderHook(() => useTheme())
    expect(result.current.isDark).toBe(true)
  })

  it('toggles dark mode', () => {
    const { result } = renderHook(() => useTheme())
    const initialDark = result.current.isDark

    act(() => {
      result.current.setIsDark(!initialDark)
    })

    expect(result.current.isDark).toBe(!initialDark)
    expect(document.documentElement.classList.contains('dark')).toBe(!initialDark)
    expect(localStorage.getItem('theme')).toBe(!initialDark ? 'dark' : 'light')
  })

  it('toggles light mode', () => {
    localStorage.setItem('theme', 'dark')
    const { result } = renderHook(() => useTheme())

    act(() => {
      result.current.setIsDark(false)
    })

    expect(result.current.isDark).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(localStorage.getItem('theme')).toBe('light')
  })

  it('persists theme to localStorage', () => {
    const { result } = renderHook(() => useTheme())

    act(() => {
      result.current.setIsDark(true)
    })

    expect(localStorage.getItem('theme')).toBe('dark')
  })

  it('syncs the cocode.dk frame dark attribute with the theme', () => {
    document.body.innerHTML = '<cocode-head></cocode-head><cocode-foot></cocode-foot>'
    const head = document.querySelector('cocode-head')!
    const foot = document.querySelector('cocode-foot')!

    const { result } = renderHook(() => useTheme())
    act(() => {
      result.current.setIsDark(true)
    })
    expect(head.hasAttribute('dark')).toBe(true)
    expect(foot.hasAttribute('dark')).toBe(true)

    act(() => {
      result.current.setIsDark(false)
    })
    expect(head.hasAttribute('dark')).toBe(false)
    expect(foot.hasAttribute('dark')).toBe(false)

    document.body.innerHTML = ''
  })
})
