import { useEffect, useRef, useState } from 'react'
import { EditorContent, useEditor } from '@tiptap/react'
import RichTextToolbar from './richText/RichTextToolbar'
import { stripHtml } from '../app_helpers/richTextarea/htmlUtils'
import { useEditorExtensions, getEditorProps } from '../app_helpers/richTextarea/editorConfig'
import { useEditorSync } from '../app_helpers/richTextarea/useEditorSync'
import { useAiAssist } from '../app_helpers/richTextarea/useAiAssist'
import { AiRewriteModal } from '../app_helpers/richTextarea/AiRewriteModal'

interface RichTextareaProps {
  id: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  rows?: number
  error?: { message?: string }
  maxLength?: number
  className?: string
  showAiAssist?: boolean
}

export { stripHtml }

export default function RichTextarea({
  id,
  value,
  onChange,
  placeholder,
  rows = 4,
  error,
  maxLength,
  className = '',
  showAiAssist = false,
}: RichTextareaProps) {
  const minHeight = rows * 24
  const lastKnownHtmlRef = useRef<string>(value || '')
  const lastEmittedValueRef = useRef<string>(value || '')
  const isEditingRef = useRef<boolean>(false)
  const editingTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const [textLength, setTextLength] = useState(() => stripHtml(value || '').length)

  const extensions = useEditorExtensions(placeholder)

  const editor = useEditor({
    extensions,
    content: value || '',
    editorProps: getEditorProps({ id, placeholder, error, minHeight }),
    onUpdate: ({ editor: currentEditor }) => {
      const html = currentEditor.getHTML()

      lastKnownHtmlRef.current = html
      lastEmittedValueRef.current = html
      setTextLength(currentEditor.getText().length)

      // Mark as actively editing and clear flag after delay
      isEditingRef.current = true
      if (editingTimeoutRef.current) {
        clearTimeout(editingTimeoutRef.current)
      }
      editingTimeoutRef.current = setTimeout(() => {
        isEditingRef.current = false
        editingTimeoutRef.current = null
      }, 150)

      onChange(html)
    },
  })

  useEditorSync({
    editor,
    value,
    onChange,
    isEditingRef,
    lastKnownHtmlRef,
    lastEmittedValueRef,
    setTextLength,
  })

  const {
    showPromptModal,
    setShowPromptModal,
    isRewriting,
    rewriteError,
    applyAiAssist,
    handleLlmRewrite,
  } = useAiAssist({
    editor,
    onChange,
    maxLength,
    lastKnownHtmlRef,
    lastEmittedValueRef,
    setTextLength,
  })

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (editingTimeoutRef.current) {
        clearTimeout(editingTimeoutRef.current)
      }
    }
  }, [])

  return (
    <div className={className}>
      {showAiAssist ? (
        <div className="mb-2 flex justify-end gap-2">
          <button
            type="button"
            onClick={() => applyAiAssist('rewrite')}
            className="rounded-md border border-gray-300 bg-white px-2.5 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            AI rewrite
          </button>
          <button
            type="button"
            onClick={() => applyAiAssist('bullets')}
            className="rounded-md border border-gray-300 bg-white px-2.5 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            AI bullets
          </button>
        </div>
      ) : null}

      <AiRewriteModal
        isOpen={showPromptModal}
        onClose={() => setShowPromptModal(false)}
        onRewrite={handleLlmRewrite}
        isRewriting={isRewriting}
        rewriteError={rewriteError}
      />

      {editor ? <RichTextToolbar editor={editor} /> : null}
      <EditorContent editor={editor} />

      {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error.message}</p>}
      {maxLength && (
        <p
          className={`mt-1 text-xs ${textLength > maxLength ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'}`}
        >
          {textLength} / {maxLength} characters
        </p>
      )}
    </div>
  )
}
