import { useMemo } from 'react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import { EditorOptions } from '@tiptap/react'

interface EditorConfigOptions {
  id: string
  placeholder?: string
  error?: { message?: string }
  minHeight: number
}

/**
 * Creates TipTap editor extensions configuration
 */
export function useEditorExtensions(placeholder?: string) {
  return useMemo(
    () => [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      Underline,
      Link.configure({ openOnClick: false, autolink: false }),
      Placeholder.configure({ placeholder: placeholder || '' }),
    ],
    [placeholder]
  )
}

/**
 * Creates TipTap editor props configuration
 */
export function getEditorProps({
  id,
  error,
  minHeight,
}: EditorConfigOptions): EditorOptions['editorProps'] {
  return {
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
  }
}
