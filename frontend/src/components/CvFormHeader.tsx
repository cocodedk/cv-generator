interface CvFormHeaderProps {
  title: string
  onLoadProfile: () => void
  onSaveProfile: () => void
  onGenerateFromJd: () => void
  onGenerateCoverLetter?: () => void
  onDownloadPdf?: () => void
  isGeneratingPdf?: boolean
}

export default function CvFormHeader({
  title,
  onLoadProfile,
  onSaveProfile,
  onGenerateFromJd,
  onGenerateCoverLetter,
  onDownloadPdf,
  isGeneratingPdf = false,
}: CvFormHeaderProps) {
  return (
    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{title}</h2>
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={onLoadProfile}
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Load from Profile
          </button>
          <button
            type="button"
            onClick={onSaveProfile}
            className="px-4 py-2 text-sm font-medium text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
          >
            Save to Profile
          </button>
          <button
            type="button"
            onClick={onGenerateFromJd}
            className="px-4 py-2 text-sm font-medium text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
          >
            Generate from JD
          </button>
          {onGenerateCoverLetter && (
            <button
              type="button"
              onClick={onGenerateCoverLetter}
              className="px-4 py-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
            >
              Cover Letter
            </button>
          )}
          {onDownloadPdf && (
            <button
              type="button"
              onClick={onDownloadPdf}
              disabled={isGeneratingPdf}
              className="px-4 py-2 text-sm font-medium text-orange-600 hover:text-orange-700 dark:text-orange-400 dark:hover:text-orange-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGeneratingPdf ? 'Generating...' : 'Download PDF'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
