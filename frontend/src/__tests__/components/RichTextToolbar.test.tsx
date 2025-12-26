import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { Editor } from '@tiptap/react'
import RichTextToolbar from '../../components/richText/RichTextToolbar'

function createEditorMock(overrides?: Partial<Editor>): Editor {
  const chain = {
    focus: vi.fn(() => chain),
    toggleHeading: vi.fn(() => chain),
    toggleBold: vi.fn(() => chain),
    toggleItalic: vi.fn(() => chain),
    toggleUnderline: vi.fn(() => chain),
    toggleStrike: vi.fn(() => chain),
    toggleOrderedList: vi.fn(() => chain),
    toggleBulletList: vi.fn(() => chain),
    extendMarkRange: vi.fn(() => chain),
    unsetLink: vi.fn(() => chain),
    setLink: vi.fn(() => chain),
    unsetAllMarks: vi.fn(() => chain),
    clearNodes: vi.fn(() => chain),
    run: vi.fn(() => true),
  }

  const editor = {
    isActive: vi.fn(() => false),
    getAttributes: vi.fn(() => ({})),
    chain: vi.fn(() => chain),
    ...overrides,
  } as unknown as Editor

  return editor
}

describe('RichTextToolbar', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders the formatting actions', () => {
    render(<RichTextToolbar editor={createEditorMock()} />)

    for (const label of ['H1', 'H2', 'H3', 'B', 'I', 'U', 'S', 'OL', 'UL', 'Link', 'Clear']) {
      expect(screen.getByRole('button', { name: label })).toBeInTheDocument()
    }
  })

  it('toggles bold when clicking B', async () => {
    const user = userEvent.setup()
    const editor = createEditorMock()
    render(<RichTextToolbar editor={editor} />)

    await user.click(screen.getByRole('button', { name: 'B' }))

    const chain = (editor.chain as unknown as ReturnType<typeof vi.fn>).mock.results[0].value
    expect(chain.focus).toHaveBeenCalled()
    expect(chain.toggleBold).toHaveBeenCalled()
    expect(chain.run).toHaveBeenCalled()
  })

  it('sets a link when clicking Link', async () => {
    const user = userEvent.setup()
    const editor = createEditorMock({
      getAttributes: vi.fn(() => ({ href: '' })),
    })
    vi.spyOn(window, 'prompt').mockReturnValue('https://example.com')

    render(<RichTextToolbar editor={editor} />)
    await user.click(screen.getByRole('button', { name: 'Link' }))

    const chain = (editor.chain as unknown as ReturnType<typeof vi.fn>).mock.results[0].value
    expect(chain.focus).toHaveBeenCalled()
    expect(chain.extendMarkRange).toHaveBeenCalledWith('link')
    expect(chain.setLink).toHaveBeenCalledWith({ href: 'https://example.com' })
    expect(chain.run).toHaveBeenCalled()
  })
})
