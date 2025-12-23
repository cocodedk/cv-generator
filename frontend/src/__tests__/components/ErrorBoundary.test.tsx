import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from '../../components/ErrorBoundary'

const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error')
  }
  return <div>No error</div>
}

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    )

    expect(screen.getByText('No error')).toBeInTheDocument()
  })

  it('catches errors and displays error UI', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText(/An unexpected error occurred/)).toBeInTheDocument()

    consoleError.mockRestore()
  })

  it('displays refresh button', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
    const reload = vi.fn()
    Object.defineProperty(window, 'location', {
      value: { reload },
      writable: true,
    })

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    const refreshButton = screen.getByText('Refresh Page')
    expect(refreshButton).toBeInTheDocument()

    consoleError.mockRestore()
  })

  it('displays error details when available', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    const details = screen.getByText('Error details')
    expect(details).toBeInTheDocument()

    consoleError.mockRestore()
  })
})
