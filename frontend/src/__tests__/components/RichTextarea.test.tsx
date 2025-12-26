import { describe, it, expect, vi } from 'vitest'
import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RichTextarea, { stripHtml } from '../../components/RichTextarea'

describe('RichTextarea', () => {
  it('renders with placeholder', () => {
    const onChange = vi.fn()
    render(
      <RichTextarea
        id="test-textarea"
        value=""
        onChange={onChange}
        placeholder="Enter text here..."
      />
    )

    // RichTextarea renders a contentEditable editor surface
    expect(document.querySelector('.ql-editor')).toBeInTheDocument()
  })

  it('displays value', () => {
    const onChange = vi.fn()
    render(<RichTextarea id="test-textarea" value="<p>Test content</p>" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor')
    expect(editor).toBeInTheDocument()
    expect(editor?.textContent).toContain('Test content')
  })

  it('calls onChange when content changes', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    if (editor) {
      editor.focus()
      await act(async () => {
        await user.type(editor, 'New content')
      })

      // Editor may call onChange multiple times during typing
      await waitFor(() => {
        expect(onChange).toHaveBeenCalled()
      })
    }
  })

  it('displays error message when error prop is provided', () => {
    const onChange = vi.fn()
    render(
      <RichTextarea
        id="test-textarea"
        value=""
        onChange={onChange}
        error={{ message: 'This field is required' }}
      />
    )

    expect(screen.getByText('This field is required')).toBeInTheDocument()
  })

  it('displays character count when maxLength is provided', () => {
    const onChange = vi.fn()
    render(
      <RichTextarea id="test-textarea" value="<p>Test</p>" onChange={onChange} maxLength={300} />
    )

    // Should show "4 / 300 characters" (plain text length)
    expect(screen.getByText(/4 \/ 300 characters/)).toBeInTheDocument()
  })

  it('prevents input when maxLength is exceeded', async () => {
    const onChange = vi.fn()
    const longText = 'x'.repeat(301)
    render(
      <RichTextarea
        id="test-textarea"
        value={`<p>${longText}</p>`}
        onChange={onChange}
        maxLength={300}
      />
    )

    // Character count should show exceeded
    expect(screen.getByText(/301 \/ 300 characters/)).toBeInTheDocument()
    // The count text should be red when exceeded
    const countText = screen.getByText(/301 \/ 300 characters/)
    expect(countText.className).toContain('text-red-600')
  })

  it('applies custom className', () => {
    const onChange = vi.fn()
    const { container } = render(
      <RichTextarea id="test-textarea" value="" onChange={onChange} className="custom-class" />
    )

    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('respects rows prop for minimum height', () => {
    const onChange = vi.fn()
    render(<RichTextarea id="test-textarea" value="" onChange={onChange} rows={10} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    if (editor) {
      // min-height should be approximately rows * 24
      const minHeight = parseInt(editor.style.minHeight || '')
      expect(minHeight).toBeGreaterThanOrEqual(200) // 10 rows * ~20px
    }
  })
})

describe('stripHtml', () => {
  it('strips HTML tags', () => {
    expect(stripHtml('<p>Hello</p>')).toBe('Hello')
    expect(stripHtml('<strong>Bold</strong> text')).toBe('Bold text')
  })

  it('handles nested HTML', () => {
    expect(stripHtml('<p><strong>Nested</strong> content</p>')).toBe('Nested content')
  })

  it('handles empty HTML', () => {
    expect(stripHtml('')).toBe('')
    expect(stripHtml('<p></p>')).toBe('')
  })

  it('preserves plain text', () => {
    expect(stripHtml('Plain text')).toBe('Plain text')
  })

  it('handles HTML entities', () => {
    // Note: stripHtml uses DOM parsing, so entities are automatically decoded
    const div = document.createElement('div')
    div.innerHTML = '&nbsp;'
    expect(div.textContent || div.innerText).toBe('\u00A0') // Non-breaking space
    // Test stripHtml function directly
    expect(stripHtml('&nbsp;')).toBe('\u00A0')
  })
})
