import { Control, UseFormRegister, useController } from 'react-hook-form'
import { CVData } from '../types/cv'
import RichTextarea from './RichTextarea'

interface ProjectEditorProps {
  control: Control<CVData>
  register: UseFormRegister<CVData>
  experienceIndex: number
  projectIndex: number
  onRemove: () => void
  showAiAssist?: boolean
}

function listToText(value: unknown, separator: string) {
  return Array.isArray(value) ? value.filter(Boolean).join(separator) : ''
}

function technologiesFromText(value: string): string[] {
  return value
    .split(',')
    .map(v => v.trim())
    .filter(Boolean)
}

function highlightsFromText(value: string): string[] {
  return value
    .split('\n')
    .map(v => v.trim().replace(/^[-*•]\s*/, ''))
    .filter(Boolean)
}

export default function ProjectEditor({
  control,
  register,
  experienceIndex,
  projectIndex,
  onRemove,
  showAiAssist,
}: ProjectEditorProps) {
  const base = `experience.${experienceIndex}.projects.${projectIndex}` as const
  const nameField = useController({
    control,
    name: `${base}.name` as const,
    rules: { required: 'Project name is required' },
  })
  const technologies = useController({ control, name: `${base}.technologies` as const })
  const highlights = useController({ control, name: `${base}.highlights` as const })

  return (
    <div className="border border-gray-200 rounded-md p-3 space-y-3 dark:border-gray-800 dark:bg-gray-900/30">
      <div className="flex justify-between items-center">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
          Project {projectIndex + 1}
        </p>
        <button
          type="button"
          onClick={onRemove}
          className="text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
        >
          Remove
        </button>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label
            htmlFor={`project-name-${experienceIndex}-${projectIndex}`}
            className="block text-xs font-medium text-gray-700 dark:text-gray-300"
          >
            Project Name *
          </label>
          <input
            id={`project-name-${experienceIndex}-${projectIndex}`}
            type="text"
            {...nameField.field}
            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
          />
          {nameField.fieldState.error?.message && (
            <p className="mt-1 text-xs text-red-600">{nameField.fieldState.error.message}</p>
          )}
        </div>

        <div>
          <label
            htmlFor={`project-url-${experienceIndex}-${projectIndex}`}
            className="block text-xs font-medium text-gray-700 dark:text-gray-300"
          >
            URL
          </label>
          <input
            id={`project-url-${experienceIndex}-${projectIndex}`}
            type="text"
            {...register(`${base}.url` as const)}
            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
          />
        </div>
      </div>

      <div>
        <label
          htmlFor={`project-description-${experienceIndex}-${projectIndex}`}
          className="block text-xs font-medium text-gray-700 dark:text-gray-300"
        >
          Description
        </label>
        <input
          id={`project-description-${experienceIndex}-${projectIndex}`}
          type="text"
          {...register(`${base}.description` as const)}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
      </div>

      <div>
        <label
          htmlFor={`project-tech-${experienceIndex}-${projectIndex}`}
          className="block text-xs font-medium text-gray-700 dark:text-gray-300"
        >
          Technologies (comma-separated)
        </label>
        <input
          id={`project-tech-${experienceIndex}-${projectIndex}`}
          type="text"
          value={listToText(technologies.field.value, ', ')}
          onChange={e => technologies.field.onChange(technologiesFromText(e.target.value))}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
      </div>

      <div>
        <label
          id={`project-highlights-${experienceIndex}-${projectIndex}-label`}
          htmlFor={`project-highlights-${experienceIndex}-${projectIndex}`}
          className="block text-xs font-medium text-gray-700 dark:text-gray-300"
        >
          Highlights
        </label>
        <RichTextarea
          id={`project-highlights-${experienceIndex}-${projectIndex}`}
          value={listToText(highlights.field.value, '\n')}
          onChange={value => {
            // Convert rich text back to plain text lines for highlights array
            const plainText = value
              .replace(/<br\s*\/?>/g, '\n')
              .replace(/<\/li>/g, '\n')
              .replace(/<\/p>/g, '\n')
              .replace(/<[^>]*>/g, '')
              .replace(/&nbsp;/g, ' ')
              .trim()
            highlights.field.onChange(highlightsFromText(plainText))
          }}
          rows={3}
          placeholder="Enter highlights (one per line)..."
          className="mt-1"
          showAiAssist={showAiAssist}
        />
      </div>
    </div>
  )
}
