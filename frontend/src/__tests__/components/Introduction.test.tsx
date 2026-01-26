import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import Introduction from '../../components/Introduction'

describe('Introduction', () => {
  beforeEach(() => {
    const templateIndex = {
      generated_at: '2024-01-01T00:00:00Z',
      profile_name: 'Jane Doe',
      templates: [
        {
          layout: 'modern-sidebar',
          theme: 'professional',
          file: 'jane-doe-modern-sidebar-professional.html',
          pdf_file: 'pdfs/jane-doe-modern-sidebar-professional.pdf',
          name: 'Modern Sidebar (professional)',
          description: 'A professional layout.',
          print_friendly: false,
          web_optimized: true,
        },
      ],
    }

    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({
        ok: true,
        json: async () => templateIndex,
      })) as unknown as typeof fetch
    )
  })

  it('renders a PDF download link when pdf_file is provided', async () => {
    render(<Introduction />)

    const downloadLink = await screen.findByRole('link', { name: /download pdf/i })

    expect(downloadLink).toHaveAttribute(
      'href',
      '/templates/pdfs/jane-doe-modern-sidebar-professional.pdf'
    )
    expect(downloadLink).toHaveAttribute('download', 'Jane Doe - Modern Sidebar (professional).pdf')
  })
})
