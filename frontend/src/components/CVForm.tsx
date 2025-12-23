import { useState } from 'react'
import { useForm } from 'react-hook-form'
import PersonalInfo from './PersonalInfo'
import Experience from './Experience'
import Education from './Education'
import Skills from './Skills'
import { CVData, ProfileData } from '../types/cv'
import axios from 'axios'

interface CVFormProps {
  onSuccess: (message: string) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

export default function CVForm({ onSuccess, onError, setLoading }: CVFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showProfileLoader, setShowProfileLoader] = useState(false)
  const [profileData, setProfileData] = useState<ProfileData | null>(null)
  const [selectedExperiences, setSelectedExperiences] = useState<Set<number>>(new Set())
  const [selectedEducations, setSelectedEducations] = useState<Set<number>>(new Set())
  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<CVData>({
    defaultValues: {
      personal_info: {
        name: '',
        title: '',
        email: '',
        phone: '',
        address: {
          street: '',
          city: '',
          state: '',
          zip: '',
          country: '',
        },
        linkedin: '',
        github: '',
        website: '',
        summary: '',
      },
      experience: [],
      education: [],
      skills: [],
      theme: 'classic',
    },
  })

  const loadProfile = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/profile')
      if (response.data) {
        setProfileData(response.data)
        setShowProfileLoader(true)
        // Pre-select all items
        const expIndices = new Set(response.data.experience.map((_: any, i: number) => i))
        const eduIndices = new Set(response.data.education.map((_: any, i: number) => i))
        setSelectedExperiences(expIndices)
        setSelectedEducations(eduIndices)
      } else {
        onError('No profile found. Please save a profile first.')
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        onError('No profile found. Please save a profile first.')
      } else {
        onError('Failed to load profile')
      }
    } finally {
      setLoading(false)
    }
  }

  const applySelectedProfile = () => {
    if (!profileData) return

    const selectedExp = profileData.experience.filter((_, i) => selectedExperiences.has(i))
    const selectedEdu = profileData.education.filter((_, i) => selectedEducations.has(i))

    reset({
      personal_info: profileData.personal_info,
      experience: selectedExp,
      education: selectedEdu,
      skills: profileData.skills,
      theme: 'classic',
    })

    setShowProfileLoader(false)
    setProfileData(null)
    setSelectedExperiences(new Set())
    setSelectedEducations(new Set())
    onSuccess('Profile data loaded successfully!')
  }

  const saveToProfile = async () => {
    setLoading(true)
    try {
      const formData = control._formValues as CVData
      const profileData: ProfileData = {
        personal_info: formData.personal_info,
        experience: formData.experience,
        education: formData.education,
        skills: formData.skills,
      }
      await axios.post('/api/profile', profileData)
      onSuccess('Current form data saved to profile!')
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to save to profile')
    } finally {
      setLoading(false)
    }
  }

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
    <>
      {showProfileLoader && profileData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Select Items to Include
            </h3>

            {profileData.experience.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                  Experiences
                </h4>
                <div className="space-y-2">
                  {profileData.experience.map((exp, index) => (
                    <label
                      key={index}
                      className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={selectedExperiences.has(index)}
                        onChange={e => {
                          const newSet = new Set(selectedExperiences)
                          if (e.target.checked) {
                            newSet.add(index)
                          } else {
                            newSet.delete(index)
                          }
                          setSelectedExperiences(newSet)
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <span className="font-medium text-gray-900 dark:text-gray-100">
                          {exp.title}
                        </span>
                        <span className="text-gray-600 dark:text-gray-400"> at {exp.company}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {profileData.education.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                  Education
                </h4>
                <div className="space-y-2">
                  {profileData.education.map((edu, index) => (
                    <label
                      key={index}
                      className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={selectedEducations.has(index)}
                        onChange={e => {
                          const newSet = new Set(selectedEducations)
                          if (e.target.checked) {
                            newSet.add(index)
                          } else {
                            newSet.delete(index)
                          }
                          setSelectedEducations(newSet)
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <span className="font-medium text-gray-900 dark:text-gray-100">
                          {edu.degree}
                        </span>
                        <span className="text-gray-600 dark:text-gray-400">
                          {' '}
                          from {edu.institution}
                        </span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end space-x-4 mt-6">
              <button
                type="button"
                onClick={() => {
                  setShowProfileLoader(false)
                  setProfileData(null)
                  setSelectedExperiences(new Set())
                  setSelectedEducations(new Set())
                }}
                className="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={applySelectedProfile}
                className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:hover:bg-blue-500"
              >
                Load Selected
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Create Your CV</h2>
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={loadProfile}
                className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
              >
                Load from Profile
              </button>
              <button
                type="button"
                onClick={saveToProfile}
                className="px-4 py-2 text-sm font-medium text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
              >
                Save to Profile
              </button>
            </div>
          </div>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-8">
          <div className="grid gap-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="theme">
              Theme
            </label>
            <select
              id="theme"
              {...register('theme')}
              className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            >
              <option value="classic">Classic</option>
              <option value="modern">Modern</option>
              <option value="minimal">Minimal</option>
              <option value="elegant">Elegant</option>
              <option value="accented">Accented</option>
            </select>
          </div>
          <PersonalInfo register={register} errors={errors} />
          <Experience control={control} register={register} />
          <Education control={control} register={register} />
          <Skills control={control} register={register} />

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => reset()}
              className="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed dark:hover:bg-blue-500"
            >
              {isSubmitting ? 'Generating...' : 'Generate CV'}
            </button>
          </div>
        </form>
      </div>
    </>
  )
}
