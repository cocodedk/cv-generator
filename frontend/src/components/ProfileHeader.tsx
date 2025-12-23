/** Profile header component with load and delete buttons. */
interface ProfileHeaderProps {
  hasProfile: boolean
  isLoadingProfile: boolean
  onLoad: () => void
  onDelete: () => void
}

export default function ProfileHeader({
  hasProfile,
  isLoadingProfile,
  onLoad,
  onDelete,
}: ProfileHeaderProps) {
  return (
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
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onLoad}
            disabled={isLoadingProfile}
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoadingProfile ? 'Loading...' : hasProfile ? 'Reload Profile' : 'Load Profile'}
          </button>
          {hasProfile && (
            <button
              type="button"
              onClick={onDelete}
              className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
            >
              Delete Profile
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
