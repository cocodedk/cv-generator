import { Control, UseFormRegister, useFieldArray } from 'react-hook-form'
import { CVData } from '../types/cv'
import ProjectEditor from './ProjectEditor'

interface ExperienceProjectsProps {
  control: Control<CVData>
  register: UseFormRegister<CVData>
  experienceIndex: number
}

export default function ExperienceProjects({
  control,
  register,
  experienceIndex,
}: ExperienceProjectsProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: `experience.${experienceIndex}.projects` as const,
  })

  return (
    <div className="mt-4 space-y-3">
      <div className="flex justify-between items-center">
        <h5 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Projects</h5>
        <button
          type="button"
          onClick={() =>
            append({
              name: '',
              description: '',
              url: '',
              technologies: [],
              highlights: [],
            })
          }
          className="px-3 py-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          + Add Project
        </button>
      </div>

      {fields.length === 0 && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          No projects added. Add projects to move details out of the role description.
        </p>
      )}

      {fields.map((projectField, projectIndex) => (
        <ProjectEditor
          key={projectField.id}
          control={control}
          register={register}
          experienceIndex={experienceIndex}
          projectIndex={projectIndex}
          onRemove={() => remove(projectIndex)}
        />
      ))}
    </div>
  )
}
