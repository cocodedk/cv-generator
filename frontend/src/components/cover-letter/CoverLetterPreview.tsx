import { CoverLetterResponse } from '../../types/coverLetter'
import { downloadCoverLetterPDF } from '../../services/coverLetterService'

interface CoverLetterPreviewProps {
  result: CoverLetterResponse
  onError: (message: string) => void
  onRegenerate?: () => void
  isRegenerating?: boolean
}

export default function CoverLetterPreview({
  result,
  onError,
  onRegenerate,
  isRegenerating = false,
}: CoverLetterPreviewProps) {
  const handleDownloadPDF = async () => {
    try {
      await downloadCoverLetterPDF(result.cover_letter_html)
    } catch (error: any) {
      onError(error.message || 'Failed to download PDF')
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
        <div className="mb-3 flex items-center justify-between">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Preview</h4>
          <div className="flex items-center gap-2">
            {onRegenerate && (
              <button
                type="button"
                onClick={onRegenerate}
                disabled={isRegenerating}
                className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
              >
                {isRegenerating ? 'Regenerating...' : 'Regenerate'}
              </button>
            )}
            <button
              type="button"
              onClick={handleDownloadPDF}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 dark:hover:bg-blue-500"
            >
              Download PDF
            </button>
          </div>
        </div>
        <div className="cover-letter-preview-container">
          <style>{`
            .dark .cover-letter-preview-container body,
            .dark .cover-letter-preview-container .container,
            .dark .cover-letter-preview-container .sender-info,
            .dark .cover-letter-preview-container .date,
            .dark .cover-letter-preview-container .recipient-info,
            .dark .cover-letter-preview-container .cover-letter-body,
            .dark .cover-letter-preview-container .cover-letter-body p,
            .dark .cover-letter-preview-container .signature {
              color: #e5e7eb !important;
            }
            .dark .cover-letter-preview-container .sender-info .name {
              color: #10b981 !important;
            }
            .dark .cover-letter-preview-container body {
              background-color: transparent !important;
            }
          `}</style>
          <div
            className="max-h-[400px] overflow-y-auto rounded border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900"
            dangerouslySetInnerHTML={{ __html: result.cover_letter_html }}
          />
        </div>
      </div>

      {result.highlights_used.length > 0 && (
        <div className="rounded-md border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
          <h4 className="mb-2 text-sm font-semibold text-gray-900 dark:text-gray-100">
            Profile Highlights Used
          </h4>
          <ul className="list-disc space-y-1 pl-5 text-xs text-gray-700 dark:text-gray-300">
            {result.highlights_used.map((highlight, idx) => (
              <li key={idx}>{highlight}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
