import { describe, it, expect, vi } from 'vitest'
import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useForm } from 'react-hook-form'
import Experience from '../../components/Experience'
import { CVData } from '../../types/cv'

// Wrapper component to provide form context
function ExperienceWrapper() {
  const {
    control,
    register,
    formState: { errors },
  } = useForm<CVData>({
    defaultValues: {
      personal_info: { name: 'Test' },
      experience: [],
    },
  })

  return <Experience control={control} register={register} errors={errors} />
}

describe('Experience', () => {
  it('renders experience section', () => {
    render(<ExperienceWrapper />)

    expect(screen.getByRole('heading', { name: /work experience/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add experience/i })).toBeInTheDocument()
  })

  it('displays message when no experience added', () => {
    render(<ExperienceWrapper />)

    expect(screen.getByText(/no experience added/i)).toBeInTheDocument()
  })

  it('adds new experience entry', async () => {
    const user = userEvent.setup()
    render(<ExperienceWrapper />)

    const addButton = screen.getByRole('button', { name: /add experience/i })
    await act(async () => {
      await user.click(addButton)
    })

    await waitFor(() => {
      expect(screen.getByText(/experience 1/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/job title/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/company/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/start date/i)).toBeInTheDocument()
      // RichTextarea for role summary is present (check by label or by quill editor)
      expect(screen.getByLabelText(/role summary/i)).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: /projects/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /add project/i })).toBeInTheDocument()
    })
  })

  it('adds a project under an experience', async () => {
    const user = userEvent.setup()
    render(<ExperienceWrapper />)

    await act(async () => {
      await user.click(screen.getByRole('button', { name: /add experience/i }))
    })

    await act(async () => {
      await user.click(screen.getByRole('button', { name: /add project/i }))
    })

    await waitFor(() => {
      expect(screen.getByText(/project 1/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/project name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/technologies/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/highlights/i)).toBeInTheDocument()
    })
  })

  it('removes experience entry', async () => {
    const user = userEvent.setup()

    function ExperienceWithData() {
      const {
        control,
        register,
        formState: { errors },
      } = useForm<CVData>({
        defaultValues: {
          personal_info: { name: 'Test' },
          experience: [
            {
              title: 'Developer',
              company: 'Tech Corp',
              start_date: '2020-01',
              end_date: '',
              description: '',
              location: '',
              projects: [],
            },
          ],
        },
      })

      return <Experience control={control} register={register} errors={errors} />
    }

    render(<ExperienceWithData />)

    const removeButton = screen.getByRole('button', { name: /remove/i })
    await act(async () => {
      await user.click(removeButton)
    })

    await waitFor(() => {
      expect(screen.getByText(/no experience added/i)).toBeInTheDocument()
    })
  })

  it('renders multiple experience entries', async () => {
    const user = userEvent.setup()
    render(<ExperienceWrapper />)

    const addButton = screen.getByRole('button', { name: /add experience/i })
    await act(async () => {
      await user.click(addButton)
      await user.click(addButton)
    })

    await waitFor(() => {
      expect(screen.getByText(/experience 1/i)).toBeInTheDocument()
      expect(screen.getByText(/experience 2/i)).toBeInTheDocument()
    })
  })
})
