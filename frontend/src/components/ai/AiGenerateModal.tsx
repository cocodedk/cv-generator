import { useMemo, useState } from 'react'
import { CVData } from '../../types/cv'
import { AIGenerateCVRequest, AIGenerateCVResponse } from '../../types/ai'
import { generateCvDraft } from '../../services/aiService'
import AiGenerateFields from './AiGenerateFields'
import AiGeneratePanels from './AiGeneratePanels'

interface AiGenerateModalProps {
  onClose: () => void
  onApply: (draft: CVData) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

const defaultPayload: AIGenerateCVRequest = {
  job_description: '',
  style: 'select_and_reorder',
  max_experiences: 4,
}

function getErrorDetail(error: unknown): string | null {
  if (typeof error !== 'object' || error === null) return null
  if (!('response' in error)) return null
  const response = (error as { response?: { data?: { detail?: string } } }).response
  return response?.data?.detail || null
}

export default function AiGenerateModal({
  onClose,
  onApply,
  onError,
  setLoading,
}: AiGenerateModalProps) {
  const [payload, setPayload] = useState<AIGenerateCVRequest>(defaultPayload)
  const [result, setResult] = useState<AIGenerateCVResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const canGenerate = useMemo(
    () => payload.job_description.trim().length >= 20,
    [payload.job_description]
  )

  const updateField = <K extends keyof AIGenerateCVRequest>(
    key: K,
    value: AIGenerateCVRequest[K]
  ) => {
    setPayload(current => ({ ...current, [key]: value }))
  }

  const onGenerate = async () => {
    if (!canGenerate || isGenerating) return
    setIsGenerating(true)
    setLoading(true)
    setResult(null)
    try {
      const response = await generateCvDraft(payload)
      setResult(response)
    } catch (error: unknown) {
      onError(getErrorDetail(error) || 'Failed to generate CV draft')
    } finally {
      setIsGenerating(false)
      setLoading(false)
    }
  }

  const onApplyDraft = () => {
    if (!result) return
    onApply(result.draft_cv)
    onClose()
  }

  const onRegenerateWithAnswers = async (answers: string) => {
    if (!canGenerate || isGenerating) return
    setIsGenerating(true)
    setLoading(true)
    setResult(null)
    try {
      const existingContext = payload.additional_context?.trim()
      const newContext = existingContext ? `${existingContext}\n\n${answers}` : answers
      const updatedPayload = { ...payload, additional_context: newContext }
      setPayload(updatedPayload)
      const response = await generateCvDraft(updatedPayload)
      setResult(response)
    } catch (error: unknown) {
      onError(getErrorDetail(error) || 'Failed to regenerate CV draft')
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
            Generate CV from Job Description
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
          <AiGenerateFields
            payload={payload}
            isGenerating={isGenerating}
            canGenerate={canGenerate}
            onChange={updateField}
          />
          {result ? (
            <AiGeneratePanels
              result={result}
              isGenerating={isGenerating}
              onRegenerateWithAnswers={onRegenerateWithAnswers}
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
              onClick={onApplyDraft}
              className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 dark:hover:bg-green-500"
            >
              Apply draft to form
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
