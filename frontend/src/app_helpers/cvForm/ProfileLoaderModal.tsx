import { ProfileData } from '../../types/cv'

interface ProfileLoaderModalProps {
  profileData: ProfileData
  selectedExperiences: Set<number>
  selectedEducations: Set<number>
  onExperienceToggle: (index: number, checked: boolean) => void
  onEducationToggle: (index: number, checked: boolean) => void
  onApply: () => void
  onCancel: () => void
}

export default function ProfileLoaderModal({
  profileData,
  selectedExperiences,
  selectedEducations,
  onExperienceToggle,
  onEducationToggle,
  onApply,
  onCancel,
}: ProfileLoaderModalProps) {
  return (
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
                    onChange={e => onExperienceToggle(index, e.target.checked)}
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
                    onChange={e => onEducationToggle(index, e.target.checked)}
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
            onClick={onCancel}
            data-testid="profile-loader-cancel"
            className="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onApply}
            className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:hover:bg-blue-500"
          >
            Load Selected
          </button>
        </div>
      </div>
    </div>
  )
}
