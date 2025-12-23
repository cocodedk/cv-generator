import { ViewMode } from './types'

export const hashToViewMode = (hash: string): ViewMode => {
  const normalizedHash = hash.replace(/^#/, '').toLowerCase()
  if (normalizedHash.startsWith('edit/')) {
    return 'edit'
  }
  if (normalizedHash === 'form' || normalizedHash === 'list' || normalizedHash === 'profile') {
    return normalizedHash as ViewMode
  }
  return 'form'
}

export const extractCvIdFromHash = (hash: string): string | null => {
  const normalizedHash = hash.replace(/^#/, '').toLowerCase()
  if (normalizedHash.startsWith('edit/')) {
    const cvId = normalizedHash.substring(5) // Remove 'edit/' prefix
    return cvId || null
  }
  return null
}

export const viewModeToHash = (mode: ViewMode, cvId?: string): string => {
  if (mode === 'edit' && cvId) {
    return `edit/${cvId}`
  }
  return mode
}
