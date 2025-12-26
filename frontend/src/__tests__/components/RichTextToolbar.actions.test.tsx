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

describe('RichTextToolbar actions', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('toggles heading levels when clicking H1/H2/H3', async () => {
    const user = userEvent.setup()
    const editor = createEditorMock()
    render(<RichTextToolbar editor={editor} />)

    await user.click(screen.getByRole('button', { name: 'H1' }))
    await user.click(screen.getByRole('button', { name: 'H2' }))
    await user.click(screen.getByRole('button', { name: 'H3' }))

    const chain = (editor.chain as unknown as ReturnType<typeof vi.fn>).mock.results[0].value
    expect(chain.toggleHeading).toHaveBeenCalledWith({ level: 1 })
    expect(chain.toggleHeading).toHaveBeenCalledWith({ level: 2 })
    expect(chain.toggleHeading).toHaveBeenCalledWith({ level: 3 })
    expect(chain.run).toHaveBeenCalled()
  })

  it('toggles inline marks when clicking I/U/S', async () => {
    const user = userEvent.setup()
    const editor = createEditorMock()
    render(<RichTextToolbar editor={editor} />)

    await user.click(screen.getByRole('button', { name: 'I' }))
    await user.click(screen.getByRole('button', { name: 'U' }))
    await user.click(screen.getByRole('button', { name: 'S' }))

    const chain = (editor.chain as unknown as ReturnType<typeof vi.fn>).mock.results[0].value
    expect(chain.toggleItalic).toHaveBeenCalled()
    expect(chain.toggleUnderline).toHaveBeenCalled()
    expect(chain.toggleStrike).toHaveBeenCalled()
    expect(chain.run).toHaveBeenCalled()
  })

  it('toggles list types when clicking OL/UL', async () => {
    const user = userEvent.setup()
    const editor = createEditorMock()
    render(<RichTextToolbar editor={editor} />)

    await user.click(screen.getByRole('button', { name: 'OL' }))
    await user.click(screen.getByRole('button', { name: 'UL' }))

    const chain = (editor.chain as unknown as ReturnType<typeof vi.fn>).mock.results[0].value
    expect(chain.toggleOrderedList).toHaveBeenCalled()
    expect(chain.toggleBulletList).toHaveBeenCalled()
    expect(chain.run).toHaveBeenCalled()
  })

  it('unsets a link when Link prompt is blank', async () => {
    const user = userEvent.setup()
    const editor = createEditorMock({
      getAttributes: vi.fn(() => ({ href: 'https://existing.example' })),
    })
    vi.spyOn(window, 'prompt').mockReturnValue('   ')

    render(<RichTextToolbar editor={editor} />)
    await user.click(screen.getByRole('button', { name: 'Link' }))

    const chain = (editor.chain as unknown as ReturnType<typeof vi.fn>).mock.results[0].value
    expect(chain.extendMarkRange).toHaveBeenCalledWith('link')
    expect(chain.unsetLink).toHaveBeenCalled()
    expect(chain.run).toHaveBeenCalled()
  })

  it('does nothing when Link prompt is cancelled', async () => {
    const user = userEvent.setup()
    const editor = createEditorMock()
    vi.spyOn(window, 'prompt').mockReturnValue(null)

    render(<RichTextToolbar editor={editor} />)
    await user.click(screen.getByRole('button', { name: 'Link' }))

    expect(editor.chain).not.toHaveBeenCalled()
  })

  it('clears marks and nodes when clicking Clear', async () => {
    const user = userEvent.setup()
    const editor = createEditorMock()
    render(<RichTextToolbar editor={editor} />)

    await user.click(screen.getByRole('button', { name: 'Clear' }))

    const chain = (editor.chain as unknown as ReturnType<typeof vi.fn>).mock.results[0].value
    expect(chain.unsetAllMarks).toHaveBeenCalled()
    expect(chain.clearNodes).toHaveBeenCalled()
    expect(chain.run).toHaveBeenCalled()
  })

  it('disables all actions when disabled', () => {
    render(<RichTextToolbar editor={createEditorMock()} disabled />)

    for (const label of ['H1', 'H2', 'H3', 'B', 'I', 'U', 'S', 'OL', 'UL', 'Link', 'Clear']) {
      expect(screen.getByRole('button', { name: label })).toBeDisabled()
    }
  })
})
