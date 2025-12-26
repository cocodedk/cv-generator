import { useState, useEffect, useRef, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import PersonalInfo from './PersonalInfo'
import Experience from './Experience'
import Education from './Education'
import Skills from './Skills'
import ProfileHeader from './ProfileHeader'
import ProfileSelectionModal from './ProfileSelectionModal'
import { ProfileData } from '../types/cv'
import {
  getProfile,
  getProfileByUpdatedAt,
  saveProfile,
  deleteProfile,
} from '../services/profileService'
import { defaultProfileData } from '../constants/profileDefaults'
import { useHashRouting } from '../app_helpers/useHashRouting'

interface ProfileManagerProps {
  onSuccess: (message: string) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

export default function ProfileManager({ onSuccess, onError, setLoading }: ProfileManagerProps) {
  const { profileUpdatedAt } = useHashRouting()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hasProfile, setHasProfile] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(true)
  const [showProfileSelectionModal, setShowProfileSelectionModal] = useState(false)
  const formRef = useRef<HTMLFormElement>(null)
  const isSubmittingRef = useRef(isSubmitting)
  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<ProfileData>({
    defaultValues: defaultProfileData,
  })

  // Keep ref in sync with state
  useEffect(() => {
    isSubmittingRef.current = isSubmitting
  }, [isSubmitting])

  const onSubmit = useCallback(
    async (data: ProfileData) => {
      setIsSubmitting(true)
      setLoading(true)
      try {
        await saveProfile(data)
        setHasProfile(true)
        onSuccess('Profile saved successfully!')
      } catch (error: any) {
        onError(error.message)
      } finally {
        setIsSubmitting(false)
        setLoading(false)
      }
    },
    [setLoading, onSuccess, onError]
  )

  useEffect(() => {
    loadInitialProfile()
  }, [profileUpdatedAt])

  // Keyboard shortcut handler for Ctrl+S / Cmd+S
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check for Ctrl+S (Windows/Linux) or Cmd+S (Mac)
      // Handle both lowercase 's' and uppercase 'S' (though 's' should be standard)
      if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
        e.preventDefault() // Prevent browser save dialog
        e.stopPropagation() // Prevent event from bubbling

        // Don't trigger if form is still loading
        if (isLoadingProfile) {
          return
        }

        // Don't trigger if already submitting
        if (isSubmittingRef.current) {
          return
        }

        // Don't trigger if user is typing in an input/textarea/rich text editor
        const activeElement = document.activeElement
        if (
          activeElement &&
          (activeElement.tagName === 'INPUT' ||
            activeElement.tagName === 'TEXTAREA' ||
            activeElement.getAttribute('contenteditable') === 'true' ||
            activeElement.closest('[contenteditable="true"]'))
        ) {
          return
        }

        // Ensure form is ready
        if (!formRef.current) {
          return
        }

        // Trigger form submission directly using handleSubmit
        // This ensures validation is run and form state is properly handled
        handleSubmit(onSubmit)()
      }
    }

    document.addEventListener('keydown', handleKeyDown, true) // Use capture phase
    return () => {
      document.removeEventListener('keydown', handleKeyDown, true)
    }
  }, [handleSubmit, onSubmit, isLoadingProfile])

  const loadProfile = async () => {
    setShowProfileSelectionModal(true)
  }

  const handleProfileSelected = (profile: ProfileData) => {
    reset(profile)
    setHasProfile(true)
    onSuccess('Profile loaded successfully!')
  }

  const loadInitialProfile = async () => {
    setIsLoadingProfile(true)
    try {
      let profile: ProfileData | null = null
      if (profileUpdatedAt) {
        // Load specific profile from hash
        profile = await getProfileByUpdatedAt(profileUpdatedAt)
      } else {
        // Load most recent profile
        profile = await getProfile()
      }
      if (profile) {
        reset(profile)
        setHasProfile(true)
      } else {
        reset(defaultProfileData)
        setHasProfile(false)
      }
    } catch (error: any) {
      setHasProfile(false)
      onError(`Failed to load profile: ${error.message || 'Unknown error'}`)
    } finally {
      setIsLoadingProfile(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete your profile? This action cannot be undone.')) {
      return
    }

    setLoading(true)
    try {
      await deleteProfile()
      reset(defaultProfileData)
      setHasProfile(false)
      onSuccess('Profile deleted successfully!')
    } catch (error: any) {
      onError(error.message)
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
    <>
      <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800">
        <ProfileHeader
          hasProfile={hasProfile}
          isLoadingProfile={isLoadingProfile}
          onLoad={loadProfile}
          onDelete={handleDelete}
        />
        <form ref={formRef} onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-8">
          <PersonalInfo register={register} errors={errors} control={control} showAiAssist={true} />
          <Experience control={control} register={register} errors={errors} showAiAssist={true} />
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
      <ProfileSelectionModal
        isOpen={showProfileSelectionModal}
        onClose={() => setShowProfileSelectionModal(false)}
        onSelect={handleProfileSelected}
        onError={onError}
      />
    </>
  )
}
