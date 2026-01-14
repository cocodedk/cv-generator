import { useEffect, useState } from 'react'
import { BRANDING } from '../app_helpers/branding'

type FeaturedCVStatus = {
  available: boolean
  last_updated?: string
}

export default function Introduction() {
  const [cvStatus, setCvStatus] = useState<FeaturedCVStatus>({ available: false })

  useEffect(() => {
    // Check if the featured CV exists
    const basePath = import.meta.env.BASE_URL || '/'
    const cvUrl = `${basePath}cv.html`

    fetch(cvUrl, { method: 'HEAD' })
      .then(response => {
        if (response.ok) {
          // Get the last modified date from headers
          const lastModified = response.headers.get('last-modified')
          setCvStatus({
            available: true,
            last_updated: lastModified || undefined,
          })
        } else {
          setCvStatus({ available: false })
        }
      })
      .catch(() => {
        setCvStatus({ available: false })
      })
  }, [])

  const cvUrl = `${import.meta.env.BASE_URL || '/'}cv.html`

  return (
    <div className="space-y-12">
      {/* Hero Section with Featured CV */}
      <div className="text-center space-y-6">
        <h1 className="text-5xl font-bold text-gray-900 dark:text-gray-100">
          Welcome to {BRANDING.appName}
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          Create professional CVs and resumes with ease. Your latest profile is automatically
          transformed into a beautifully designed CV.
        </p>
      </div>

      {/* Featured CV Display */}
      {cvStatus.available ? (
        <div className="max-w-6xl mx-auto">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-800 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
              <h2 className="text-2xl font-bold text-center">My Professional CV</h2>
              {cvStatus.last_updated && (
                <p className="text-center text-blue-100 mt-1 text-sm">
                  Last updated: {new Date(cvStatus.last_updated).toLocaleDateString()}
                </p>
              )}
            </div>

            <div className="p-6">
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
                <iframe
                  src={cvUrl}
                  className="w-full h-96 border-0 rounded"
                  title="Featured CV"
                  loading="lazy"
                />
              </div>

              <div className="flex flex-wrap justify-center gap-4">
                <a
                  href={cvUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                  View Full CV
                </a>

                <button
                  onClick={() => window.open(`${cvUrl}?print=true`, '_blank')}
                  className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
                    />
                  </svg>
                  Print CV
                </button>

                <a
                  href="/api/cv/download-featured"
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Download DOCX
                </a>
              </div>
            </div>
          </div>
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
              No CV Available Yet
            </h3>
            <p className="text-yellow-700 dark:text-yellow-300 mb-6">
              Create your profile to generate your professional CV automatically.
            </p>
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Auto-Generated CV
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Your profile is automatically transformed into a beautifully designed CV using
            professional layouts.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Refresh CV
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
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Multiple Formats
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Export your CV in HTML, DOCX, and print-ready formats for any professional need.
          </p>
          <a
            href="https://github.com/cocodedk/cv-generator/tree/main/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            View Docs
          </a>
        </div>
      </div>
    </div>
  )
}
