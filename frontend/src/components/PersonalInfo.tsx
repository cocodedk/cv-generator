import { UseFormRegister, FieldErrors, useController, Control } from 'react-hook-form'
import { useState, useRef, useEffect } from 'react'
import { CVData } from '../types/cv'
import RichTextarea from './RichTextarea'

interface PersonalInfoProps {
  register: UseFormRegister<CVData>
  errors: FieldErrors<CVData>
  control: Control<CVData>
  showAiAssist?: boolean
}

export default function PersonalInfo({
  register,
  errors,
  control,
  showAiAssist,
}: PersonalInfoProps) {
  const summaryController = useController({ control, name: 'personal_info.summary' })
  const photoController = useController({ control, name: 'personal_info.photo' })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [photoPreview, setPhotoPreview] = useState<string | null>(
    photoController.field.value || null
  )

  // Sync photo preview when form value changes (e.g., when loading existing CV)
  useEffect(() => {
    setPhotoPreview(photoController.field.value || null)
  }, [photoController.field.value])

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file')
      return
    }

    // Validate file size (max 2MB)
    const maxSize = 2 * 1024 * 1024 // 2MB
    if (file.size > maxSize) {
      alert('Image size must be less than 2MB')
      return
    }

    // Convert to base64
    const reader = new FileReader()
    reader.onloadend = () => {
      const base64String = reader.result as string
      photoController.field.onChange(base64String)
      setPhotoPreview(base64String)
    }
    reader.onerror = () => {
      alert('Error reading file')
    }
    reader.readAsDataURL(file)
  }

  const handleRemovePhoto = () => {
    photoController.field.onChange(null)
    setPhotoPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Personal Information
      </h3>

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

      <div>
        <label
          htmlFor="photo"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Photo
        </label>
        <div className="mt-1 flex items-center gap-4">
          <div className="flex-shrink-0">
            {photoPreview ? (
              <img
                src={photoPreview}
                alt="Preview"
                className="h-24 w-24 rounded-md object-cover border border-gray-300 dark:border-gray-700"
              />
            ) : (
              <div className="h-24 w-24 rounded-md border border-gray-300 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <span className="text-xs text-gray-500 dark:text-gray-400">No photo</span>
              </div>
            )}
          </div>
          <div className="flex-1">
            <input
              type="file"
              id="photo"
              ref={fileInputRef}
              accept="image/*"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-900 dark:text-gray-100 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900 dark:file:text-blue-300 dark:hover:file:bg-blue-800 cursor-pointer"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              JPEG, PNG or WebP. Max size 2MB.
            </p>
            {photoPreview && (
              <button
                type="button"
                onClick={handleRemovePhoto}
                className="mt-2 text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              >
                Remove photo
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="text-md font-medium text-gray-800 dark:text-gray-200">Address</h4>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label
              htmlFor="address.street"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Street Address
            </label>
            <input
              type="text"
              id="address.street"
              {...register('personal_info.address.street')}
              className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:placeholder:text-gray-500 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              placeholder="House number and street name"
            />
          </div>

          <div>
            <label
              htmlFor="address.city"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              City
            </label>
            <input
              type="text"
              id="address.city"
              {...register('personal_info.address.city')}
              className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            />
          </div>

          <div>
            <label
              htmlFor="address.state"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              State / Province
            </label>
            <input
              type="text"
              id="address.state"
              {...register('personal_info.address.state')}
              className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            />
          </div>

          <div>
            <label
              htmlFor="address.zip"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              ZIP / Postal Code
            </label>
            <input
              type="text"
              id="address.zip"
              {...register('personal_info.address.zip')}
              className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            />
          </div>

          <div>
            <label
              htmlFor="address.country"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Country
            </label>
            <input
              type="text"
              id="address.country"
              {...register('personal_info.address.country')}
              className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            />
          </div>
        </div>
      </div>

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
    </div>
  )
}
