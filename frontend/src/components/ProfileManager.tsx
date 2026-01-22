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
  translateProfile,
} from '../services/profileService'
import { defaultProfileData } from '../constants/profileDefaults'
import { useHashRouting } from '../app_helpers/useHashRouting'
import { LANGUAGE_NAMES } from '../utils/languageUtils'

export const LANGUAGE_OPTIONS = Object.entries(LANGUAGE_NAMES)
  .filter(([code]) => code !== 'en') // Exclude English as it's not a translation target
  .map(([value, label]) => ({ value, label }))

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
  const [isTranslating, setIsTranslating] = useState(false)
  const [targetLanguage, setTargetLanguage] = useState('es')
  const [shouldCreateNewProfile, setShouldCreateNewProfile] = useState(false)
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
        await saveProfile(data, shouldCreateNewProfile)
        setHasProfile(true)
        setShouldCreateNewProfile(false) // Reset flag after saving
        onSuccess('Profile saved successfully!')
      } catch (error: any) {
        onError(error.message)
      } finally {
        setIsSubmitting(false)
        setLoading(false)
      }
    },
    [setLoading, onSuccess, onError, shouldCreateNewProfile]
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
        // If not found (timestamp changed after update), fallback to most recent
        if (!profile) {
          profile = await getProfile()
          // Update URL with current timestamp to prevent future issues
          if (profile?.updated_at) {
            window.location.hash = `#profile-edit/${encodeURIComponent(profile.updated_at)}`
          }
        }
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

  const handleTranslatedProfile = (translatedProfile: ProfileData, targetLanguage: string) => {
    reset(translatedProfile)
    setShouldCreateNewProfile(true)
    setHasProfile(false)
    onSuccess(`Profile translated to ${targetLanguage.toUpperCase()} and saved successfully!`)
  }

  const handleTranslate = async () => {
    const currentValues = control._formValues as ProfileData
    if (!currentValues || Object.keys(currentValues).length === 0) {
      onError('No profile data to translate')
      return
    }

    setIsTranslating(true)
    try {
      const response = await translateProfile(currentValues, targetLanguage)

      // Check if a profile already exists with the target language
      if (response.saved_profile_updated_at) {
        // Load the existing profile and update it
        const existingProfile = await getProfileByUpdatedAt(response.saved_profile_updated_at)
        if (existingProfile) {
          // Update the existing profile with translated data
          const updatedProfile = {
            ...existingProfile,
            ...response.translated_profile,
            updated_at: existingProfile.updated_at, // Keep the original updated_at
          }
          reset(updatedProfile)
          setShouldCreateNewProfile(false) // Mark that this should update the existing profile
          setHasProfile(true) // Update UI to show "Update Profile"
          onSuccess(
            `Existing profile updated with translation to ${targetLanguage.toUpperCase()} and saved successfully!`
          )
        } else {
          // Fallback: create new profile if existing profile not found
          handleTranslatedProfile(response.translated_profile, targetLanguage)
        }
      } else {
        // No existing profile: create new one
        handleTranslatedProfile(response.translated_profile, targetLanguage)
      }
    } catch (error: any) {
      onError(error.message)
    } finally {
      setIsTranslating(false)
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

        {/* Top Action Bar */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Language Selector */}
              <div className="flex items-center space-x-2">
                <label
                  htmlFor="target-language"
                  className="text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  Translate to:
                </label>
                <select
                  id="target-language"
                  value={targetLanguage}
                  onChange={e => setTargetLanguage(e.target.value)}
                  className="block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
                  disabled={isTranslating}
                >
                  {LANGUAGE_OPTIONS.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={handleTranslate}
                  disabled={isTranslating}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed dark:focus:ring-offset-gray-800"
                >
                  {isTranslating ? (
                    <>
                      <svg
                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Translating...
                    </>
                  ) : (
                    <>
                      <svg
                        className="-ml-1 mr-2 h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
                        ></path>
                      </svg>
                      Translate
                    </>
                  )}
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {/* Top Save Button */}
              <button
                type="button"
                onClick={() => handleSubmit(onSubmit)()}
                disabled={isSubmitting}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed dark:hover:bg-blue-500"
              >
                {isSubmitting ? (
                  <>
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Saving...
                  </>
                ) : (
                  <>
                    <svg
                      className="-ml-1 mr-2 h-4 w-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M5 13l4 4L19 7"
                      ></path>
                    </svg>
                    {hasProfile ? 'Update Profile' : 'Save Profile'}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

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
