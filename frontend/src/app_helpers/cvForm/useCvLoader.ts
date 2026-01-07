import { useEffect, useState, useRef } from 'react'
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
  const callbacksRef = useRef({ onError, setLoading, reset })
  const loadingRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    callbacksRef.current = { onError, setLoading, reset }
  }, [onError, setLoading, reset])

  useEffect(() => {
    const loadCvData = async () => {
      if (!cvId) return

      if (loadingRef.current.has(cvId)) {
        return
      }

      loadingRef.current.add(cvId)
      setIsLoadingCv(true)
      callbacksRef.current.setLoading(true)
      try {
        const response = await axios.get(`/api/cv/${cvId}`)
        const cvData = response.data
        callbacksRef.current.reset({
          personal_info: cvData.personal_info || defaultCvData.personal_info,
          experience: cvData.experience || [],
          education: cvData.education || [],
          skills: cvData.skills || [],
          theme: cvData.theme || 'classic',
          layout: cvData.layout || 'classic-two-column',
          target_company: cvData.target_company || '',
          target_role: cvData.target_role || '',
        })
      } catch (error: any) {
        if (error.response?.status === 404) {
          callbacksRef.current.onError('CV not found')
        } else {
          callbacksRef.current.onError(error.response?.data?.detail || 'Failed to load CV')
        }
      } finally {
        loadingRef.current.delete(cvId)
        setIsLoadingCv(false)
        callbacksRef.current.setLoading(false)
      }
    }

    if (cvId) {
      loadCvData()
    }
  }, [cvId])

  return { isLoadingCv }
}
