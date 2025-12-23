import { expect } from 'vitest'
import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CVForm from '../../../components/CVForm'

export interface CVFormProps {
  onSuccess: (message: string) => void
  onError: (message: string) => void
  setLoading: (loading: boolean) => void
  cvId?: string | null
}

export const renderCVForm = (props: CVFormProps) => {
  return render(
    <CVForm
      onSuccess={props.onSuccess}
      onError={props.onError}
      setLoading={props.setLoading}
      cvId={props.cvId}
    />
  )
}

export const fillNameField = async (name: string) => {
  const user = userEvent.setup()
  const nameInput = screen.getByLabelText(/full name/i)
  await act(async () => {
    await user.type(nameInput, name)
  })
  return nameInput
}

export const clearNameField = async () => {
  const user = userEvent.setup()
  const nameInput = screen.getByLabelText(/full name/i)
  await act(async () => {
    await user.clear(nameInput)
  })
  return nameInput
}

export const submitForm = async (buttonText: RegExp | string = /generate cv/i) => {
  const user = userEvent.setup()
  const submitButton = screen.getByRole('button', { name: buttonText })
  await act(async () => {
    await user.click(submitButton)
  })
  return submitButton
}

export const clickLoadProfileButton = async () => {
  const user = userEvent.setup()
  const loadButton = screen.getByRole('button', { name: /load from profile/i })
  await act(async () => {
    await user.click(loadButton)
  })
  return loadButton
}

export const clickSaveToProfileButton = async () => {
  const user = userEvent.setup()
  const saveButton = screen.getByRole('button', { name: /save to profile/i })
  await act(async () => {
    await user.click(saveButton)
  })
  return saveButton
}

export const waitForFormToLoad = async () => {
  await waitFor(() => {
    expect(screen.getByText('Create Your CV')).toBeInTheDocument()
  })
}

export const waitForEditModeToLoad = async () => {
  await waitFor(() => {
    expect(screen.getByText('Edit CV')).toBeInTheDocument()
  })
}
