import { useEffect, useState } from 'react'
import { BRANDING } from '../app_helpers/branding'

type CVTemplate = {
  layout: string
  theme: string
  file: string
  name: string
  description: string
  print_friendly: boolean
  web_optimized: boolean
}

type TemplateIndex = {
  generated_at: string
  profile_name: string
  templates: CVTemplate[]
}

type FilterType = 'all' | 'web' | 'print'

export default function Introduction() {
  const [templateData, setTemplateData] = useState<TemplateIndex | null>(null)
  const [selectedFilter, setSelectedFilter] = useState<FilterType>('all')
  const [previewTemplate, setPreviewTemplate] = useState<CVTemplate | null>(null)

  useEffect(() => {
    // Load template index
    const basePath = import.meta.env.BASE_URL || '/'
    const indexUrl = `${basePath}templates/index.json`

    fetch(indexUrl)
      .then(async response => {
        if (response.ok) {
          const data = (await response.json()) as TemplateIndex
          setTemplateData(data)
        } else {
          setTemplateData(null)
        }
      })
      .catch(() => {
        setTemplateData(null)
      })
  }, [])

  const filteredTemplates =
    templateData?.templates.filter(template => {
      if (selectedFilter === 'web') return template.web_optimized
      if (selectedFilter === 'print') return template.print_friendly
      return true
    }) || []

  const templatesBase = `${import.meta.env.BASE_URL || '/'}templates/`

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <h1 className="text-5xl font-bold text-gray-900 dark:text-gray-100">
          Welcome to {BRANDING.appName}
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          Create professional CVs and resumes with ease. Your latest profile is automatically
          transformed into beautifully designed CV templates.
        </p>
      </div>

      {/* Template Gallery */}
      {templateData?.templates ? (
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                  CV Templates
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  {templateData.profile_name}&apos;s professional CV in{' '}
                  {templateData.templates.length} different styles
                </p>
              </div>

              {/* Filter Controls */}
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedFilter('all')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedFilter === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  All ({templateData.templates.length})
                </button>
                <button
                  onClick={() => setSelectedFilter('web')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedFilter === 'web'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  Web ({templateData.templates.filter(t => t.web_optimized).length})
                </button>
                <button
                  onClick={() => setSelectedFilter('print')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedFilter === 'print'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  Print ({templateData.templates.filter(t => t.print_friendly).length})
                </button>
              </div>
            </div>
          </div>

          {/* Template Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map(template => (
              <div
                key={`${template.layout}-${template.theme}`}
                className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-800 overflow-hidden hover:shadow-xl transition-shadow"
              >
                {/* Template Preview */}
                <div className="h-64 bg-gray-50 dark:bg-gray-800 relative overflow-hidden border-b border-gray-200 dark:border-gray-700">
                  <div className="absolute inset-0 flex items-start justify-center">
                    <iframe
                      src={`${templatesBase}${template.file}`}
                      className="border-0"
                      style={{
                        width: '800px',
                        height: '1131px', // A4 portrait (1:1.414)
                        transform: 'scale(0.28)',
                        transformOrigin: 'top center',
                      }}
                      title={`${template.name} preview`}
                      loading="lazy"
                      scrolling="no"
                    />
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-t from-black/10 via-transparent to-transparent pointer-events-none" />
                </div>

                {/* Template Info */}
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    {template.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {template.description}
                  </p>

                  {/* Badges */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {template.web_optimized && (
                      <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full">
                        Web Optimized
                      </span>
                    )}
                    {template.print_friendly && (
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">
                        Print Friendly
                      </span>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPreviewTemplate(template)}
                      className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors text-sm"
                    >
                      Preview
                    </button>
                    <a
                      href={`${templatesBase}${template.file}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors text-center text-sm"
                    >
                      View Full
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredTemplates.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                No templates match the selected filter.
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="max-w-2xl mx-auto text-center">
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-8">
            <svg
              className="w-16 h-16 text-yellow-600 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            <h3 className="text-xl font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
              No Templates Available
            </h3>
            <p className="text-yellow-700 dark:text-yellow-300 mb-6">
              Create your profile to generate professional CV templates automatically.
            </p>
            <button
              onClick={() => {
                window.location.hash = 'profile'
              }}
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Create Profile
            </button>
          </div>
        </div>
      )}

      {/* Template Preview Modal */}
      {previewTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-800">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                {previewTemplate.name}
              </h3>
              <button
                onClick={() => setPreviewTemplate(null)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
            <div className="p-6">
              <iframe
                src={`${templatesBase}${previewTemplate.file}`}
                className="w-full h-96 border-0 rounded"
                title={`${previewTemplate.name} full preview`}
              />
              <div className="flex justify-end gap-3 mt-6">
                <a
                  href={`${templatesBase}${previewTemplate.file}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                >
                  Open in New Tab
                </a>
                <button
                  onClick={() => setPreviewTemplate(null)}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Cards */}
      <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto">
            <svg
              className="w-8 h-8 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Create Your Profile
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Build your professional profile with personal information, experience, education, and
            skills.
          </p>
          <button
            onClick={() => {
              window.location.hash = 'profile'
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Create Profile
          </button>
        </div>

        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Template Gallery
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Choose from professional templates optimized for web viewing or print production.
          </p>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Browse Templates
          </button>
        </div>

        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto">
            <svg
              className="w-8 h-8 text-purple-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Export Options</h3>
          <p className="text-gray-600 dark:text-gray-400">
            Download individual templates or use our API to generate custom versions.
          </p>
          <a
            href="https://github.com/cocodedk/cv-generator/tree/main/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            View API Docs
          </a>
        </div>
      </div>
    </div>
  )
}
