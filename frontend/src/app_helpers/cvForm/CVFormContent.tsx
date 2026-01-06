import { CVData } from '../../types/cv'
import {
  UseFormRegister,
  Control,
  UseFormHandleSubmit,
  UseFormReset,
  FieldErrors,
} from 'react-hook-form'
import PersonalInfo from '../../components/PersonalInfo'
import Experience from '../../components/Experience'
import Education from '../../components/Education'
import Skills from '../../components/Skills'
import CvFormHeader from '../../components/CvFormHeader'

interface CVFormContentProps {
  isEditMode: boolean
  isSubmitting: boolean
  register: UseFormRegister<CVData>
  control: Control<CVData>
  errors: FieldErrors<CVData>
  handleSubmit: UseFormHandleSubmit<CVData>
  reset: UseFormReset<CVData>
  onSubmit: (data: CVData) => void | Promise<void>
  onLoadProfile: () => void
  onSaveProfile: () => void
  onGenerateFromJd: () => void
  onGenerateCoverLetter?: () => void
  onDownloadPdf?: () => void
  isGeneratingPdf?: boolean
}

/**
 * Component that renders the main CV form content.
 * Includes header, theme selector, and all form sections.
 */
export default function CVFormContent({
  isEditMode,
  isSubmitting,
  register,
  control,
  errors,
  handleSubmit,
  reset,
  onSubmit,
  onLoadProfile,
  onSaveProfile,
  onGenerateFromJd,
  onGenerateCoverLetter,
  onDownloadPdf,
  isGeneratingPdf = false,
}: CVFormContentProps) {
  return (
    <div className="bg-white shadow rounded-lg dark:bg-gray-900 dark:border dark:border-gray-800">
      <CvFormHeader
        title={isEditMode ? 'Edit CV' : 'Create Your CV'}
        onLoadProfile={onLoadProfile}
        onSaveProfile={onSaveProfile}
        onGenerateFromJd={onGenerateFromJd}
        onGenerateCoverLetter={onGenerateCoverLetter}
        onDownloadPdf={onDownloadPdf}
        isGeneratingPdf={isGeneratingPdf}
      />
      <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="theme">
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
          <div className="grid gap-2">
            <label
              className="text-sm font-medium text-gray-700 dark:text-gray-300"
              htmlFor="layout"
            >
              Layout
            </label>
            <select
              id="layout"
              {...register('layout')}
              className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            >
              <optgroup label="Print-First">
                <option value="classic-two-column">Classic Two-Column</option>
                <option value="ats-single-column">ATS Single Column</option>
                <option value="modern-sidebar">Modern Sidebar</option>
              </optgroup>
              <optgroup label="Web-First">
                <option value="section-cards-grid">Section Cards Grid</option>
                <option value="project-case-studies">Project Case Studies</option>
                <option value="portfolio-spa">Portfolio SPA</option>
                <option value="dark-mode-tech">Dark Mode Tech</option>
              </optgroup>
              <optgroup label="Special">
                <option value="career-timeline">Career Timeline</option>
                <option value="interactive-skills-matrix">Interactive Skills Matrix</option>
                <option value="academic-cv">Academic CV</option>
              </optgroup>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor="target_role">
              Job Title
            </label>
            <input
              id="target_role"
              {...register('target_role')}
              type="text"
              placeholder="e.g. Senior Software Engineer"
              className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            />
          </div>
          <div className="grid gap-2">
            <label
              className="text-sm font-medium text-gray-700 dark:text-gray-300"
              htmlFor="target_company"
            >
              Target Company
            </label>
            <input
              id="target_company"
              {...register('target_company')}
              type="text"
              placeholder="e.g. Google"
              className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
            />
          </div>
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
  )
}
