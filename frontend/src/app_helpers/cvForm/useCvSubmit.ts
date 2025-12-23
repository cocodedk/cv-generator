import { useState } from 'react'
import axios from 'axios'
import { CVData } from '../../types/cv'
import { openDownload } from '../download'

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
        try {
          const docxResponse = await axios.post(`/api/cv/${cvId}/generate-docx`)
          if (docxResponse.data.filename) {
            openDownload(docxResponse.data.filename)
            onSuccess('CV updated and downloaded successfully!')
          } else {
            onSuccess('CV updated successfully!')
          }
        } catch (docxError: any) {
          onError(docxError.response?.data?.detail || 'CV updated but DOCX generation failed')
        }
      } else {
        const response = await axios.post('/api/generate-cv-docx', data)
        if (response.data.filename) {
          openDownload(response.data.filename)
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
