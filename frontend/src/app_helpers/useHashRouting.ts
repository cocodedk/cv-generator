import { useEffect, useState, useRef } from 'react'
import { ViewMode } from './types'
import { hashToViewMode, extractCvIdFromHash, extractProfileUpdatedAtFromHash } from './hashRouting'

export const useHashRouting = () => {
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    if (typeof window === 'undefined') {
      return 'introduction'
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

  const isUpdatingFromHashChangeRef = useRef(false)

  useEffect(() => {
    if (isUpdatingFromHashChangeRef.current) {
      isUpdatingFromHashChangeRef.current = false
      return
    }

    const currentHash = window.location.hash
    const hashViewMode = hashToViewMode(currentHash)
    const hashCvId = extractCvIdFromHash(currentHash)
    const hashProfileUpdatedAt = extractProfileUpdatedAtFromHash(currentHash)

    if (
      hashViewMode !== viewMode ||
      hashCvId !== cvId ||
      hashProfileUpdatedAt !== profileUpdatedAt
    ) {
      setViewMode(hashViewMode)
      setCvId(hashCvId)
      setProfileUpdatedAt(hashProfileUpdatedAt)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const handleHashChange = () => {
      isUpdatingFromHashChangeRef.current = true
      const newViewMode = hashToViewMode(window.location.hash)
      const newCvId = extractCvIdFromHash(window.location.hash)
      const newProfileUpdatedAt = extractProfileUpdatedAtFromHash(window.location.hash)

      setViewMode(newViewMode)
      setCvId(newCvId)
      setProfileUpdatedAt(newProfileUpdatedAt)
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => {
      window.removeEventListener('hashchange', handleHashChange)
    }
  }, [])

  return { viewMode, cvId, profileUpdatedAt }
}
