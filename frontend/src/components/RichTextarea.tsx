import { useEffect, useMemo, useRef, useState } from 'react'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import { buildAiRewriteHtml } from '../app_helpers/ai/aiTextAssist'
import { rewriteText } from '../services/aiService'
import RichTextToolbar from './richText/RichTextToolbar'

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

export function stripHtml(html: string): string {
  const tmp = document.createElement('DIV')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

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
  const [textLength, setTextLength] = useState(() => stripHtml(value || '').length)
  const [showPromptModal, setShowPromptModal] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [isRewriting, setIsRewriting] = useState(false)
  const [rewriteError, setRewriteError] = useState<string | null>(null)

  const extensions = useMemo(
    () => [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      Underline,
      Link.configure({ openOnClick: false, autolink: false }),
      Placeholder.configure({ placeholder: placeholder || '' }),
    ],
    [placeholder]
  )

  const editor = useEditor({
    extensions,
    content: value || '',
    editorProps: {
      attributes: {
        id,
        class:
          'ql-editor w-full rounded-b-md border bg-gray-50 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 dark:bg-gray-800 ' +
          (error
            ? 'border-red-500 focus:ring-red-500 dark:border-red-500 dark:focus:ring-red-500'
            : 'border-gray-300 text-gray-900 focus:ring-blue-500 dark:border-gray-700 dark:text-gray-100 dark:focus:ring-blue-400'),
        style: `min-height:${minHeight}px;`,
        'aria-labelledby': `${id}-label`,
        role: 'textbox',
        'aria-multiline': 'true',
      },
    },
    onUpdate: ({ editor: currentEditor }) => {
      const html = currentEditor.getHTML()
      lastKnownHtmlRef.current = html
      lastEmittedValueRef.current = html
      setTextLength(currentEditor.getText().length)
      onChange(html)
    },
  })

  useEffect(() => {
    if (!editor) return

    // Get current editor content
    const currentHtml = editor.getHTML()
    const currentText = editor.getText()
    const normalizedValue = value || ''
    const valueText = stripHtml(normalizedValue)
    const isFocused = editor.isFocused

    // CRITICAL: If editor is focused and user is typing/pasting, prioritize preserving editor content
    // This prevents clearing text during active editing sessions
    if (isFocused) {
      // If plain text matches, skip update (handles HTML normalization)
      if (valueText === currentText && currentText.length > 0) {
        // Update refs to keep them in sync even if HTML format differs
        if (normalizedValue !== lastEmittedValueRef.current) {
          lastEmittedValueRef.current = normalizedValue
          lastKnownHtmlRef.current = normalizedValue
        }
        return
      }
      // If HTML matches exactly, definitely skip
      if (normalizedValue === currentHtml) {
        return
      }
    }

    // Skip update if:
    // 1. Value HTML matches what we last emitted (this update came from our onChange)
    //    This is the primary safeguard against race conditions
    if (normalizedValue === lastEmittedValueRef.current) {
      return
    }

    // 2. Value HTML matches current editor content (already in sync)
    if (normalizedValue === currentHtml) {
      lastKnownHtmlRef.current = normalizedValue
      lastEmittedValueRef.current = normalizedValue
      return
    }

    // 3. Value HTML matches last known value (already synced)
    if (normalizedValue === lastKnownHtmlRef.current) {
      return
    }

    // 4. Plain text content matches (handles HTML normalization differences)
    // Only apply this check if we have meaningful content
    if (valueText === currentText && valueText.length > 0 && currentText.length > 0) {
      // Update refs to keep them in sync even if HTML format differs
      lastEmittedValueRef.current = normalizedValue
      lastKnownHtmlRef.current = normalizedValue
      return
    }

    // This is an external update (form reset, profile load, etc.)
    // Only update if the value is actually different from what's in the editor
    lastKnownHtmlRef.current = normalizedValue
    lastEmittedValueRef.current = normalizedValue
    editor.commands.setContent(normalizedValue, false)
    setTextLength(editor.getText().length)
  }, [editor, value])

  const applyAiAssist = (mode: 'rewrite' | 'bullets') => {
    if (!editor) return
    const currentHtml = editor.getHTML()
    if (!stripHtml(currentHtml || '').trim()) return

    if (mode === 'rewrite') {
      // Show prompt modal for LLM rewrite
      setShowPromptModal(true)
      setPrompt('')
      setRewriteError(null)
    } else {
      // Use heuristic-based bullets
      const next = buildAiRewriteHtml(currentHtml || '', { mode, maxLength })
      if (!stripHtml(next || '').trim()) return
      lastKnownHtmlRef.current = next
      lastEmittedValueRef.current = next
      editor.commands.setContent(next, false)
      setTextLength(editor.getText().length)
      onChange(next)
    }
  }

  const handleLlmRewrite = async () => {
    if (!editor || !prompt.trim()) return

    setIsRewriting(true)
    setRewriteError(null)

    try {
      const currentHtml = editor.getHTML()
      const plainText = stripHtml(currentHtml || '').trim()

      if (!plainText) {
        setRewriteError('Please enter some text to rewrite')
        setIsRewriting(false)
        return
      }

      const response = await rewriteText({
        text: plainText,
        prompt: prompt.trim(),
      })

      // Convert plain text response back to HTML
      // Preserve paragraphs (double newlines) and line breaks (single newlines)
      const rewrittenHtml =
        response.rewritten_text
          .split(/\n\n+/)
          .map(para => para.trim())
          .filter(Boolean)
          .map(para => `<p>${para.replace(/\n/g, '<br>')}</p>`)
          .join('') || '<p></p>'

      lastKnownHtmlRef.current = rewrittenHtml
      lastEmittedValueRef.current = rewrittenHtml
      editor.commands.setContent(rewrittenHtml, false)
      setTextLength(editor.getText().length)
      onChange(rewrittenHtml)

      setShowPromptModal(false)
      setPrompt('')
    } catch (error: any) {
      setRewriteError(error.response?.data?.detail || error.message || 'Failed to rewrite text')
    } finally {
      setIsRewriting(false)
    }
  }

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

      {showPromptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
              AI Rewrite
            </h3>
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
                onClick={() => {
                  setShowPromptModal(false)
                  setPrompt('')
                  setRewriteError(null)
                }}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
                disabled={isRewriting}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleLlmRewrite}
                disabled={isRewriting || !prompt.trim()}
                className="rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed dark:hover:bg-blue-500"
              >
                {isRewriting ? 'Rewriting...' : 'Rewrite'}
              </button>
            </div>
          </div>
        </div>
      )}

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
