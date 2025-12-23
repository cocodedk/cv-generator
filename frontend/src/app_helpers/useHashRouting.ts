import { useEffect, useState } from 'react'
import { ViewMode } from './types'
import { hashToViewMode, viewModeToHash, extractCvIdFromHash } from './hashRouting'

export const useHashRouting = () => {
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    if (typeof window === 'undefined') {
      return 'form'
    }
    return hashToViewMode(window.location.hash)
  })
  const [cvId, setCvId] = useState<string | null>(() => {
    if (typeof window === 'undefined') {
      return null
    }
    return extractCvIdFromHash(window.location.hash)
  })

  useEffect(() => {
    const currentHash = window.location.hash
    const hashViewMode = hashToViewMode(currentHash)
    const hashCvId = extractCvIdFromHash(currentHash)
    const expectedHash = viewModeToHash(viewMode, cvId || undefined)

    if (hashViewMode !== viewMode || hashCvId !== cvId) {
      const normalizedCurrentHash = currentHash.replace(/^#/, '')
      if (normalizedCurrentHash !== expectedHash) {
        window.location.hash = expectedHash
      }
    }
  }, [viewMode, cvId])

  useEffect(() => {
    const handleHashChange = () => {
      const newViewMode = hashToViewMode(window.location.hash)
      const newCvId = extractCvIdFromHash(window.location.hash)
      if (newViewMode !== viewMode || newCvId !== cvId) {
        setViewMode(newViewMode)
        setCvId(newCvId)
      }
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => {
      window.removeEventListener('hashchange', handleHashChange)
    }
  }, [viewMode, cvId])

  return { viewMode, cvId }
}
