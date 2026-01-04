import { useMemo, useState } from 'react'
import { CoverLetterRequest, CoverLetterResponse } from '../../types/coverLetter'
import { generateCoverLetter } from '../../services/coverLetterService'
import RecipientFields from './RecipientFields'
import CoverLetterPreview from './CoverLetterPreview'

interface CoverLetterModalProps {
  onClose: () => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
  initialJobDescription?: string
}

const defaultPayload: CoverLetterRequest = {
  job_description: '',
  company_name: '',
  tone: 'professional',
}

function getErrorDetail(error: unknown): string | null {
  if (typeof error !== 'object' || error === null) return null
  if (!('response' in error)) return null
  const response = (error as { response?: { data?: { detail?: string } } }).response
  return response?.data?.detail || null
}

export default function CoverLetterModal({
  onClose,
  onError,
  setLoading,
  initialJobDescription = '',
}: CoverLetterModalProps) {
  const [payload, setPayload] = useState<CoverLetterRequest>({
    ...defaultPayload,
    job_description: initialJobDescription,
  })
  const [result, setResult] = useState<CoverLetterResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const canGenerate = useMemo(
    () => payload.job_description.trim().length >= 20 && payload.company_name.trim().length > 0,
    [payload.job_description, payload.company_name]
  )

  const updateField = <K extends keyof CoverLetterRequest>(
    key: K,
    value: CoverLetterRequest[K]
  ) => {
    setPayload(current => ({ ...current, [key]: value }))
  }

  const onGenerate = async () => {
    if (!canGenerate || isGenerating) return
    setIsGenerating(true)
    setLoading(true)
    setResult(null)
    try {
      const response = await generateCoverLetter(payload)
      setResult(response)
    } catch (error: unknown) {
      onError(getErrorDetail(error) || 'Failed to generate cover letter')
    } finally {
      setIsGenerating(false)
      setLoading(false)
    }
  }

  const onRegenerate = async () => {
    if (!canGenerate || isGenerating) return
    setIsGenerating(true)
    setLoading(true)
    try {
      const response = await generateCoverLetter(payload)
      setResult(response)
    } catch (error: unknown) {
      onError(getErrorDetail(error) || 'Failed to regenerate cover letter')
    } finally {
      setIsGenerating(false)
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-3xl rounded-lg bg-white shadow-lg dark:border dark:border-gray-800 dark:bg-gray-900">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Generate Cover Letter
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
          >
            Close
          </button>
        </div>

        <div className="space-y-4 p-6">
          <RecipientFields payload={payload} isGenerating={isGenerating} onChange={updateField} />
          {result ? (
            <CoverLetterPreview
              result={result}
              onError={onError}
              onRegenerate={onRegenerate}
              isRegenerating={isGenerating}
            />
          ) : null}
        </div>

        <div className="flex items-center justify-end gap-3 border-t border-gray-200 px-6 py-4 dark:border-gray-800">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            Cancel
          </button>
          {result ? (
            <button
              type="button"
              disabled={!canGenerate || isGenerating}
              onClick={onRegenerate}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-blue-500"
            >
              {isGenerating ? 'Regenerating...' : 'Regenerate'}
            </button>
          ) : (
            <button
              type="button"
              disabled={!canGenerate || isGenerating}
              onClick={onGenerate}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-blue-500"
            >
              {isGenerating ? 'Generating...' : 'Generate'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
