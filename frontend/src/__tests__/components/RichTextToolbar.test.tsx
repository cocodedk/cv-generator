import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { Editor } from '@tiptap/react'
import RichTextToolbar from '../../components/richText/RichTextToolbar'

function createEditorMock(overrides?: Partial<Editor>): Editor {
  type Chain = {
    focus: () => Chain
    toggleHeading: (options: { level: number }) => Chain
    toggleBold: () => Chain
    toggleItalic: () => Chain
    toggleUnderline: () => Chain
    toggleStrike: () => Chain
    toggleOrderedList: () => Chain
    toggleBulletList: () => Chain
    extendMarkRange: (mark: string) => Chain
    unsetLink: () => Chain
    setLink: (attrs: { href: string }) => Chain
    unsetAllMarks: () => Chain
    clearNodes: () => Chain
    run: () => boolean
  }

  const chain = {} as Chain
  chain.focus = vi.fn(() => chain)
  chain.toggleHeading = vi.fn(() => chain)
  chain.toggleBold = vi.fn(() => chain)
  chain.toggleItalic = vi.fn(() => chain)
  chain.toggleUnderline = vi.fn(() => chain)
  chain.toggleStrike = vi.fn(() => chain)
  chain.toggleOrderedList = vi.fn(() => chain)
  chain.toggleBulletList = vi.fn(() => chain)
  chain.extendMarkRange = vi.fn(() => chain)
  chain.unsetLink = vi.fn(() => chain)
  chain.setLink = vi.fn(() => chain)
  chain.unsetAllMarks = vi.fn(() => chain)
  chain.clearNodes = vi.fn(() => chain)
  chain.run = vi.fn(() => true)

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
