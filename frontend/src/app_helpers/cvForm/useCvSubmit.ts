import { useState } from 'react'
import axios from 'axios'
import { UseFormSetError } from 'react-hook-form'
import { CVData } from '../../types/cv'
import { normalizeCvDataForApi } from './normalizeCvData'

interface UseCvSubmitProps {
  cvId: string | null | undefined
  isEditMode: boolean
  onSuccess: (message: string) => void
  onError: (message: string | string[]) => void
  setLoading: (loading: boolean) => void
  setError: UseFormSetError<CVData>
}

function openPrintable(cvId: string) {
  window.open(`/api/cv/${cvId}/print-html`, '_blank', 'noopener,noreferrer')
}

function _extractFieldPath(loc: any[]): string | null {
  if (!loc || !Array.isArray(loc)) return null

  // Skip 'body' if present
  const parts = loc[0] === 'body' ? loc.slice(1) : loc

  if (parts.length === 0) return null

  // Convert to react-hook-form path (e.g., ['experience', 0, 'description'] -> 'experience.0.description')
  return parts
    .map((part, i) => {
      if (typeof part === 'number') {
        return i === 0 ? String(part) : `.${part}`
      }
      return i === 0 ? part : `.${part}`
    })
    .join('')
}

function _extractErrorMessage(error: any): string {
  const msg = error.msg || ''
  if (error.type === 'string_too_long' && error.ctx?.max_length) {
    return `Maximum ${error.ctx.max_length} characters allowed. Please shorten or move details to projects.`
  }
  return msg
}

function _scrollToField(fieldPath: string) {
  // Convert field path to element ID
  // e.g., 'experience.0.description' -> 'experience-description-0'
  const parts = fieldPath.split('.')
  let elementId = ''

  if (parts[0] === 'experience' && parts.length >= 3) {
    const index = parts[1]
    const field = parts[2]
    elementId = `experience-${field}-${index}`
  } else if (parts[0] === 'education' && parts.length >= 3) {
    const index = parts[1]
    const field = parts[2]
    elementId = `education-${field}-${index}`
  } else if (parts[0] === 'skills' && parts.length >= 3) {
    const index = parts[1]
    const field = parts[2]
    elementId = `skill-${field}-${index}`
  } else if (parts[0] === 'personal_info' && parts.length >= 2) {
    const field = parts[1]
    elementId = field === 'name' ? 'name' : `personal-info-${field}`
  }

  if (elementId) {
    setTimeout(() => {
      const element = document.getElementById(elementId)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        element.focus()
        // Add error styling
        element.classList.add('border-red-500', 'ring-2', 'ring-red-500')
        setTimeout(() => {
          element.classList.remove('ring-2', 'ring-red-500')
        }, 3000)
      }
    }, 100)
  }
}

export function useCvSubmit({
  cvId,
  isEditMode,
  onSuccess,
  onError,
  setLoading,
  setError,
}: UseCvSubmitProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const onSubmit = async (data: CVData) => {
    setIsSubmitting(true)
    setLoading(true)
    try {
      const payload = normalizeCvDataForApi(data)
      if (isEditMode && cvId) {
        await axios.put(`/api/cv/${cvId}`, payload)
        openPrintable(cvId)
        onSuccess('CV updated. Printable view opened.')
      } else {
        const response = await axios.post('/api/save-cv', payload)
        const createdCvId: string | undefined = response.data?.cv_id
        if (createdCvId) {
          window.location.hash = `edit/${createdCvId}`
          openPrintable(createdCvId)
          onSuccess('CV saved. Printable view opened.')
        } else {
          onSuccess('CV saved successfully!')
        }
      }
    } catch (error: any) {
      const errorResponse = error.response?.data
      const errorDetail = errorResponse?.detail
      const errorErrors = errorResponse?.errors || []

      // Set form field errors and scroll to first error
      let firstErrorField: string | null = null

      if (Array.isArray(errorErrors)) {
        errorErrors.forEach((err: any) => {
          const fieldPath = err.field_path || _extractFieldPath(err.loc)
          if (fieldPath) {
            const message = _extractErrorMessage(err)
            setError(fieldPath as any, {
              type: 'server',
              message,
            })
            if (!firstErrorField) {
              firstErrorField = fieldPath
            }
          }
        })
      }

      // Scroll to first error field
      if (firstErrorField) {
        _scrollToField(firstErrorField)
      }

      // Handle both string and array error messages for notification
      const errorMessage =
        errorDetail || (isEditMode ? 'Failed to update CV' : 'Failed to generate CV')
      onError(errorMessage)
    } finally {
      setIsSubmitting(false)
      setLoading(false)
    }
  }

  return { isSubmitting, onSubmit }
}
