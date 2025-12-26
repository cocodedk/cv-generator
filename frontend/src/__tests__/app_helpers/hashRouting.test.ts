import { describe, it, expect } from 'vitest'
import {
  hashToViewMode,
  extractCvIdFromHash,
  extractProfileUpdatedAtFromHash,
  viewModeToHash,
} from '../../app_helpers/hashRouting'

describe('hashRouting', () => {
  describe('hashToViewMode', () => {
    it('identifies form mode', () => {
      expect(hashToViewMode('#form')).toBe('form')
      expect(hashToViewMode('form')).toBe('form')
      expect(hashToViewMode('#FORM')).toBe('form')
    })

    it('identifies list mode', () => {
      expect(hashToViewMode('#list')).toBe('list')
      expect(hashToViewMode('list')).toBe('list')
    })

    it('identifies profile mode', () => {
      expect(hashToViewMode('#profile')).toBe('profile')
      expect(hashToViewMode('profile')).toBe('profile')
    })

    it('identifies profile-list mode', () => {
      expect(hashToViewMode('#profile-list')).toBe('profile-list')
      expect(hashToViewMode('profile-list')).toBe('profile-list')
      expect(hashToViewMode('#profiles')).toBe('profile-list')
      expect(hashToViewMode('profiles')).toBe('profile-list')
    })

    it('identifies profile-edit mode', () => {
      expect(hashToViewMode('#profile-edit/2024-01-01T00:00:00')).toBe('profile-edit')
      expect(hashToViewMode('profile-edit/2024-01-01T00:00:00')).toBe('profile-edit')
    })

    it('identifies edit mode', () => {
      expect(hashToViewMode('#edit/cv-123')).toBe('edit')
      expect(hashToViewMode('edit/cv-123')).toBe('edit')
      expect(hashToViewMode('#EDIT/CV-123')).toBe('edit')
    })

    it('defaults to form mode for unknown hashes', () => {
      expect(hashToViewMode('#unknown')).toBe('form')
      expect(hashToViewMode('')).toBe('form')
    })
  })

  describe('extractCvIdFromHash', () => {
    it('extracts CV ID from edit hash', () => {
      expect(extractCvIdFromHash('#edit/cv-123')).toBe('cv-123')
      expect(extractCvIdFromHash('edit/cv-123')).toBe('cv-123')
      expect(extractCvIdFromHash('#edit/test-id-456')).toBe('test-id-456')
    })

    it('returns null for non-edit hashes', () => {
      expect(extractCvIdFromHash('#form')).toBeNull()
      expect(extractCvIdFromHash('#list')).toBeNull()
      expect(extractCvIdFromHash('#profile')).toBeNull()
      expect(extractCvIdFromHash('')).toBeNull()
    })

    it('returns null for empty edit hash', () => {
      expect(extractCvIdFromHash('#edit/')).toBeNull()
      expect(extractCvIdFromHash('edit/')).toBeNull()
    })
  })

  describe('viewModeToHash', () => {
    it('generates hash for form mode', () => {
      expect(viewModeToHash('form')).toBe('form')
    })

    it('generates hash for list mode', () => {
      expect(viewModeToHash('list')).toBe('list')
    })

    it('generates hash for profile mode', () => {
      expect(viewModeToHash('profile')).toBe('profile')
    })

    it('generates hash for edit mode with CV ID', () => {
      expect(viewModeToHash('edit', 'cv-123')).toBe('edit/cv-123')
      expect(viewModeToHash('edit', 'test-id-456')).toBe('edit/test-id-456')
    })

    it('generates hash for edit mode without CV ID', () => {
      expect(viewModeToHash('edit')).toBe('edit')
    })

    it('generates hash for profile-list mode', () => {
      expect(viewModeToHash('profile-list')).toBe('profile-list')
    })

    it('generates hash for profile-edit mode with updated_at', () => {
      // URL encoding is applied to handle special characters in timestamps
      expect(viewModeToHash('profile-edit', undefined, '2024-01-01T00:00:00')).toBe(
        'profile-edit/2024-01-01T00%3A00%3A00'
      )
    })

    it('generates hash for profile-edit mode with special characters', () => {
      // Test that special characters are properly encoded
      const timestampWithSpecialChars = '2024-01-01T00:00:00+05:30'
      const encoded = viewModeToHash('profile-edit', undefined, timestampWithSpecialChars)
      expect(encoded).toBe('profile-edit/2024-01-01T00%3A00%3A00%2B05%3A30')
      // Verify it can be decoded back
      expect(extractProfileUpdatedAtFromHash(`#${encoded}`)).toBe(timestampWithSpecialChars)
    })

    it('generates hash for profile-edit mode without updated_at', () => {
      expect(viewModeToHash('profile-edit')).toBe('profile-edit')
    })
  })

  describe('extractProfileUpdatedAtFromHash', () => {
    it('extracts updated_at from profile-edit hash', () => {
      expect(extractProfileUpdatedAtFromHash('#profile-edit/2024-01-01T00:00:00')).toBe(
        '2024-01-01T00:00:00'
      )
      expect(extractProfileUpdatedAtFromHash('profile-edit/2024-01-01T00:00:00')).toBe(
        '2024-01-01T00:00:00'
      )
    })

    it('decodes URL-encoded updated_at from profile-edit hash', () => {
      // Test decoding of URL-encoded timestamps
      expect(extractProfileUpdatedAtFromHash('#profile-edit/2024-01-01T00%3A00%3A00')).toBe(
        '2024-01-01T00:00:00'
      )
      expect(extractProfileUpdatedAtFromHash('profile-edit/2024-01-01T00%3A00%3A00')).toBe(
        '2024-01-01T00:00:00'
      )
    })

    it('returns null for non-profile-edit hashes', () => {
      expect(extractProfileUpdatedAtFromHash('#form')).toBeNull()
      expect(extractProfileUpdatedAtFromHash('#list')).toBeNull()
      expect(extractProfileUpdatedAtFromHash('#profile')).toBeNull()
      expect(extractProfileUpdatedAtFromHash('#edit/cv-123')).toBeNull()
      expect(extractProfileUpdatedAtFromHash('')).toBeNull()
    })

    it('returns null for empty profile-edit hash', () => {
      expect(extractProfileUpdatedAtFromHash('#profile-edit/')).toBeNull()
      expect(extractProfileUpdatedAtFromHash('profile-edit/')).toBeNull()
    })
  })
})
