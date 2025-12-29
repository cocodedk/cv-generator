import { useEffect, useState } from 'react'
import { BRANDING } from '../app_helpers/branding'

type ShowcaseLayout = {
  layout: string
  theme: string
  file: string
}

type ShowcaseCv = {
  cv_id: string
  name: string
  theme: string
  layouts: ShowcaseLayout[]
}

type ShowcaseIndex = {
  generated_at: string
  cvs: ShowcaseCv[]
}

export default function Introduction() {
  const [showcase, setShowcase] = useState<ShowcaseIndex | null>(null)

  useEffect(() => {
    const basePath = import.meta.env.BASE_URL || '/'
    const url = `${basePath}showcase/index.json`
    fetch(url, { cache: 'no-store' })
      .then(async response => {
        if (!response.ok) {
          return null
        }
        const data = (await response.json()) as ShowcaseIndex
        if (data && Array.isArray(data.cvs)) {
          setShowcase(data)
        }
        return null
      })
      .catch(() => null)
  }, [])

  const showcaseBase = `${import.meta.env.BASE_URL || '/'}showcase/`

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100">
          Welcome to {BRANDING.appName}
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Create professional CVs and resumes with ease. Manage your profiles, generate multiple CV
          formats, and export to various file types.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mt-12">
        <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Create Your CV
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Build your CV step by step with our intuitive form. Add your personal information,
            experience, education, skills, and more.
          </p>
          <button
            onClick={() => {
              window.location.hash = 'form'
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Get Started
          </button>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Manage Your CVs
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            View, edit, and manage all your CVs in one place. Keep track of different versions and
            update them as needed.
          </p>
          <button
            onClick={() => {
              window.location.hash = 'list'
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            View My CVs
          </button>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Profile Management
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Create and manage your profiles to quickly populate CV forms with your information. Save
            time by reusing profile data.
          </p>
          <button
            onClick={() => {
              window.location.hash = 'profile'
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Manage Profiles
          </button>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Export Options
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Export your CVs in multiple formats including DOCX, HTML, and print-ready versions.
            Choose the format that works best for your needs.
          </p>
        </div>
      </div>

      <div className="mt-12 text-center">
        <p className="text-gray-600 dark:text-gray-400">
          Need help? Navigate using the menu above to explore all features.
        </p>
      </div>

      {showcase?.cvs?.length ? (
        <div className="mt-16">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 text-center">
            Public CV Examples
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-center mt-2">
            Explore generated layouts for each published CV.
          </p>
          <div className="grid md:grid-cols-2 gap-6 mt-8">
            {showcase.cvs.map(cv => (
              <div
                key={cv.cv_id}
                className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800"
              >
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {cv.name || 'CV'}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Theme: {cv.theme}</p>
                <div className="flex flex-wrap gap-2 mt-4">
                  {cv.layouts.map(layout => (
                    <a
                      key={`${cv.cv_id}-${layout.layout}`}
                      href={`${showcaseBase}${layout.file}`}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-1 rounded-full border border-blue-200 text-blue-700 dark:border-blue-500/40 dark:text-blue-300 text-sm hover:bg-blue-50 dark:hover:bg-blue-500/10 transition-colors"
                    >
                      {layout.layout}
                    </a>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  )
}
