import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { mockProfileDataWithMultipleExperiences, mockCvResponse } from '../helpers/cvForm/testData'
import {
  renderCVForm,
  fillNameField,
  submitForm,
  clickLoadProfileButton,
  clickSaveToProfileButton,
} from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  it('renders form with all sections', () => {
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    expect(screen.getByText('Personal Information')).toBeInTheDocument()
    expect(screen.getByText('Work Experience')).toBeInTheDocument()
    expect(screen.getByText('Education')).toBeInTheDocument()
    expect(screen.getByText('Skills')).toBeInTheDocument()
  })

  it('submits form with valid data', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await fillNameField('John Doe')
    await submitForm()

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/save-cv',
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
    mockedAxios.post.mockRejectedValue({
      response: { data: { detail: 'Server error' } },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await fillNameField('John Doe')
    await submitForm()

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Server error')
    })
  })

  it('validates required name field', async () => {
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await submitForm()

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    expect(mockedAxios.post).not.toHaveBeenCalled()
  })

  it('allows theme selection', async () => {
    const user = userEvent.setup()

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    const themeSelect = screen.getByLabelText(/theme/i)
    await act(async () => {
      await user.selectOptions(themeSelect, 'modern')
    })

    expect(themeSelect).toHaveValue('modern')
  })

  it('has all theme options available', async () => {
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    const themeSelect = screen.getByLabelText(/theme/i) as HTMLSelectElement
    const options = Array.from(themeSelect.options).map(opt => opt.value)

    const expectedThemes = [
      'accented',
      'classic',
      'colorful',
      'creative',
      'elegant',
      'executive',
      'minimal',
      'modern',
      'professional',
      'tech',
    ]

    expect(options).toEqual(expect.arrayContaining(expectedThemes))
    expect(options.length).toBe(expectedThemes.length)
  })

  it('shows profile selection modal when Load from Profile is clicked', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        profiles: [
          {
            name: 'John Doe',
            updated_at: '2024-01-01T00:00:00Z',
            language: 'en',
          },
        ],
      },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/profiles')
    })

    await waitFor(() => {
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })
  })

  it('handles profile load error when no profiles exist', async () => {
    mockedAxios.get.mockResolvedValue({
      data: { profiles: [] },
    })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    await waitFor(() => {
      expect(
        screen.getByText('No profiles found. Please create a profile first.')
      ).toBeInTheDocument()
    })
  })

  it('saves current form data to profile', async () => {
    mockedAxios.post.mockResolvedValue({ data: { status: 'success' } })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await fillNameField('John Doe')
    await clickSaveToProfileButton()

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

    // Mock profile list API
    mockedAxios.get
      .mockResolvedValueOnce({
        data: {
          profiles: [
            {
              name: 'John Doe',
              updated_at: '2024-01-01T00:00:00Z',
              language: 'en',
            },
          ],
        },
      })
      // Mock profile by ID API
      .mockResolvedValueOnce({ data: mockProfileDataWithMultipleExperiences })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await clickLoadProfileButton()

    // Profile selection modal should appear
    await waitFor(() => {
      expect(screen.getByText('Select Profile to Load')).toBeInTheDocument()
    })

    // Click on the profile to select it
    const profileButton = screen.getByText('John Doe')
    await act(async () => {
      await user.click(profileButton)
    })

    // Profile loader modal should appear
    await waitFor(() => {
      expect(screen.getByText('Select Items to Include')).toBeInTheDocument()
    })

    expect(screen.getByText(/developer/i)).toBeInTheDocument()
    expect(screen.getByText(/senior dev/i)).toBeInTheDocument()

    const checkboxes = screen.getAllByRole('checkbox')
    await act(async () => {
      await user.click(checkboxes[0])
    })

    const loadSelectedButton = screen.getByRole('button', { name: /load selected/i })
    await act(async () => {
      await user.click(loadSelectedButton)
    })

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('renders target company and job title fields', () => {
    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    expect(screen.getByPlaceholderText('e.g. Senior Software Engineer')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('e.g. Google')).toBeInTheDocument()
  })

  it('allows target company and job title input', async () => {
    const user = userEvent.setup()

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    const jobTitleInput = screen.getByLabelText(/job title/i)
    const companyInput = screen.getByLabelText(/target company/i)

    await act(async () => {
      await user.type(jobTitleInput, 'Senior Software Engineer')
      await user.type(companyInput, 'Google')
    })

    expect(jobTitleInput).toHaveValue('Senior Software Engineer')
    expect(companyInput).toHaveValue('Google')
  })

  it('includes target fields in form submission', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await fillNameField('John Doe')

    // Fill in target fields using placeholder text to ensure we get the right inputs
    const user = userEvent.setup()
    const jobTitleInput = screen.getByPlaceholderText('e.g. Senior Software Engineer')
    const companyInput = screen.getByPlaceholderText('e.g. Google')

    await act(async () => {
      await user.type(jobTitleInput, 'Senior Developer')
      await user.type(companyInput, 'Tech Corp')
    })

    await submitForm()

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/save-cv',
        expect.objectContaining({
          personal_info: expect.objectContaining({
            name: 'John Doe',
          }),
          target_role: 'Senior Developer',
          target_company: 'Tech Corp',
        })
      )
    })
  })
})
