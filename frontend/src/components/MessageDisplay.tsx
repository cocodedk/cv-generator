import { Message } from '../app_helpers/useMessage'

interface MessageDisplayProps {
  message: Message | null
}

export default function MessageDisplay({ message }: MessageDisplayProps) {
  if (!message) {
    return null
  }

  return (
    <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4`}>
      <div
        className={`rounded-md p-4 ${
          message.type === 'success'
            ? 'bg-green-50 text-green-800 border border-green-200 dark:bg-green-900/30 dark:text-green-200 dark:border-green-800'
            : 'bg-red-50 text-red-800 border border-red-200 dark:bg-red-900/30 dark:text-red-200 dark:border-red-800'
        }`}
      >
        {message.text}
      </div>
    </div>
  )
}
