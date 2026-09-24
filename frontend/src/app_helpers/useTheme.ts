import { useEffect, useState } from 'react'

export const useTheme = () => {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === 'undefined') {
      return false
    }
    const stored = window.localStorage.getItem('theme')
    if (stored === 'dark') {
      return true
    }
    if (stored === 'light') {
      return false
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark)
    window.localStorage.setItem('theme', isDark ? 'dark' : 'light')
    // The cocode.dk frame's own background is transparent, so it must be told
    // the app's current theme to keep its text readable against ours.
    document.querySelectorAll('cocode-head, cocode-foot').forEach(el => {
      el.toggleAttribute('dark', isDark)
    })
  }, [isDark])

  return { isDark, setIsDark }
}
