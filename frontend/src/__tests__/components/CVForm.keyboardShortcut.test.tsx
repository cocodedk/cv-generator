import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupAxiosMock, setupWindowMocks, createMockCallbacks } from '../helpers/cvForm/mocks'
import { mockCvResponse } from '../helpers/cvForm/testData'
import { renderCVForm, fillNameField } from '../helpers/cvForm/testHelpers'

const mockedAxios = setupAxiosMock()

describe('CVForm - Keyboard Shortcut (Ctrl+S / Cmd+S)', () => {
  const { mockOnSuccess, mockOnError, mockSetLoading } = createMockCallbacks()

  beforeEach(() => {
    vi.clearAllMocks()
    setupWindowMocks()
  })

  const createKeyboardEvent = (
    key: string,
    options: { ctrlKey?: boolean; metaKey?: boolean } = {}
  ) => {
    return new KeyboardEvent('keydown', {
      key,
      ctrlKey: options.ctrlKey ?? false,
      metaKey: options.metaKey ?? false,
      bubbles: true,
      cancelable: true,
    })
  }

  it('saves CV when Ctrl+S is pressed', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(() => {
      expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    })

    // Fill in name field
    await fillNameField('John Doe')

    // Simulate Ctrl+S keypress (works even when input is focused)
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // Wait for save to be called
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

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('saves CV when Cmd+S is pressed (Mac)', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(() => {
      expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    })

    const nameInput = await fillNameField('Jane Doe')
    await act(async () => {
      nameInput.blur()
    })

    // Simulate Cmd+S keypress (Mac)
    const cmdSEvent = createKeyboardEvent('s', { metaKey: true })
    await act(async () => {
      document.dispatchEvent(cmdSEvent)
    })

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalled()
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('saves CV when Ctrl+S is pressed while typing in input field', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(() => {
      expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    })

    // Focus on name input and type
    const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
    await act(async () => {
      nameInput.focus()
      await userEvent.type(nameInput, 'John Doe')
    })

    // Simulate Ctrl+S while input is focused - should now work
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // Wait for save to be called
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

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('saves CV when Ctrl+S is pressed while typing in rich text editor', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(() => {
      expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    })

    // Fill in the required name field first
    await fillNameField('John Doe')

    // Find the rich text editor (TipTap contenteditable)
    const summaryEditor = document.querySelector('.ql-editor') as HTMLElement
    expect(summaryEditor).toBeInTheDocument()

    // Type in the editor
    await act(async () => {
      summaryEditor.focus()
      await userEvent.type(summaryEditor, 'Test summary text')
    })

    // Simulate Ctrl+S while editor is focused - should now work
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // Wait for save to be called
    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalled()
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('does not save when Ctrl+S is pressed while form is submitting', async () => {
    const user = userEvent.setup()
    // Make post hang to simulate submitting state
    mockedAxios.post.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ data: mockCvResponse }), 1000))
    )

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(() => {
      expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    })

    const nameInput = await fillNameField('John Doe')
    await act(async () => {
      nameInput.blur()
    })

    // Start a save operation by clicking submit button
    const submitButton = screen.getByRole('button', { name: /generate cv/i })
    await act(async () => {
      await user.click(submitButton)
    })

    // Wait for button to show "Generating..." state
    await waitFor(() => {
      expect(screen.getByText('Generating...')).toBeInTheDocument()
    })

    // Try Ctrl+S while submitting
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // Wait a bit
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    // post should only be called once (from the button click)
    expect(mockedAxios.post).toHaveBeenCalledTimes(1)
  })

  it('prevents default browser save dialog when Ctrl+S is pressed', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(() => {
      expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    })

    const nameInput = await fillNameField('John Doe')
    await act(async () => {
      nameInput.blur()
    })

    // Create event and check if preventDefault is called
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    const preventDefaultSpy = vi.spyOn(ctrlSEvent, 'preventDefault')

    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // preventDefault should have been called
    expect(preventDefaultSpy).toHaveBeenCalled()
  })

  it('updates CV when Ctrl+S is pressed in edit mode', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        personal_info: { name: 'Jane Doe' },
        experience: [],
        education: [],
        skills: [],
        theme: 'classic',
      },
    })
    mockedAxios.put.mockResolvedValue({ data: { status: 'success' } })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
      cvId: 'test-cv-id',
    })

    await waitFor(() => {
      expect(screen.getByText('Edit CV')).toBeInTheDocument()
    })

    // Wait for form to load
    await waitFor(() => {
      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      expect(nameInput.value).toBe('Jane Doe')
    })

    // Modify name field
    const nameInput = screen.getByLabelText(/full name/i)
    await act(async () => {
      await userEvent.clear(nameInput)
      await userEvent.type(nameInput, 'Updated Name')
      nameInput.blur()
    })

    // Simulate Ctrl+S
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    await waitFor(() => {
      expect(mockedAxios.put).toHaveBeenCalledWith(
        '/api/cv/test-cv-id',
        expect.objectContaining({
          personal_info: expect.objectContaining({
            name: 'Updated Name',
          }),
        })
      )
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('does not trigger save when modals are open', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(() => {
      expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    })

    // Open AI modal
    const generateButton = screen.getByRole('button', { name: /generate from jd/i })
    await act(async () => {
      await userEvent.click(generateButton)
    })

    // Wait for modal to appear - check for modal title instead
    await waitFor(() => {
      expect(screen.getByText(/Generate CV from Job Description/i)).toBeInTheDocument()
    })

    // Try Ctrl+S while modal is open
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // Wait a bit
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    // Save should not have been called
    expect(mockedAxios.post).not.toHaveBeenCalled()
  })

  it('does not trigger save for other keyboard shortcuts', async () => {
    mockedAxios.post.mockResolvedValue({ data: mockCvResponse })

    renderCVForm({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(() => {
      expect(screen.getByText('Create Your CV')).toBeInTheDocument()
    })

    // Try Ctrl+A (select all)
    const ctrlAEvent = createKeyboardEvent('a', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlAEvent)
    })

    // Try Ctrl+C (copy)
    const ctrlCEvent = createKeyboardEvent('c', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlCEvent)
    })

    // Try just 's' without Ctrl
    const sEvent = createKeyboardEvent('s')
    await act(async () => {
      document.dispatchEvent(sEvent)
    })

    // Wait a bit
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    // Save should not have been called
    expect(mockedAxios.post).not.toHaveBeenCalled()
  })
})
