import { useFieldArray, Control, UseFormRegister } from 'react-hook-form'
import { CVData } from '../types/cv'
import ExperienceItem from './ExperienceItem'

interface ExperienceProps {
  control: Control<CVData>
  register: UseFormRegister<CVData>
}

export default function Experience({ control, register }: ExperienceProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'experience',
  })

  const addExperience = () => {
    append({
      title: '',
      company: '',
      start_date: '',
      end_date: '',
      description: '',
      location: '',
      projects: [],
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Work Experience</h3>
        <button
          type="button"
          onClick={addExperience}
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          + Add Experience
        </button>
      </div>

      {fields.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No experience added. Click "Add Experience" to add one.
        </p>
      )}

      {fields.map((field, index) => (
        <ExperienceItem
          key={field.id}
          control={control}
          register={register}
          index={index}
          onRemove={() => remove(index)}
        />
      ))}
    </div>
  )
}
