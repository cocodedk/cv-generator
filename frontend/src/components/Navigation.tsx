import { ViewMode } from '../app_helpers/types'

interface NavigationProps {
  viewMode: ViewMode
  isDark: boolean
  onThemeToggle: () => void
}

export default function Navigation({ viewMode, isDark, onThemeToggle }: NavigationProps) {
  return (
    <nav className="bg-white shadow-sm dark:bg-gray-900 dark:border-b dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16">
          {/* min-w-0 lets this row shrink below its buttons' combined natural width (the
              default flex-item min-width is "auto", which otherwise floors it there and
              pushes the whole page wider on phones); overflow-x-auto then scrolls the row
              inside the nav instead. */}
          <div className="flex items-center space-x-4 min-w-0 overflow-x-auto">
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
