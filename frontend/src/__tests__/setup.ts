import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import React from 'react'
import { afterEach, vi } from 'vitest'

declare global {
  interface GlobalThis {
    IS_REACT_ACT_ENVIRONMENT: boolean
  }
}

;(globalThis as unknown as { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

// TipTap/ProseMirror relies on DOM geometry APIs not implemented in jsdom (elementFromPoint/getClientRects).
// For unit tests, mock TipTap with a minimal contenteditable surface that preserves the public API shape.
vi.mock('@tiptap/react', () => {
  type EditorUpdateHandler = (payload: { editor: any }) => void
  type UseEditorConfig = {
    content?: string
    editorProps?: { attributes?: Record<string, unknown> }
    onUpdate?: EditorUpdateHandler
  }

  const parseStyle = (style: unknown): React.CSSProperties | undefined => {
    if (typeof style !== 'string') return undefined
    const rules = style
      .split(';')
      .map(v => v.trim())
      .filter(Boolean)
    const result: Record<string, string> = {}
    for (const rule of rules) {
      const [rawKey, rawValue] = rule.split(':').map(v => v.trim())
      if (!rawKey || !rawValue) continue
      const key = rawKey.replace(/-([a-z])/g, (_, char: string) => char.toUpperCase())
      result[key] = rawValue
    }
    return result as unknown as React.CSSProperties
  }

  const createEditor = (config: UseEditorConfig) => {
    let html = typeof config.content === 'string' ? config.content : ''
    const toText = (value: string) => value.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ')
    const editor = {
      getHTML: () => html,
      getText: () => toText(html),
      isActive: () => false,
      getAttributes: () => ({}),
      commands: {
        setContent: (next: string) => {
          html = next
        },
      },
      chain: () => {
        const chainObj = {
          focus: () => chainObj,
          toggleHeading: () => chainObj,
          toggleBold: () => chainObj,
          toggleItalic: () => chainObj,
          toggleUnderline: () => chainObj,
          toggleStrike: () => chainObj,
          toggleOrderedList: () => chainObj,
          toggleBulletList: () => chainObj,
          extendMarkRange: () => chainObj,
          unsetLink: () => chainObj,
          setLink: () => chainObj,
          unsetAllMarks: () => chainObj,
          clearNodes: () => chainObj,
          run: () => true,
        }
        return chainObj
      },
      __setHtml: (next: string) => {
        html = next
        config.onUpdate?.({ editor })
      },
      __getEditorProps: () => config.editorProps,
    }
    return editor
  }

  const useEditor = (config: UseEditorConfig) => createEditor(config)

  const EditorContent = ({ editor }: { editor: any }) => {
    if (!editor) return null
    const attrs = (editor.__getEditorProps?.()?.attributes || {}) as Record<string, unknown>
    const className = typeof attrs.class === 'string' ? attrs.class : 'ql-editor'
    const style = parseStyle(attrs.style)
    const { class: _class, style: _style, ...rest } = attrs as Record<string, unknown>
    const props: Record<string, unknown> = { ...rest, className, style }

    return React.createElement('div', {
      ...props,
      contentEditable: true,
      suppressContentEditableWarning: true,
      dangerouslySetInnerHTML: { __html: editor.getHTML() },
      onInput: (e: React.FormEvent<HTMLDivElement>) => {
        const next = `<p>${(e.currentTarget.textContent || '').trim()}</p>`
        editor.__setHtml(next)
      },
    })
  }

  return { useEditor, EditorContent }
})

// Cleanup after each test
afterEach(() => {
  cleanup()
})

export {}
