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

  it('loads profile data when Load from Profile is clicked', async () => {
    const user = userEvent.setup()
    const profileData = {
      personal_info: {
        name: 'John Doe',
        email: 'john@example.com',
      },
      experience: [{ title: 'Developer', company: 'Tech Corp', start_date: '2020-01' }],
      education: [{ degree: 'BS CS', institution: 'University', year: '2018' }],
      skills: [{ name: 'Python' }],
    }
    mockedAxios.get.mockResolvedValue({ data: profileData })

    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    const loadButton = screen.getByRole('button', { name: /load from profile/i })
    await user.click(loadButton)

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/profile')
    })

    await waitFor(() => {
      expect(screen.getByText('Select Items to Include')).toBeInTheDocument()
    })
  })

  it('handles profile load error when no profile exists', async () => {
    const user = userEvent.setup()
    mockedAxios.get.mockRejectedValue({
      response: { status: 404 },
    })

    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    const loadButton = screen.getByRole('button', { name: /load from profile/i })
    await user.click(loadButton)

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('No profile found. Please save a profile first.')
    })
  })

  it('saves current form data to profile', async () => {
    const user = userEvent.setup()
    mockedAxios.post.mockResolvedValue({ data: { status: 'success' } })

    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    const nameInput = screen.getByLabelText(/full name/i)
    await user.type(nameInput, 'John Doe')

    const saveButton = screen.getByRole('button', { name: /save to profile/i })
    await user.click(saveButton)

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/profile',
        expect.objectContaining({
          personal_info: expect.objectContaining({
            name: 'John Doe',
          }),
        })
      )
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('allows selecting experiences and educations from profile', async () => {
    const user = userEvent.setup()
    const profileData = {
      personal_info: {
        name: 'John Doe',
      },
      experience: [
        { title: 'Developer', company: 'Tech Corp', start_date: '2020-01' },
        { title: 'Senior Dev', company: 'Big Corp', start_date: '2023-01' },
      ],
      education: [{ degree: 'BS CS', institution: 'University', year: '2018' }],
      skills: [],
    }
    mockedAxios.get.mockResolvedValue({ data: profileData })

    render(<CVForm onSuccess={mockOnSuccess} onError={mockOnError} setLoading={mockSetLoading} />)

    const loadButton = screen.getByRole('button', { name: /load from profile/i })
    await user.click(loadButton)

    await waitFor(() => {
      expect(screen.getByText('Select Items to Include')).toBeInTheDocument()
    })

    // Check that experiences are shown
    expect(screen.getByText(/developer/i)).toBeInTheDocument()
    expect(screen.getByText(/senior dev/i)).toBeInTheDocument()

    // Uncheck one experience
    const checkboxes = screen.getAllByRole('checkbox')
    await user.click(checkboxes[0]) // Uncheck first experience

    const loadSelectedButton = screen.getByRole('button', { name: /load selected/i })
    await user.click(loadSelectedButton)

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })
})
