import { useState } from 'react'
import { useForm } from 'react-hook-form'
import PersonalInfo from './PersonalInfo'
import Experience from './Experience'
import Education from './Education'
import Skills from './Skills'
import { CVData } from '../types/cv'
import axios from 'axios'

interface CVFormProps {
  onSuccess: (message: string) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

export default function CVForm({ onSuccess, onError, setLoading }: CVFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { register, handleSubmit, control, formState: { errors } } = useForm<CVData>({
    defaultValues: {
      personal_info: {
        name: '',
        email: '',
        phone: '',
        address: '',
        linkedin: '',
        github: '',
        website: '',
        summary: ''
      },
      experience: [],
      education: [],
      skills: []
    }
  })

  const onSubmit = async (data: CVData) => {
    setIsSubmitting(true)
    setLoading(true)
    try {
      const response = await axios.post('/api/generate-cv', data)
      if (response.data.filename) {
        // Download the file
        const downloadUrl = `/api/download/${response.data.filename}`
        window.open(downloadUrl, '_blank')
        onSuccess('CV generated and downloaded successfully!')
      } else {
        onSuccess('CV saved successfully!')
      }
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to generate CV')
    } finally {
      setIsSubmitting(false)
      setLoading(false)
    }
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Create Your CV</h2>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-8">
        <PersonalInfo register={register} errors={errors} />
        <Experience control={control} register={register} />
        <Education control={control} register={register} />
        <Skills control={control} register={register} />

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            className="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Generating...' : 'Generate CV'}
          </button>
        </div>
      </form>
    </div>
  )
}
