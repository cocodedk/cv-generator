import { useEffect, useState } from 'react'
import { UseFormReset } from 'react-hook-form'
import axios from 'axios'
import { CVData } from '../../types/cv'
import { defaultCvData } from './cvFormDefaults'

interface UseCvLoaderProps {
  cvId: string | null | undefined
  reset: UseFormReset<CVData>
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

export function useCvLoader({ cvId, reset, onError, setLoading }: UseCvLoaderProps) {
  const [isLoadingCv, setIsLoadingCv] = useState(false)

  useEffect(() => {
    const loadCvData = async () => {
      if (!cvId) return
      setIsLoadingCv(true)
      setLoading(true)
      try {
        const response = await axios.get(`/api/cv/${cvId}`)
        const cvData = response.data
        reset({
          personal_info: cvData.personal_info || defaultCvData.personal_info,
          experience: cvData.experience || [],
          education: cvData.education || [],
          skills: cvData.skills || [],
          theme: cvData.theme || 'classic',
        })
      } catch (error: any) {
        if (error.response?.status === 404) {
          onError('CV not found')
        } else {
          onError(error.response?.data?.detail || 'Failed to load CV')
        }
      } finally {
        setIsLoadingCv(false)
        setLoading(false)
      }
    }

    if (cvId) {
      loadCvData()
    }
  }, [cvId, reset, onError, setLoading])

  return { isLoadingCv }
}
