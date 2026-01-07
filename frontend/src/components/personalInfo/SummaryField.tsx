import { Control, useController } from 'react-hook-form'
import { CVData } from '../../types/cv'
import RichTextarea from '../RichTextarea'

interface SummaryFieldProps {
  control: Control<CVData>
  showAiAssist?: boolean
}

export default function SummaryField({ control, showAiAssist }: SummaryFieldProps) {
  const summaryController = useController({ control, name: 'personal_info.summary' })

  return (
    <div>
      <label
        id="summary-label"
        htmlFor="summary"
        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        Professional Summary
      </label>
      <RichTextarea
        id="summary"
        value={summaryController.field.value || ''}
        onChange={summaryController.field.onChange}
        rows={4}
        placeholder="Brief summary of your professional background..."
        className="mt-1"
        showAiAssist={showAiAssist}
      />
    </div>
  )
}
