import { ViewMode } from '../app_helpers/types'
import { BRANDING } from '../app_helpers/branding'

interface NavigationProps {
  viewMode: ViewMode
  isDark: boolean
  onThemeToggle: () => void
}

export default function Navigation({ viewMode, isDark, onThemeToggle }: NavigationProps) {
  return (
    <nav className="bg-white shadow-sm dark:bg-gray-900 dark:border-b dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <div className="flex items-baseline gap-2">
                <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  {BRANDING.appName}
                </h1>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {BRANDING.ownerName} · {BRANDING.companyName}
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => {
                window.location.hash = 'introduction'
              }}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                viewMode === 'introduction'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
              }`}
            >
              Introduction
            </button>
            <button
              type="button"
              onClick={onThemeToggle}
              aria-pressed={isDark}
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800"
            >
              {isDark ? 'Light mode' : 'Dark mode'}
            </button>
            <button
              onClick={() => {
                window.location.hash = 'form'
              }}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                viewMode === 'form' || viewMode === 'edit'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
              }`}
            >
              {viewMode === 'edit' ? 'Edit CV' : 'Create CV'}
            </button>
            <button
              onClick={() => {
                window.location.hash = 'list'
              }}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                viewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
              }`}
            >
              My CVs
            </button>
            <button
              onClick={() => {
                window.location.hash = 'profile-list'
              }}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                viewMode === 'profile-list'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
              }`}
            >
              My Profiles
            </button>
            <button
              onClick={() => {
                window.location.hash = 'profile'
              }}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                viewMode === 'profile' || viewMode === 'profile-edit'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
              }`}
            >
              Profile
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
