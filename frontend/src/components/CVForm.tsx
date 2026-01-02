import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { CVData } from '../types/cv'
import { useCvLoader } from '../app_helpers/cvForm/useCvLoader'
import { useProfileManager } from '../app_helpers/cvForm/useProfileManager'
import { useCvSubmit } from '../app_helpers/cvForm/useCvSubmit'
import { useKeyboardShortcut } from '../app_helpers/cvForm/useKeyboardShortcut'
import { defaultCvData } from '../app_helpers/cvForm/cvFormDefaults'
import CVFormModals from '../app_helpers/cvForm/CVFormModals'
import CVFormContent from '../app_helpers/cvForm/CVFormContent'
import CVFormLoading from '../app_helpers/cvForm/CVFormLoading'
import { downloadPdf } from '../app_helpers/pdfDownload'

interface CVFormProps {
  onSuccess: (message: string) => void
  onError: (message: string | string[]) => void
  setLoading: (loading: boolean) => void
  cvId?: string | null
}

/**
 * Main CV form component that orchestrates form state, hooks, and sub-components.
 * Handles CV creation and editing with support for AI generation and profile loading.
 */
export default function CVForm({ onSuccess, onError, setLoading, cvId }: CVFormProps) {
  const isEditMode = !!cvId
  const [showAiModal, setShowAiModal] = useState(false)
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false)
  const {
    register,
    handleSubmit,
    control,
    reset,
    getValues,
    setError,
    formState: { errors },
  } = useForm<CVData>({
    defaultValues: defaultCvData,
  })
  const { isLoadingCv } = useCvLoader({ cvId, reset, onError, setLoading })

  const {
    showProfileLoader,
    profileData,
    selectedExperiences,
    selectedEducations,
    loadProfile,
    applySelectedProfile,
    saveToProfile,
    closeProfileLoader,
    handleExperienceToggle,
    handleEducationToggle,
  } = useProfileManager({ reset, onSuccess, onError, setLoading })

  const { isSubmitting, onSubmit } = useCvSubmit({
    cvId,
    isEditMode,
    onSuccess,
    onError,
    setLoading,
    setError,
  })

  // Set up keyboard shortcut handler
  useKeyboardShortcut({
    handleSubmit,
    onSubmit,
    isLoadingCv,
    isSubmitting,
    showAiModal,
    showProfileLoader,
  })

  const handleDownloadPdf = async () => {
    if (!cvId || isGeneratingPdf) {
      return
    }

    setIsGeneratingPdf(true)
    try {
      // Optionally get current theme/layout from form values
      const formValues = getValues()
      const theme = formValues.theme
      const layout = formValues.layout

      await downloadPdf(cvId, {
        theme: theme || undefined,
        layout: layout || undefined,
      })
    } catch (error: any) {
      onError(error.message || 'Failed to download PDF')
    } finally {
      setIsGeneratingPdf(false)
    }
  }

  return (
    <>
      <CVFormModals
        showAiModal={showAiModal}
        showProfileLoader={showProfileLoader}
        profileData={profileData}
        selectedExperiences={selectedExperiences}
        selectedEducations={selectedEducations}
        getValues={getValues}
        reset={reset}
        onCloseAiModal={() => setShowAiModal(false)}
        onApplyDraft={draft => {
          const currentTheme = getValues('theme')
          reset({ ...draft, theme: currentTheme || draft.theme })
          onSuccess('Draft applied. Review and save when ready.')
        }}
        onError={onError}
        setLoading={setLoading}
        onExperienceToggle={handleExperienceToggle}
        onEducationToggle={handleEducationToggle}
        onApplyProfile={applySelectedProfile}
        onCancelProfileLoader={closeProfileLoader}
        onSuccess={onSuccess}
      />

      {isLoadingCv ? (
        <CVFormLoading />
      ) : (
        <CVFormContent
          isEditMode={isEditMode}
          isSubmitting={isSubmitting}
          register={register}
          control={control}
          errors={errors}
          handleSubmit={handleSubmit}
          reset={reset}
          onSubmit={onSubmit}
          onLoadProfile={loadProfile}
          onSaveProfile={handleSubmit(saveToProfile)}
          onGenerateFromJd={() => setShowAiModal(true)}
          onDownloadPdf={cvId ? handleDownloadPdf : undefined}
          isGeneratingPdf={isGeneratingPdf}
        />
      )}
    </>
  )
}
