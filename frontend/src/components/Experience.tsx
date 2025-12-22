import { useFieldArray, Control, UseFormRegister } from 'react-hook-form'
import { CVData } from '../types/cv'

interface ExperienceProps {
  control: Control<CVData>
  register: UseFormRegister<CVData>
}

export default function Experience({ control, register }: ExperienceProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'experience'
  })

  const addExperience = () => {
    append({
      title: '',
      company: '',
      start_date: '',
      end_date: '',
      description: '',
      location: ''
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Work Experience</h3>
        <button
          type="button"
          onClick={addExperience}
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          + Add Experience
        </button>
      </div>

      {fields.length === 0 && (
        <p className="text-sm text-gray-500">No experience added. Click "Add Experience" to add one.</p>
      )}

      {fields.map((field, index) => (
        <div key={field.id} className="border border-gray-200 rounded-lg p-4 space-y-4">
          <div className="flex justify-between items-center">
            <h4 className="text-md font-medium text-gray-900">Experience {index + 1}</h4>
            <button
              type="button"
              onClick={() => remove(index)}
              className="text-sm text-red-600 hover:text-red-700"
            >
              Remove
            </button>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Job Title *
              </label>
              <input
                type="text"
                {...register(`experience.${index}.title` as const, { required: 'Title is required' })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Company *
              </label>
              <input
                type="text"
                {...register(`experience.${index}.company` as const, { required: 'Company is required' })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Start Date (YYYY-MM) *
              </label>
              <input
                type="text"
                {...register(`experience.${index}.start_date` as const, { required: 'Start date is required' })}
                placeholder="2020-01"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                End Date (YYYY-MM or "Present")
              </label>
              <input
                type="text"
                {...register(`experience.${index}.end_date` as const)}
                placeholder="2023-12 or Present"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Location
              </label>
              <input
                type="text"
                {...register(`experience.${index}.location` as const)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              rows={3}
              {...register(`experience.${index}.description` as const)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>
      ))}
    </div>
  )
}
