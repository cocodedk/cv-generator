import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import axios from 'axios'
import CVForm from '../../components/CVForm'

// Mock axios
vi.mock('axios')
const mockedAxios = axios as any

describe('CVForm', () => {
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()
  const mockSetLoading = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock window.open
    global.window.open = vi.fn()
  })

  it('renders form with all sections', () => {
    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    expect(screen.getByText('Personal Information')).toBeInTheDocument()
    expect(screen.getByText('Work Experience')).toBeInTheDocument()
    expect(screen.getByText('Education')).toBeInTheDocument()
    expect(screen.getByText('Skills')).toBeInTheDocument()
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({
      data: { cv_id: 'test-id', filename: 'cv_test.odt', status: 'success' },
    })

    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    // Fill in required name field
    const nameInput = screen.getByLabelText(/full name/i)
    await user.type(nameInput, 'John Doe')

    // Submit form
    const submitButton = screen.getByRole('button', { name: /generate cv/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/generate-cv',
        expect.objectContaining({
          personal_info: expect.objectContaining({
            name: 'John Doe',
          }),
        })
      )
    })

    expect(mockSetLoading).toHaveBeenCalledWith(true)
    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('handles form submission error', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockRejectedValue({
      response: { data: { detail: 'Server error' } },
    })

    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    const nameInput = screen.getByLabelText(/full name/i)
    await user.type(nameInput, 'John Doe')

    const submitButton = screen.getByRole('button', { name: /generate cv/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Server error')
    })
  })

  it('validates required name field', async () => {
    const user = userEvent.setup()

    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    const submitButton = screen.getByRole('button', { name: /generate cv/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    expect(mockedAxios.post).not.toHaveBeenCalled()
  })

  it('allows theme selection', async () => {
    const user = userEvent.setup()

    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    const themeSelect = screen.getByLabelText(/theme/i)
    await user.selectOptions(themeSelect, 'modern')

    expect(themeSelect).toHaveValue('modern')
  })
})
