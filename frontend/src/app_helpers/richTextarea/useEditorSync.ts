import { useEffect } from 'react'
import { Editor } from '@tiptap/react'
import { hasListHtml, normalizeHtmlForComparison, stripHtml } from './htmlUtils'

interface UseEditorSyncOptions {
  editor: Editor | null
  value: string
  onChange: (value: string) => void
  isEditingRef: React.MutableRefObject<boolean>
  lastKnownHtmlRef: React.MutableRefObject<string>
  lastEmittedValueRef: React.MutableRefObject<string>
  setTextLength: (length: number) => void
}

/**
 * Custom hook to sync TipTap editor content with external value prop.
 * Handles race conditions and HTML normalization differences.
 */
export function useEditorSync({
  editor,
  value,
  onChange,
  isEditingRef,
  lastKnownHtmlRef,
  lastEmittedValueRef,
  setTextLength,
}: UseEditorSyncOptions) {
  useEffect(() => {
    if (!editor) return

    // CRITICAL: Skip updates while user is actively editing to prevent race conditions
    // This prevents line breaks and other edits from being reset
    if (isEditingRef.current) {
      return
    }

    // Get current editor content
    const currentHtml = editor.getHTML()
    const currentText = editor.getText()
    const normalizedValue = value || ''
    const valueText = stripHtml(normalizedValue)
    const isFocused = editor.isFocused

    // Normalize HTML for comparison to handle TipTap's normalization differences
    const normalizedCurrentHtml = normalizeHtmlForComparison(currentHtml)
    const normalizedValueHtml = normalizeHtmlForComparison(normalizedValue)
    const normalizedLastEmitted = normalizeHtmlForComparison(lastEmittedValueRef.current)
    const normalizedLastKnown = normalizeHtmlForComparison(lastKnownHtmlRef.current)
    const listSensitive = hasListHtml(normalizedValue) || hasListHtml(currentHtml)

    // CRITICAL: If editor is focused and user is typing/pasting, prioritize preserving editor content
    // This prevents clearing text during active editing sessions
    if (isFocused) {
      // If plain text matches, skip update (handles HTML normalization)
      if (valueText === currentText && currentText.length > 0) {
        if (!listSensitive || normalizedValueHtml === normalizedCurrentHtml) {
          // Update refs to keep them in sync even if HTML format differs
          if (normalizedValue !== lastEmittedValueRef.current) {
            lastEmittedValueRef.current = normalizedValue
            lastKnownHtmlRef.current = normalizedValue
          }
          return
        }
      }
      // If normalized HTML matches, definitely skip
      if (normalizedValueHtml === normalizedCurrentHtml) {
        return
      }
    }

    // Skip update if:
    // 1. Normalized value HTML matches what we last emitted (this update came from our onChange)
    //    This is the primary safeguard against race conditions
    if (normalizedValueHtml === normalizedLastEmitted) {
      if (!listSensitive || normalizedValueHtml === normalizedCurrentHtml) {
        return
      }
    }

    // 2. Normalized value HTML matches current editor content (already in sync)
    if (normalizedValueHtml === normalizedCurrentHtml) {
      lastKnownHtmlRef.current = normalizedValue
      lastEmittedValueRef.current = normalizedValue
      return
    }

    // 3. Normalized value HTML matches last known value (already synced)
    if (normalizedValueHtml === normalizedLastKnown) {
      if (!listSensitive || normalizedValueHtml === normalizedCurrentHtml) {
        return
      }
    }

    // 4. Plain text content matches AND HTML is normalized to be the same
    // Only skip if both match (handles HTML normalization differences without losing formatting)
    if (
      valueText === currentText &&
      valueText.length > 0 &&
      currentText.length > 0 &&
      normalizedValueHtml === normalizedCurrentHtml
    ) {
      // Update refs to keep them in sync
      lastEmittedValueRef.current = normalizedValue
      lastKnownHtmlRef.current = normalizedValue
      return
    }

    // If plain text matches but HTML differs, we MUST update to preserve formatting
    // This handles the case where formatting changes but text stays the same

    // This is an external update (form reset, profile load, etc.)
    // Only update if the value is actually different from what's in the editor
    lastKnownHtmlRef.current = normalizedValue
    lastEmittedValueRef.current = normalizedValue
    editor.commands.setContent(normalizedValue, false)
    setTextLength(editor.getText().length)
  }, [editor, value, onChange, isEditingRef, lastKnownHtmlRef, lastEmittedValueRef, setTextLength])
}
