import { UseFormRegister, FieldErrors } from 'react-hook-form'
import { CVData } from '../../types/cv'

interface BasicFieldsProps {
  register: UseFormRegister<CVData>
  errors: FieldErrors<CVData>
}

export default function BasicFields({ register, errors }: BasicFieldsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label
          htmlFor="name"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Full Name *
        </label>
        <input
          type="text"
          id="name"
          {...register('personal_info.name', { required: 'Name is required' })}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
        {errors.personal_info?.name && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {errors.personal_info.name.message}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Professional Title
        </label>
        <input
          type="text"
          id="title"
          {...register('personal_info.title')}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
      </div>

      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Email
        </label>
        <input
          type="email"
          id="email"
          {...register('personal_info.email')}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
      </div>

      <div>
        <label
          htmlFor="phone"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Phone
        </label>
        <input
          type="tel"
          id="phone"
          {...register('personal_info.phone')}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
      </div>

      <div>
        <label
          htmlFor="linkedin"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          LinkedIn
        </label>
        <input
          type="url"
          id="linkedin"
          {...register('personal_info.linkedin')}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
      </div>

      <div>
        <label
          htmlFor="github"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          GitHub
        </label>
        <input
          type="url"
          id="github"
          {...register('personal_info.github')}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
      </div>

      <div>
        <label
          htmlFor="website"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Website
        </label>
        <input
          type="url"
          id="website"
          {...register('personal_info.website')}
          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        />
      </div>
    </div>
  )
}
