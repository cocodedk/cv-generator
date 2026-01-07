import { useState, useRef, useEffect } from 'react'
import { Control, useController } from 'react-hook-form'
import { CVData } from '../../types/cv'

export function usePhotoUpload(control: Control<CVData>) {
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

  return {
    photoPreview,
    fileInputRef,
    handleFileChange,
    handleRemovePhoto,
    photoController,
  }
}
