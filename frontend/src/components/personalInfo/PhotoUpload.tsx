import { useState, useRef, useEffect } from 'react'
import { Control, useController } from 'react-hook-form'
import { CVData } from '../../types/cv'

interface PhotoUploadProps {
  control: Control<CVData>
}

export default function PhotoUpload({ control }: PhotoUploadProps) {
  const photoController = useController({ control, name: 'personal_info.photo' })
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [photoPreview, setPhotoPreview] = useState<string | null>(
    photoController.field.value || null
  )

  // Sync photo preview when form value changes (e.g., when loading existing CV)
  useEffect(() => {
    setPhotoPreview(photoController.field.value || null)
  }, [photoController.field.value])

  // Clear file input when photo value changes to prevent stale file selections
  useEffect(() => {
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
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
    <div>
      <label htmlFor="photo" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
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
  )
}
