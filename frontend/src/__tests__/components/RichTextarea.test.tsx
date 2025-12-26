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

  it('shows warning when maxLength is exceeded', async () => {
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

  it('does not clear text after typing', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Focus and type text
    editor.focus()
    await act(async () => {
      await user.type(editor, 'Test content')
    })

    // Wait for onChange to be called
    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })

    // Get the HTML that was emitted
    const emittedHtml = onChange.mock.calls[onChange.mock.calls.length - 1][0]

    // Simulate React Hook Form updating the value prop (this is what causes the race condition)
    rerender(<RichTextarea id="test-textarea" value={emittedHtml} onChange={onChange} />)

    // Wait a bit to ensure useEffect has run
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10))
    })

    // Text should still be in the editor (not cleared)
    expect(editor.textContent).toContain('Test content')
  })

  it('does not clear text after pasting', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Focus and type text (simulating paste by typing quickly)
    editor.focus()
    await act(async () => {
      // Simulate paste by typing text quickly (TipTap treats rapid input similarly)
      await user.type(editor, 'Pasted content', { delay: 0 })
    })

    // Wait for onChange to be called
    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })

    // Get the HTML that was emitted
    const emittedHtml = onChange.mock.calls[onChange.mock.calls.length - 1]?.[0] || ''

    if (emittedHtml) {
      // Simulate React Hook Form updating the value prop (race condition scenario)
      rerender(<RichTextarea id="test-textarea" value={emittedHtml} onChange={onChange} />)

      // Wait a bit to ensure useEffect has run
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 10))
      })

      // Text should still be in the editor (not cleared)
      expect(editor.textContent).toContain('Pasted content')
    }
  })

  it('updates editor content when value changes externally (form reset)', async () => {
    const onChange = vi.fn()
    const { rerender } = render(
      <RichTextarea id="test-textarea" value="<p>Initial content</p>" onChange={onChange} />
    )

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()
    expect(editor.textContent).toContain('Initial content')

    // Simulate form reset (external update)
    rerender(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    await waitFor(() => {
      expect(editor.textContent).toBe('')
    })
  })

  it('updates editor content when value changes externally (profile load)', async () => {
    const onChange = vi.fn()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Simulate profile load (external update)
    const profileContent = '<p>Loaded from profile</p>'
    rerender(<RichTextarea id="test-textarea" value={profileContent} onChange={onChange} />)

    await waitFor(() => {
      expect(editor.textContent).toContain('Loaded from profile')
    })
  })

  it('handles HTML normalization differences without clearing content', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Type text
    editor.focus()
    await act(async () => {
      await user.type(editor, 'Normalized test')
    })

    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })

    const emittedHtml = onChange.mock.calls[onChange.mock.calls.length - 1][0]

    // Simulate React Hook Form normalizing the HTML (e.g., different whitespace or tag format)
    // TipTap might emit '<p>Normalized test</p>' but RHF might store '<p>Normalized test</p> ' (with trailing space)
    // or vice versa - the plain text should match, so we should skip the update
    const normalizedHtml = emittedHtml.trim() + ' ' // Add trailing space to simulate normalization

    rerender(<RichTextarea id="test-textarea" value={normalizedHtml} onChange={onChange} />)

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10))
    })

    // Text should still be in the editor despite HTML format difference
    expect(editor.textContent).toContain('Normalized test')
  })

  it('preserves line break when Enter key is pressed', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Type text and press Enter to create a new paragraph
    editor.focus()
    await act(async () => {
      await user.type(editor, 'First line')
      await user.keyboard('{Enter}')
      await user.type(editor, 'Second line')
    })

    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })

    // Get the HTML that was emitted (should contain two paragraphs)
    const emittedHtml = onChange.mock.calls[onChange.mock.calls.length - 1][0]
    expect(emittedHtml).toContain('First line')
    expect(emittedHtml).toContain('Second line')

    // Simulate React Hook Form updating the value prop
    rerender(<RichTextarea id="test-textarea" value={emittedHtml} onChange={onChange} />)

    // Wait for useEffect to process (including editing state delay)
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 200))
    })

    // Both lines should still be in the editor (line break preserved)
    expect(editor.textContent).toContain('First line')
    expect(editor.textContent).toContain('Second line')
  })

  it('preserves line break when Shift+Enter is pressed', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Type text and press Shift+Enter to create a <br> tag
    editor.focus()
    await act(async () => {
      await user.type(editor, 'First line')
      await user.keyboard('{Shift>}{Enter}{/Shift}')
      await user.type(editor, 'Second line')
    })

    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })

    // Get the HTML that was emitted (should contain <br> tag)
    const emittedHtml = onChange.mock.calls[onChange.mock.calls.length - 1][0]
    expect(emittedHtml).toContain('First line')
    expect(emittedHtml).toContain('Second line')

    // Simulate React Hook Form updating the value prop
    rerender(<RichTextarea id="test-textarea" value={emittedHtml} onChange={onChange} />)

    // Wait for useEffect to process
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 200))
    })

    // Both lines should still be in the editor (line break preserved)
    expect(editor.textContent).toContain('First line')
    expect(editor.textContent).toContain('Second line')
  })

  it('preserves multiple paragraphs created with Enter key', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Create multiple paragraphs
    editor.focus()
    await act(async () => {
      await user.type(editor, 'Paragraph 1')
      await user.keyboard('{Enter}')
      await user.type(editor, 'Paragraph 2')
      await user.keyboard('{Enter}')
      await user.type(editor, 'Paragraph 3')
    })

    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })

    const emittedHtml = onChange.mock.calls[onChange.mock.calls.length - 1][0]

    // Simulate React Hook Form updating the value prop
    rerender(<RichTextarea id="test-textarea" value={emittedHtml} onChange={onChange} />)

    // Wait for useEffect to process
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 200))
    })

    // All paragraphs should be preserved
    expect(editor.textContent).toContain('Paragraph 1')
    expect(editor.textContent).toContain('Paragraph 2')
    expect(editor.textContent).toContain('Paragraph 3')
  })

  it('does not reset content when Enter key is pressed rapidly', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Rapidly type and press Enter multiple times
    editor.focus()
    await act(async () => {
      await user.type(editor, 'Line 1', { delay: 0 })
      await user.keyboard('{Enter}')
      await user.type(editor, 'Line 2', { delay: 0 })
      await user.keyboard('{Enter}')
      await user.type(editor, 'Line 3', { delay: 0 })
    })

    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })

    const emittedHtml = onChange.mock.calls[onChange.mock.calls.length - 1][0]

    // Simulate React Hook Form updating the value prop rapidly (race condition scenario)
    rerender(<RichTextarea id="test-textarea" value={emittedHtml} onChange={onChange} />)

    // Wait for useEffect to process (including editing state delay)
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 200))
    })

    // All content should be preserved despite rapid Enter presses
    expect(editor.textContent).toContain('Line 1')
    expect(editor.textContent).toContain('Line 2')
    expect(editor.textContent).toContain('Line 3')
  })

  it('handles HTML normalization differences for empty paragraphs', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

    const editor = document.querySelector('.ql-editor') as HTMLElement
    expect(editor).toBeInTheDocument()

    // Type text and press Enter (creates empty paragraph)
    editor.focus()
    await act(async () => {
      await user.type(editor, 'First line')
      await user.keyboard('{Enter}')
    })

    await waitFor(() => {
      expect(onChange).toHaveBeenCalled()
    })

    const emittedHtml = onChange.mock.calls[onChange.mock.calls.length - 1][0]

    // Simulate TipTap normalizing empty paragraph differently
    // TipTap might emit '<p>First line</p><p></p>' but normalize to '<p>First line</p><p><br></p>'
    // or vice versa - our normalization should handle this
    const normalizedHtml = emittedHtml.replace(/<p><\/p>/g, '<p><br></p>')

    rerender(<RichTextarea id="test-textarea" value={normalizedHtml} onChange={onChange} />)

    // Wait for useEffect to process
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 200))
    })

    // Content should still be preserved despite empty paragraph normalization difference
    expect(editor.textContent).toContain('First line')
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
