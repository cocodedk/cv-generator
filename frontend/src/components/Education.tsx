import { useFieldArray, Control, UseFormRegister } from 'react-hook-form'
import { CVData } from '../types/cv'

interface EducationProps {
  control: Control<CVData>
  register: UseFormRegister<CVData>
}

export default function Education({ control, register }: EducationProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'education',
  })

  const addEducation = () => {
    append({
      degree: '',
      institution: '',
      year: '',
      field: '',
      gpa: '',
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Education</h3>
        <button
          type="button"
          onClick={addEducation}
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          + Add Education
        </button>
      </div>

      {fields.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No education added. Click "Add Education" to add one.
        </p>
      )}

      {fields.map((field, index) => (
        <div
          key={field.id}
          className="border border-gray-200 rounded-lg p-4 space-y-4 dark:border-gray-800 dark:bg-gray-900/40"
        >
          <div className="flex justify-between items-center">
            <h4 className="text-md font-medium text-gray-900 dark:text-gray-100">
              Education {index + 1}
            </h4>
            <button
              type="button"
              onClick={() => remove(index)}
              className="text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
            >
              Remove
            </button>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label
                htmlFor={`education-degree-${index}`}
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Degree *
              </label>
              <input
                id={`education-degree-${index}`}
                type="text"
                {...register(`education.${index}.degree` as const, {
                  required: 'Degree is required',
                })}
                className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>

            <div>
              <label
                htmlFor={`education-institution-${index}`}
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Institution *
              </label>
              <input
                id={`education-institution-${index}`}
                type="text"
                {...register(`education.${index}.institution` as const, {
                  required: 'Institution is required',
                })}
                className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>

            <div>
              <label
                htmlFor={`education-year-${index}`}
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Year
              </label>
              <input
                id={`education-year-${index}`}
                type="text"
                {...register(`education.${index}.year` as const)}
                className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>

            <div>
              <label
                htmlFor={`education-field-${index}`}
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Field of Study
              </label>
              <input
                id={`education-field-${index}`}
                type="text"
                {...register(`education.${index}.field` as const)}
                className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>

            <div>
              <label
                htmlFor={`education-gpa-${index}`}
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                GPA
              </label>
              <input
                id={`education-gpa-${index}`}
                type="text"
                {...register(`education.${index}.gpa` as const)}
                placeholder="3.8/4.0"
                className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder:text-gray-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
