import { useEffect, useState } from 'react'
import { ViewMode } from './types'
import {
  hashToViewMode,
  viewModeToHash,
  extractCvIdFromHash,
  extractProfileUpdatedAtFromHash,
} from './hashRouting'

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
  const [profileUpdatedAt, setProfileUpdatedAt] = useState<string | null>(() => {
    if (typeof window === 'undefined') {
      return null
    }
    return extractProfileUpdatedAtFromHash(window.location.hash)
  })

  useEffect(() => {
    const currentHash = window.location.hash
    const hashViewMode = hashToViewMode(currentHash)
    const hashCvId = extractCvIdFromHash(currentHash)
    const hashProfileUpdatedAt = extractProfileUpdatedAtFromHash(currentHash)
    const expectedHash = viewModeToHash(viewMode, cvId || undefined, profileUpdatedAt || undefined)

    if (
      hashViewMode !== viewMode ||
      hashCvId !== cvId ||
      hashProfileUpdatedAt !== profileUpdatedAt
    ) {
      const normalizedCurrentHash = currentHash.replace(/^#/, '')
      if (normalizedCurrentHash !== expectedHash) {
        window.location.hash = expectedHash
      }
    }
  }, [viewMode, cvId, profileUpdatedAt])

  useEffect(() => {
    const handleHashChange = () => {
      const newViewMode = hashToViewMode(window.location.hash)
      const newCvId = extractCvIdFromHash(window.location.hash)
      const newProfileUpdatedAt = extractProfileUpdatedAtFromHash(window.location.hash)
      if (
        newViewMode !== viewMode ||
        newCvId !== cvId ||
        newProfileUpdatedAt !== profileUpdatedAt
      ) {
        setViewMode(newViewMode)
        setCvId(newCvId)
        setProfileUpdatedAt(newProfileUpdatedAt)
      }
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => {
      window.removeEventListener('hashchange', handleHashChange)
    }
  }, [viewMode, cvId, profileUpdatedAt])

  return { viewMode, cvId, profileUpdatedAt }
}
