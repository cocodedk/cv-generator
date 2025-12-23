import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import PersonalInfo from './PersonalInfo'
import Experience from './Experience'
import Education from './Education'
import Skills from './Skills'
import { ProfileData } from '../types/cv'
import axios from 'axios'

interface ProfileManagerProps {
  onSuccess: (message: string) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

export default function ProfileManager({ onSuccess, onError, setLoading }: ProfileManagerProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hasProfile, setHasProfile] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<ProfileData>({
    defaultValues: {
      personal_info: {
        name: '',
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
    },
  })

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    setIsLoadingProfile(true)
    try {
      const response = await axios.get('/api/profile')
      if (response.data) {
        reset(response.data)
        setHasProfile(true)
      } else {
        setHasProfile(false)
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        setHasProfile(false)
      } else {
        onError('Failed to load profile')
      }
    } finally {
      setIsLoadingProfile(false)
    }
  }

  const onSubmit = async (data: ProfileData) => {
    setIsSubmitting(true)
    setLoading(true)
    try {
      await axios.post('/api/profile', data)
      setHasProfile(true)
      onSuccess('Profile saved successfully!')
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to save profile')
    } finally {
      setIsSubmitting(false)
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete your profile? This action cannot be undone.')) {
      return
    }

    setLoading(true)
    try {
      await axios.delete('/api/profile')
      reset({
        personal_info: {
          name: '',
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
      })
      setHasProfile(false)
      onSuccess('Profile deleted successfully!')
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to delete profile')
    } finally {
      setLoading(false)
    }
  }

  if (isLoadingProfile) {
    return (
      <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800 p-6">
        <p className="text-gray-600 dark:text-gray-400">Loading profile...</p>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Master Profile</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {hasProfile
                ? 'Your profile is saved. Update it below.'
                : 'Save your information once and reuse it for all CVs.'}
            </p>
          </div>
          {hasProfile && (
            <button
              type="button"
              onClick={handleDelete}
              className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
            >
              Delete Profile
            </button>
          )}
        </div>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-8">
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
            Reset
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed dark:hover:bg-blue-500"
          >
            {isSubmitting ? 'Saving...' : hasProfile ? 'Update Profile' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  )
}
