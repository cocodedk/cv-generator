import { useState } from 'react'

interface AiRewriteModalProps {
  isOpen: boolean
  onClose: () => void
  onRewrite: (prompt: string) => Promise<void>
  isRewriting: boolean
  rewriteError: string | null
}

export function AiRewriteModal({
  isOpen,
  onClose,
  onRewrite,
  isRewriting,
  rewriteError,
}: AiRewriteModalProps) {
  const [prompt, setPrompt] = useState('')

  if (!isOpen) return null

  const handleSubmit = async () => {
    if (!prompt.trim()) return
    await onRewrite(prompt.trim())
    setPrompt('')
  }

  const handleClose = () => {
    setPrompt('')
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">AI Rewrite</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Enter your prompt/instruction for rewriting the text:
        </p>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="e.g., Make it more professional, Make it shorter, Improve clarity..."
          aria-label="Prompt for AI rewrite"
          className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 mb-4"
          rows={3}
        />
        {rewriteError && (
          <p className="text-sm text-red-600 dark:text-red-400 mb-4">{rewriteError}</p>
        )}
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={handleClose}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
            disabled={isRewriting}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isRewriting || !prompt.trim()}
            className="rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed dark:hover:bg-blue-500"
          >
            {isRewriting ? 'Rewriting...' : 'Rewrite'}
          </button>
        </div>
      </div>
    </div>
  )
}
