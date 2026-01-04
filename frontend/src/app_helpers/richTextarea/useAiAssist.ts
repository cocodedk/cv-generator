import { useState } from 'react'
import { Editor } from '@tiptap/react'
import { buildAiRewriteHtml } from '../ai/aiTextAssist'
import { rewriteText } from '../../services/aiService'
import { stripHtml } from './htmlUtils'

interface UseAiAssistOptions {
  editor: Editor | null
  onChange: (value: string) => void
  maxLength?: number
  lastKnownHtmlRef: React.MutableRefObject<string>
  lastEmittedValueRef: React.MutableRefObject<string>
  setTextLength: (length: number) => void
}

/**
 * Custom hook to handle AI assist functionality (rewrite and bullets)
 */
export function useAiAssist({
  editor,
  onChange,
  maxLength,
  lastKnownHtmlRef,
  lastEmittedValueRef,
  setTextLength,
}: UseAiAssistOptions) {
  const [showPromptModal, setShowPromptModal] = useState(false)
  const [isRewriting, setIsRewriting] = useState(false)
  const [rewriteError, setRewriteError] = useState<string | null>(null)

  const applyAiAssist = (mode: 'rewrite' | 'bullets') => {
    if (!editor) return
    const currentHtml = editor.getHTML()
    if (!stripHtml(currentHtml || '').trim()) return

    if (mode === 'rewrite') {
      // Show prompt modal for LLM rewrite
      setShowPromptModal(true)
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

  const handleLlmRewrite = async (rewritePrompt: string) => {
    if (!editor || !rewritePrompt.trim()) return

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
        prompt: rewritePrompt.trim(),
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
    } catch (error: any) {
      setRewriteError(error.response?.data?.detail || error.message || 'Failed to rewrite text')
    } finally {
      setIsRewriting(false)
    }
  }

  return {
    showPromptModal,
    setShowPromptModal,
    isRewriting,
    rewriteError,
    applyAiAssist,
    handleLlmRewrite,
  }
}
