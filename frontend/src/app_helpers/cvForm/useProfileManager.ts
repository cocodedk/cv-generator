import { useState } from 'react'
import { UseFormReset } from 'react-hook-form'
import axios from 'axios'
import { CVData, ProfileData } from '../../types/cv'

interface UseProfileManagerProps {
  reset: UseFormReset<CVData>
  onSuccess: (message: string) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
}

export function useProfileManager({
  reset,
  onSuccess,
  onError,
  setLoading,
}: UseProfileManagerProps) {
  const [showProfileSelection, setShowProfileSelection] = useState(false)
  const [showProfileLoader, setShowProfileLoader] = useState(false)
  const [profileData, setProfileData] = useState<ProfileData | null>(null)
  const [selectedExperiences, setSelectedExperiences] = useState<Set<number>>(new Set())
  const [selectedEducations, setSelectedEducations] = useState<Set<number>>(new Set())

  const loadProfile = () => {
    setShowProfileSelection(true)
  }

  const handleProfileSelected = (profile: ProfileData) => {
    setProfileData(profile)
    setShowProfileSelection(false)
    setShowProfileLoader(true)
    // Pre-select all experiences and education by default
    const expIndices = new Set<number>(profile.experience.map((_, i) => i))
    const eduIndices = new Set<number>(profile.education.map((_, i) => i))
    setSelectedExperiences(expIndices)
    setSelectedEducations(eduIndices)
  }

  const applySelectedProfile = () => {
    if (!profileData) return

    const selectedExp = profileData.experience.filter((_, i) => selectedExperiences.has(i))
    const selectedEdu = profileData.education.filter((_, i) => selectedEducations.has(i))

    reset({
      personal_info: profileData.personal_info,
      experience: selectedExp,
      education: selectedEdu,
      skills: profileData.skills,
      theme: 'classic',
    })

    setShowProfileLoader(false)
    setProfileData(null)
    setSelectedExperiences(new Set())
    setSelectedEducations(new Set())
    onSuccess('Profile data loaded successfully!')
  }

  const saveToProfile = async (data: CVData) => {
    setLoading(true)
    try {
      const profileData: ProfileData = {
        personal_info: data.personal_info,
        experience: data.experience,
        education: data.education,
        skills: data.skills,
      }
      await axios.post('/api/profile', profileData)
      onSuccess('Current form data saved to profile!')
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to save to profile')
    } finally {
      setLoading(false)
    }
  }

  const closeProfileSelection = () => {
    setShowProfileSelection(false)
  }

  const closeProfileLoader = () => {
    setShowProfileLoader(false)
    setProfileData(null)
    setSelectedExperiences(new Set())
    setSelectedEducations(new Set())
  }

  const handleExperienceToggle = (index: number, checked: boolean) => {
    const newSet = new Set(selectedExperiences)
    if (checked) {
      newSet.add(index)
    } else {
      newSet.delete(index)
    }
    setSelectedExperiences(newSet)
  }

  const handleEducationToggle = (index: number, checked: boolean) => {
    const newSet = new Set(selectedEducations)
    if (checked) {
      newSet.add(index)
    } else {
      newSet.delete(index)
    }
    setSelectedEducations(newSet)
  }

  return {
    showProfileSelection,
    showProfileLoader,
    profileData,
    selectedExperiences,
    selectedEducations,
    loadProfile,
    handleProfileSelected,
    applySelectedProfile,
    saveToProfile,
    closeProfileSelection,
    closeProfileLoader,
    handleExperienceToggle,
    handleEducationToggle,
  }
}
