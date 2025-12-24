import { useState } from 'react'
import axios from 'axios'
import { CVData } from '../../types/cv'

interface UseCvSubmitProps {
  cvId: string | null | undefined
  isEditMode: boolean
  onSuccess: (message: string) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

function openPrintable(cvId: string) {
  window.open(`/api/cv/${cvId}/print-html`, '_blank', 'noopener,noreferrer')
}

export function useCvSubmit({
  cvId,
  isEditMode,
  onSuccess,
  onError,
  setLoading,
}: UseCvSubmitProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const onSubmit = async (data: CVData) => {
    setIsSubmitting(true)
    setLoading(true)
    try {
      if (isEditMode && cvId) {
        await axios.put(`/api/cv/${cvId}`, data)
        openPrintable(cvId)
        onSuccess('CV updated. Printable view opened.')
      } else {
        const response = await axios.post('/api/save-cv', data)
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
      onError(
        error.response?.data?.detail ||
          (isEditMode ? 'Failed to update CV' : 'Failed to generate CV')
      )
    } finally {
      setIsSubmitting(false)
      setLoading(false)
    }
  }

  return { isSubmitting, onSubmit }
}
