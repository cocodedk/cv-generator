import { AIGenerateCVRequest, AIGenerateStyle } from '../../types/ai'

interface AiGenerateFieldsProps {
  payload: AIGenerateCVRequest
  isGenerating: boolean
  canGenerate: boolean
  onChange: <K extends keyof AIGenerateCVRequest>(key: K, value: AIGenerateCVRequest[K]) => void
}

export default function AiGenerateFields({
  payload,
  isGenerating,
  canGenerate,
  onChange,
}: AiGenerateFieldsProps) {
  return (
    <div className="space-y-4">
      <div className="grid gap-2">
        <label
          className="text-sm font-medium text-gray-700 dark:text-gray-300"
          htmlFor="ai_target_role"
        >
          Target role (optional)
        </label>
        <input
          id="ai_target_role"
          value={payload.target_role || ''}
          onChange={e => onChange('target_role', e.target.value || undefined)}
          className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          placeholder="e.g. Senior Frontend Engineer"
          disabled={isGenerating}
        />
      </div>

      <div className="grid gap-2 sm:grid-cols-3">
        <div className="grid gap-2">
          <label
            className="text-sm font-medium text-gray-700 dark:text-gray-300"
            htmlFor="ai_seniority"
          >
            Seniority (optional)
          </label>
          <input
            id="ai_seniority"
            value={payload.seniority || ''}
            onChange={e => onChange('seniority', e.target.value || undefined)}
            className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
            placeholder="e.g. Mid / Senior"
            disabled={isGenerating}
          />
        </div>
        <div className="grid gap-2">
          <label
            className="text-sm font-medium text-gray-700 dark:text-gray-300"
            htmlFor="ai_style"
          >
            Style
          </label>
          <select
            id="ai_style"
            value={payload.style || 'select_and_reorder'}
            onChange={e => onChange('style', e.target.value as AIGenerateStyle)}
            className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
            disabled={isGenerating}
          >
            <option value="select_and_reorder">Select & reorder</option>
            <option value="rewrite_bullets">Rewrite bullets (heuristic)</option>
          </select>
        </div>
        <div className="grid gap-2">
          <label
            className="text-sm font-medium text-gray-700 dark:text-gray-300"
            htmlFor="ai_max_exp"
          >
            Max experiences
          </label>
          <input
            id="ai_max_exp"
            type="number"
            min={1}
            max={10}
            value={payload.max_experiences || 4}
            onChange={e => onChange('max_experiences', Number(e.target.value))}
            className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
            disabled={isGenerating}
          />
        </div>
      </div>

      <div className="grid gap-2">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="ai_jd">
          Job description
        </label>
        <textarea
          id="ai_jd"
          value={payload.job_description}
          onChange={e => onChange('job_description', e.target.value)}
          className="min-h-[180px] w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          placeholder="Paste the job description here..."
          disabled={isGenerating}
        />
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Minimum 20 characters. {canGenerate ? 'Ready to generate.' : 'Keep pasting.'}
        </p>
      </div>
    </div>
  )
}
