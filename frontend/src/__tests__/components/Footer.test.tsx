import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Footer from '../../components/Footer'

describe('Footer', () => {
  it('renders owner name and company link', () => {
    render(<Footer />)

    expect(screen.getByText(/Babak Bandpey/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'cocode.dk' })).toHaveAttribute(
      'href',
      'https://cocode.dk'
    )
  })
})
