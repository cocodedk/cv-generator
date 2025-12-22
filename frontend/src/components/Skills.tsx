import { useFieldArray, Control, UseFormRegister } from 'react-hook-form'
import { CVData } from '../types/cv'

interface SkillsProps {
  control: Control<CVData>
  register: UseFormRegister<CVData>
}

export default function Skills({ control, register }: SkillsProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'skills'
  })

  const addSkill = () => {
    append({
      name: '',
      category: '',
      level: ''
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Skills</h3>
        <button
          type="button"
          onClick={addSkill}
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          + Add Skill
        </button>
      </div>

      {fields.length === 0 && (
        <p className="text-sm text-gray-500">No skills added. Click "Add Skill" to add one.</p>
      )}

      {fields.map((field, index) => (
        <div key={field.id} className="border border-gray-200 rounded-lg p-4">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-md font-medium text-gray-900">Skill {index + 1}</h4>
            <button
              type="button"
              onClick={() => remove(index)}
              className="text-sm text-red-600 hover:text-red-700"
            >
              Remove
            </button>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Skill Name *
              </label>
              <input
                type="text"
                {...register(`skills.${index}.name` as const, { required: 'Skill name is required' })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Category
              </label>
              <input
                type="text"
                {...register(`skills.${index}.category` as const)}
                placeholder="e.g., Programming Languages"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Level
              </label>
              <input
                type="text"
                {...register(`skills.${index}.level` as const)}
                placeholder="e.g., Expert, Advanced"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
