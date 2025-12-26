import { useState, useEffect } from 'react'
import { listProfiles, getProfileByUpdatedAt } from '../services/profileService'
import { ProfileListItem, ProfileData } from '../types/cv'

interface ProfileSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (profile: ProfileData) => void
  onError: (message: string) => void
}

export default function ProfileSelectionModal({
  isOpen,
  onClose,
  onSelect,
  onError,
}: ProfileSelectionModalProps) {
  const [profiles, setProfiles] = useState<ProfileListItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(false)

  useEffect(() => {
    if (isOpen) {
      loadProfiles()
    }
  }, [isOpen])

  const loadProfiles = async () => {
    setIsLoading(true)
    try {
      const response = await listProfiles()
      setProfiles(response.profiles)
    } catch (error: any) {
      onError(error.message || 'Failed to load profiles')
      onClose()
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectProfile = async (updatedAt: string) => {
    setIsLoadingProfile(true)
    try {
      const profile = await getProfileByUpdatedAt(updatedAt)
      if (profile) {
        onSelect(profile)
        onClose()
      } else {
        onError('Profile not found')
      }
    } catch (error: any) {
      onError(error.message || 'Failed to load profile')
    } finally {
      setIsLoadingProfile(false)
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    } catch {
      return dateString
    }
  }

  if (!isOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Select Profile to Load
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
            aria-label="Close"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {isLoading ? (
          <div className="py-8 text-center">
            <p className="text-gray-600 dark:text-gray-400">Loading profiles...</p>
          </div>
        ) : profiles.length === 0 ? (
          <div className="py-8 text-center">
            <p className="text-gray-600 dark:text-gray-400">No profiles found.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {profiles.map(profile => (
              <button
                key={profile.updated_at}
                type="button"
                onClick={() => handleSelectProfile(profile.updated_at)}
                disabled={isLoadingProfile}
                className="w-full text-left p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {profile.name}
                  </span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {formatDate(profile.updated_at)}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}

        <div className="flex justify-end mt-6">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
