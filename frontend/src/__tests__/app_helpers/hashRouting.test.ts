import { describe, it, expect } from 'vitest'
import { hashToViewMode, extractCvIdFromHash, viewModeToHash } from '../../app_helpers/hashRouting'

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
  })
})
