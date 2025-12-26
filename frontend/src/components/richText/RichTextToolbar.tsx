import type { Editor } from '@tiptap/react'

interface RichTextToolbarProps {
  editor: Editor
  disabled?: boolean
}

function Button({
  label,
  onClick,
  isActive,
  disabled,
}: {
  label: string
  onClick: () => void
  isActive?: boolean
  disabled?: boolean
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={[
        'rounded border px-2 py-1 text-xs font-medium',
        'border-gray-300 bg-white text-gray-700 hover:bg-gray-50',
        'disabled:cursor-not-allowed disabled:opacity-50',
        'dark:border-gray-700 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800',
        isActive ? 'ring-2 ring-blue-500 dark:ring-blue-400' : '',
      ].join(' ')}
      aria-pressed={isActive || false}
    >
      {label}
    </button>
  )
}

function setLink(editor: Editor) {
  const current = editor.getAttributes('link').href as string | undefined
  const url = window.prompt('Link URL', current || '')
  if (url === null) return
  if (!url.trim()) {
    editor.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }
  editor.chain().focus().extendMarkRange('link').setLink({ href: url.trim() }).run()
}

export default function RichTextToolbar({ editor, disabled }: RichTextToolbarProps) {
  return (
    <div className="flex flex-wrap items-center gap-1 rounded-t-md border border-b-0 border-gray-300 bg-gray-50 p-1.5 dark:border-gray-700 dark:bg-gray-800">
      <Button
        label="H1"
        disabled={disabled}
        isActive={editor.isActive('heading', { level: 1 })}
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
      />
      <Button
        label="H2"
        disabled={disabled}
        isActive={editor.isActive('heading', { level: 2 })}
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
      />
      <Button
        label="H3"
        disabled={disabled}
        isActive={editor.isActive('heading', { level: 3 })}
        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
      />
      <div className="mx-1 h-4 w-px bg-gray-300 dark:bg-gray-700" />
      <Button
        label="B"
        disabled={disabled}
        isActive={editor.isActive('bold')}
        onClick={() => editor.chain().focus().toggleBold().run()}
      />
      <Button
        label="I"
        disabled={disabled}
        isActive={editor.isActive('italic')}
        onClick={() => editor.chain().focus().toggleItalic().run()}
      />
      <Button
        label="U"
        disabled={disabled}
        isActive={editor.isActive('underline')}
        onClick={() => editor.chain().focus().toggleUnderline().run()}
      />
      <Button
        label="S"
        disabled={disabled}
        isActive={editor.isActive('strike')}
        onClick={() => editor.chain().focus().toggleStrike().run()}
      />
      <div className="mx-1 h-4 w-px bg-gray-300 dark:bg-gray-700" />
      <Button
        label="OL"
        disabled={disabled}
        isActive={editor.isActive('orderedList')}
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
      />
      <Button
        label="UL"
        disabled={disabled}
        isActive={editor.isActive('bulletList')}
        onClick={() => editor.chain().focus().toggleBulletList().run()}
      />
      <div className="mx-1 h-4 w-px bg-gray-300 dark:bg-gray-700" />
      <Button
        label="Link"
        disabled={disabled}
        isActive={editor.isActive('link')}
        onClick={() => setLink(editor)}
      />
      <Button
        label="Clear"
        disabled={disabled}
        onClick={() => editor.chain().focus().unsetAllMarks().clearNodes().run()}
      />
    </div>
  )
}
