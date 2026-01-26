import { describe, it, expect, beforeEach, vi } from 'vitest'
import { waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as profileService from '../../services/profileService'
import { renderProfileManager } from '../helpers/profileManager/testHelpers'
import { within } from '@testing-library/react'
import {
  createMockCallbacks,
  setupWindowMocks,
  createProfileData,
} from '../helpers/profileManager/mocks'

vi.mock('../../services/profileService')
const mockedProfileService = profileService as any

describe('ProfileManager - Keyboard Shortcut (Ctrl+S / Cmd+S)', () => {
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

  it('saves profile when Ctrl+S is pressed and not in input field', async () => {
    mockedProfileService.getProfile.mockResolvedValue(null)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    // Wait for loading to complete
    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Type in name field
    const nameInput = within(container).getByLabelText(/full name/i)
    await act(async () => {
      await userEvent.type(nameInput, 'John Doe')
      // Blur the input to simulate user clicking elsewhere
      nameInput.blur()
    })

    // Simulate Ctrl+S keypress
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // Wait for save to be called
    await waitFor(() => {
      expect(mockedProfileService.saveProfile).toHaveBeenCalled()
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('saves profile when Cmd+S is pressed (Mac)', async () => {
    mockedProfileService.getProfile.mockResolvedValue(null)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Type in name field and blur
    const nameInput = within(container).getByLabelText(/full name/i)
    await act(async () => {
      await userEvent.type(nameInput, 'Jane Doe')
      nameInput.blur()
    })

    // Simulate Cmd+S keypress (Mac)
    const cmdSEvent = createKeyboardEvent('s', { metaKey: true })
    await act(async () => {
      document.dispatchEvent(cmdSEvent)
    })

    await waitFor(() => {
      expect(mockedProfileService.saveProfile).toHaveBeenCalled()
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('does not save when Ctrl+S is pressed while typing in input field', async () => {
    mockedProfileService.getProfile.mockResolvedValue(null)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Focus on name input
    const nameInput = within(container).getByLabelText(/full name/i) as HTMLInputElement
    await act(async () => {
      nameInput.focus()
    })

    // Simulate Ctrl+S while input is focused
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // Wait a bit to ensure save is not called
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    // Save should not have been called
    expect(mockedProfileService.saveProfile).not.toHaveBeenCalled()
    expect(mockOnSuccess).not.toHaveBeenCalled()
  })

  it('does not save when Ctrl+S is pressed while typing in textarea', async () => {
    mockedProfileService.getProfile.mockResolvedValue(null)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Find the rich text editor (it uses contenteditable)
    await waitFor(() => {
      const summaryEditor = document.querySelector('[contenteditable="true"]')
      expect(summaryEditor).toBeInTheDocument()
    })

    const summaryEditor = document.querySelector('[contenteditable="true"]') as HTMLElement
    await act(async () => {
      summaryEditor.focus()
    })

    // Simulate Ctrl+S while editor is focused
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // Wait a bit to ensure save is not called
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    // Save should not have been called
    expect(mockedProfileService.saveProfile).not.toHaveBeenCalled()
    expect(mockOnSuccess).not.toHaveBeenCalled()
  })

  it('does not save when Ctrl+S is pressed while form is submitting', async () => {
    const user = userEvent.setup()
    mockedProfileService.getProfile.mockResolvedValue(null)
    // Make saveProfile hang to simulate submitting state
    mockedProfileService.saveProfile.mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 1000))
    )

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Fill in required name field
    const nameInput = within(container).getByLabelText(/full name/i)
    await act(async () => {
      await user.type(nameInput, 'John Doe')
      nameInput.blur()
    })

    // Start a save operation by clicking submit button
    const submitButton = within(container)
      .getAllByRole('button')
      .find(
        btn =>
          btn.textContent?.includes('Save Profile') || btn.textContent?.includes('Update Profile')
      )
    await act(async () => {
      await user.click(submitButton!)
    })

    // Wait for saveProfile to be called (indicating form submission started)
    await waitFor(() => {
      expect(mockedProfileService.saveProfile).toHaveBeenCalled()
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

    // saveProfile should only be called once (from the button click)
    expect(mockedProfileService.saveProfile).toHaveBeenCalledTimes(1)
  })

  it('prevents default browser save dialog when Ctrl+S is pressed', async () => {
    mockedProfileService.getProfile.mockResolvedValue(null)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Create event and check if preventDefault is called
    const ctrlSEvent = createKeyboardEvent('s', { ctrlKey: true })
    const preventDefaultSpy = vi.spyOn(ctrlSEvent, 'preventDefault')

    await act(async () => {
      document.dispatchEvent(ctrlSEvent)
    })

    // preventDefault should have been called
    expect(preventDefaultSpy).toHaveBeenCalled()
  })

  it('updates existing profile when Ctrl+S is pressed', async () => {
    const profileData = createProfileData()
    mockedProfileService.getProfile.mockResolvedValue(profileData)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Modify a field
    const nameInput = within(container).getByLabelText(/full name/i)
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
      const calls = mockedProfileService.saveProfile.mock.calls
      expect(calls.length).toBe(1)
      const calledData = calls[0][0]
      expect(calledData.personal_info.name).toBe('Updated Name')
    })

    expect(mockOnSuccess).toHaveBeenCalled()
  })

  it('does not trigger save for other keyboard shortcuts', async () => {
    mockedProfileService.getProfile.mockResolvedValue(null)
    mockedProfileService.saveProfile.mockResolvedValue({ status: 'success' })

    const { container } = renderProfileManager({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
      setLoading: mockSetLoading,
    })

    await waitFor(
      () => {
        expect(within(container).queryByText('Loading profile...')).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )

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
    expect(mockedProfileService.saveProfile).not.toHaveBeenCalled()
  })
})
