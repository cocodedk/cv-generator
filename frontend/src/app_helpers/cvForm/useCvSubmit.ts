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
        onSuccess('CV updated successfully!')
      } else {
        const response = await axios.post('/api/generate-cv', data)
        if (response.data.filename) {
          const downloadUrl = `/api/download/${response.data.filename}`
          window.open(downloadUrl, '_blank')
          onSuccess('CV generated and downloaded successfully!')
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
