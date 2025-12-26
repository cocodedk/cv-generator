import { describe, it, expect, vi } from 'vitest'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RichTextarea from '../../components/RichTextarea'

describe('RichTextarea - AI Assist', () => {
  it('hides AI assist buttons by default', () => {
    const onChange = vi.fn()
    render(<RichTextarea id="test-textarea" value="<p>Test</p>" onChange={onChange} />)
    expect(screen.queryByRole('button', { name: /ai rewrite/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /ai bullets/i })).not.toBeInTheDocument()
  })

  it('shows AI assist buttons when enabled', () => {
    const onChange = vi.fn()
    render(<RichTextarea id="test-textarea" value="" onChange={onChange} showAiAssist={true} />)
    expect(screen.getByRole('button', { name: /ai rewrite/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ai bullets/i })).toBeInTheDocument()
  })

  it('does not call onChange when empty', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<RichTextarea id="test-textarea" value="" onChange={onChange} showAiAssist={true} />)
    await act(async () => {
      await user.click(screen.getByRole('button', { name: /ai rewrite/i }))
    })
    await act(async () => {
      await user.click(screen.getByRole('button', { name: /ai bullets/i }))
    })
    expect(onChange).not.toHaveBeenCalled()
  })

  it('AI bullets rewrites to bullet HTML', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(
      <RichTextarea
        id="test-textarea"
        value="<p>worked on api. helped improve performance.</p>"
        onChange={onChange}
        showAiAssist={true}
      />
    )

    await act(async () => {
      await user.click(screen.getByRole('button', { name: /ai bullets/i }))
    })

    expect(onChange).toHaveBeenCalledTimes(1)
    expect(onChange).toHaveBeenCalledWith(expect.stringContaining('<ul>'))
    expect(onChange).toHaveBeenCalledWith(expect.stringContaining('<li>Api</li>'))
    expect(onChange).toHaveBeenCalledWith(expect.stringContaining('<li>Improve performance</li>'))
  })
})
