import { useState } from 'react'
import { useForm } from 'react-hook-form'
import PersonalInfo from './PersonalInfo'
import Experience from './Experience'
import Education from './Education'
import Skills from './Skills'
import { CVData } from '../types/cv'
import { useCvLoader } from '../app_helpers/cvForm/useCvLoader'
import { useProfileManager } from '../app_helpers/cvForm/useProfileManager'
import { useCvSubmit } from '../app_helpers/cvForm/useCvSubmit'
import ProfileLoaderModal from '../app_helpers/cvForm/ProfileLoaderModal'
import { defaultCvData } from '../app_helpers/cvForm/cvFormDefaults'
import AiGenerateModal from './ai/AiGenerateModal'
import CvFormHeader from './CvFormHeader'

interface CVFormProps {
  onSuccess: (message: string) => void
  onError: (message: string | string[]) => void
  setLoading: (loading: boolean) => void
  cvId?: string | null
}

export default function CVForm({ onSuccess, onError, setLoading, cvId }: CVFormProps) {
  const isEditMode = !!cvId
  const [showAiModal, setShowAiModal] = useState(false)
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
  return (
    <>
      {showAiModal && (
        <AiGenerateModal
          onClose={() => setShowAiModal(false)}
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
          onExperienceToggle={handleExperienceToggle}
          onEducationToggle={handleEducationToggle}
          onApply={applySelectedProfile}
          onCancel={closeProfileLoader}
        />
      )}

      {isLoadingCv && (
        <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800 p-6">
          <p className="text-gray-600 dark:text-gray-400">Loading CV data...</p>
        </div>
      )}

      {!isLoadingCv && (
        <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800">
          <CvFormHeader
            title={isEditMode ? 'Edit CV' : 'Create Your CV'}
            onLoadProfile={loadProfile}
            onSaveProfile={handleSubmit(saveToProfile)}
            onGenerateFromJd={() => setShowAiModal(true)}
          />
          <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-8">
            <div className="grid gap-2">
              <label
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
                htmlFor="theme"
              >
                Theme
              </label>
              <select
                id="theme"
                {...register('theme')}
                className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
              >
                <option value="accented">Accented</option>
                <option value="classic">Classic</option>
                <option value="colorful">Colorful</option>
                <option value="creative">Creative</option>
                <option value="elegant">Elegant</option>
                <option value="executive">Executive</option>
                <option value="minimal">Minimal</option>
                <option value="modern">Modern</option>
                <option value="professional">Professional</option>
                <option value="tech">Tech</option>
              </select>
            </div>
            <PersonalInfo
              register={register}
              errors={errors}
              control={control}
              showAiAssist={isEditMode}
            />
            <Experience
              control={control}
              register={register}
              errors={errors}
              showAiAssist={isEditMode}
            />
            <Education control={control} register={register} />
            <Skills control={control} register={register} />

            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => reset()}
                className="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed dark:hover:bg-blue-500"
              >
                {isSubmitting
                  ? isEditMode
                    ? 'Updating...'
                    : 'Generating...'
                  : isEditMode
                    ? 'Update CV'
                    : 'Generate CV'}
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  )
}
