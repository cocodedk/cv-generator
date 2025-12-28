import { ViewMode } from './types'

export const hashToViewMode = (hash: string): ViewMode => {
  const normalizedHash = hash.replace(/^#/, '').toLowerCase()
  if (normalizedHash.startsWith('edit/')) {
    return 'edit'
  }
  if (normalizedHash.startsWith('profile-edit/')) {
    return 'profile-edit'
  }
  if (
    normalizedHash === 'introduction' ||
    normalizedHash === 'form' ||
    normalizedHash === 'list' ||
    normalizedHash === 'profile' ||
    normalizedHash === 'profile-list' ||
    normalizedHash === 'profiles'
  ) {
    if (normalizedHash === 'profiles') {
      return 'profile-list'
    }
    return normalizedHash as ViewMode
  }
  return 'introduction'
}

export const extractCvIdFromHash = (hash: string): string | null => {
  const normalizedHash = hash.replace(/^#/, '').toLowerCase()
  if (normalizedHash.startsWith('edit/')) {
    const cvId = normalizedHash.substring(5) // Remove 'edit/' prefix
    return cvId || null
  }
  return null
}

export const extractProfileUpdatedAtFromHash = (hash: string): string | null => {
  const normalizedHash = hash.replace(/^#/, '')
  if (normalizedHash.toLowerCase().startsWith('profile-edit/')) {
    const updatedAt = normalizedHash.substring(13) // Remove 'profile-edit/' prefix (case-insensitive)
    if (!updatedAt) {
      return null
    }
    try {
      return decodeURIComponent(updatedAt)
    } catch {
      return updatedAt
    }
  }
  return null
}

export const viewModeToHash = (
  mode: ViewMode,
  cvId?: string,
  profileUpdatedAt?: string
): string => {
  if (mode === 'edit' && cvId) {
    return `edit/${cvId}`
  }
  if (mode === 'profile-edit' && profileUpdatedAt) {
    return `profile-edit/${encodeURIComponent(profileUpdatedAt)}`
  }
  if (mode === 'profile-list') {
    return 'profile-list'
  }
  return mode
}
