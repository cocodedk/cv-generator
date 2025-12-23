import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MessageDisplay from '../../components/MessageDisplay'
import { Message } from '../../app_helpers/useMessage'

describe('MessageDisplay', () => {
  it('renders null when no message', () => {
    const { container } = render(<MessageDisplay message={null} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders success message', () => {
    const message: Message = {
      type: 'success',
      text: 'Success message',
    }
    render(<MessageDisplay message={message} />)

    expect(screen.getByText('Success message')).toBeInTheDocument()
    const messageDiv = screen.getByText('Success message').closest('div')
    expect(messageDiv).toHaveClass('bg-green-50')
  })

  it('renders error message', () => {
    const message: Message = {
      type: 'error',
      text: 'Error message',
    }
    render(<MessageDisplay message={message} />)

    expect(screen.getByText('Error message')).toBeInTheDocument()
    const messageDiv = screen.getByText('Error message').closest('div')
    expect(messageDiv).toHaveClass('bg-red-50')
  })
})
