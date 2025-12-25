import { Message } from '../app_helpers/useMessage'

interface NotificationModalProps {
  message: Message | null
  onClose: () => void
}

export default function NotificationModal({ message, onClose }: NotificationModalProps) {
  if (!message) {
    return null
  }

  const isError = message.type === 'error'
  const isArray = Array.isArray(message.text)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 dark:bg-black/70"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className={`relative w-full max-w-md rounded-lg shadow-xl ${
          isError
            ? 'bg-red-50 dark:bg-red-900/30 border-2 border-red-200 dark:border-red-800'
            : 'bg-green-50 dark:bg-green-900/30 border-2 border-green-200 dark:border-green-800'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h3
            className={`text-lg font-semibold ${
              isError ? 'text-red-800 dark:text-red-200' : 'text-green-800 dark:text-green-200'
            }`}
          >
            {isError ? 'Error' : 'Success'}
          </h3>
          <button
            onClick={onClose}
            className={`rounded-md p-1 transition-colors ${
              isError
                ? 'text-red-600 hover:bg-red-100 dark:text-red-400 dark:hover:bg-red-800/50'
                : 'text-green-600 hover:bg-green-100 dark:text-green-400 dark:hover:bg-green-800/50'
            }`}
            aria-label="Close"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          {isArray ? (
            <ul className="space-y-2">
              {(message.text as string[]).map((item, index) => (
                <li
                  key={index}
                  className={`text-sm ${
                    isError
                      ? 'text-red-700 dark:text-red-300'
                      : 'text-green-700 dark:text-green-300'
                  }`}
                >
                  • {item}
                </li>
              ))}
            </ul>
          ) : (
            <p
              className={`text-sm ${
                isError ? 'text-red-700 dark:text-red-300' : 'text-green-700 dark:text-green-300'
              }`}
            >
              {message.text as string}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              isError
                ? 'bg-red-600 text-white hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-600'
                : 'bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600'
            }`}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
