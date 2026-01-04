import { CVData, ProfileData } from '../../types/cv'
import { UseFormGetValues, UseFormReset } from 'react-hook-form'
import AiGenerateModal from '../../components/ai/AiGenerateModal'
import ProfileLoaderModal from './ProfileLoaderModal'

interface CVFormModalsProps {
  showAiModal: boolean
  showProfileLoader: boolean
  profileData: ProfileData | null
  selectedExperiences: Set<number>
  selectedEducations: Set<number>
  getValues: UseFormGetValues<CVData>
  reset: UseFormReset<CVData>
  onCloseAiModal: () => void
  onError: (message: string | string[]) => void
  setLoading: (loading: boolean) => void
  onExperienceToggle: (index: number, checked: boolean) => void
  onEducationToggle: (index: number, checked: boolean) => void
  onApplyProfile: () => void
  onCancelProfileLoader: () => void
  onSuccess: (message: string) => void
}

/**
 * Component that renders all modals for the CV form.
 * Handles AI generation modal and profile loader modal.
 */
export default function CVFormModals({
  showAiModal,
  showProfileLoader,
  profileData,
  selectedExperiences,
  selectedEducations,
  getValues,
  reset,
  onCloseAiModal,
  onError,
  setLoading,
  onExperienceToggle,
  onEducationToggle,
  onApplyProfile,
  onCancelProfileLoader,
  onSuccess,
}: CVFormModalsProps) {
  return (
    <>
      {showAiModal && (
        <AiGenerateModal
          onClose={onCloseAiModal}
          onApply={draft => {
            const currentTheme = getValues('theme')
            reset({ ...draft, theme: currentTheme || draft.theme })
            onSuccess('Draft applied. Review and save when ready.')
          }}
          onError={onError}
          setLoading={setLoading}
        />
      )}
      {showProfileLoader && profileData && (
        <ProfileLoaderModal
          profileData={profileData}
          selectedExperiences={selectedExperiences}
          selectedEducations={selectedEducations}
          onExperienceToggle={onExperienceToggle}
          onEducationToggle={onEducationToggle}
          onApply={onApplyProfile}
          onCancel={onCancelProfileLoader}
        />
      )}
    </>
  )
}
