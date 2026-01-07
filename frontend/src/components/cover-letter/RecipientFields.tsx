import { CoverLetterRequest } from '../../types/coverLetter'

interface RecipientFieldsProps {
  payload: CoverLetterRequest
  isGenerating: boolean
  onChange: <K extends keyof CoverLetterRequest>(key: K, value: CoverLetterRequest[K]) => void
}

export default function RecipientFields({ payload, isGenerating, onChange }: RecipientFieldsProps) {
  return (
    <div className="space-y-4">
      <div className="grid gap-2">
        <label
          className="text-sm font-medium text-gray-700 dark:text-gray-300"
          htmlFor="cl_company_name"
        >
          Company Name *
        </label>
        <input
          id="cl_company_name"
          value={payload.company_name}
          onChange={e => onChange('company_name', e.target.value)}
          className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          placeholder="e.g. Acme Corporation"
          disabled={isGenerating}
          required
        />
      </div>

      <div className="grid gap-2">
        <label
          className="text-sm font-medium text-gray-700 dark:text-gray-300"
          htmlFor="cl_hiring_manager"
        >
          Hiring Manager Name (optional)
        </label>
        <input
          id="cl_hiring_manager"
          value={payload.hiring_manager_name || ''}
          onChange={e => onChange('hiring_manager_name', e.target.value || undefined)}
          className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          placeholder="e.g. Jane Smith"
          disabled={isGenerating}
        />
      </div>

      <div className="grid gap-2">
        <label
          className="text-sm font-medium text-gray-700 dark:text-gray-300"
          htmlFor="cl_company_address"
        >
          Company Address (optional)
        </label>
        <textarea
          id="cl_company_address"
          value={payload.company_address || ''}
          onChange={e => onChange('company_address', e.target.value || undefined)}
          className="min-h-[80px] w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          placeholder="Street Address&#10;City, State ZIP"
          disabled={isGenerating}
        />
      </div>

      <div className="grid gap-2">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="cl_tone">
          Tone
        </label>
        <select
          id="cl_tone"
          value={payload.tone}
          onChange={e => onChange('tone', e.target.value as CoverLetterRequest['tone'])}
          className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          disabled={isGenerating}
        >
          <option value="professional">Professional</option>
          <option value="enthusiastic">Enthusiastic</option>
          <option value="conversational">Conversational</option>
        </select>
      </div>

      <div className="grid gap-2">
        <label
          className="text-sm font-medium text-gray-700 dark:text-gray-300"
          htmlFor="cl_llm_instructions"
        >
          LLM Instructions (optional)
        </label>
        <textarea
          id="cl_llm_instructions"
          value={payload.llm_instructions || ''}
          onChange={e => onChange('llm_instructions', e.target.value || undefined)}
          className="min-h-[80px] w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          placeholder="e.g., Write in Spanish, Keep it under 200 words, Use a formal tone"
          disabled={isGenerating}
        />
      </div>

      <div className="grid gap-2">
        <label
          className="text-sm font-medium text-gray-700 dark:text-gray-300"
          htmlFor="cl_job_description"
        >
          Job Description *
        </label>
        <textarea
          id="cl_job_description"
          value={payload.job_description}
          onChange={e => onChange('job_description', e.target.value)}
          className="min-h-[180px] w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
          placeholder="Paste the job description here..."
          disabled={isGenerating}
          required
        />
        <p className="text-xs text-gray-500 dark:text-gray-400">Minimum 20 characters.</p>
      </div>
    </div>
  )
}
