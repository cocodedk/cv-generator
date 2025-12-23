import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useForm } from 'react-hook-form'
import Experience from '../../components/Experience'
import { CVData } from '../../types/cv'

// Wrapper component to provide form context
function ExperienceWrapper() {
  const { control, register } = useForm<CVData>({
    defaultValues: {
      personal_info: { name: 'Test' },
      experience: [],
    },
  })

  return <Experience control={control} register={register} />
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
    await user.click(addButton)

    expect(screen.getByText(/experience 1/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/job title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/company/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument()
  })

  it('removes experience entry', async () => {
    const user = userEvent.setup()

    function ExperienceWithData() {
      const { control, register } = useForm<CVData>({
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
            },
          ],
        },
      })

      return <Experience control={control} register={register} />
    }

    render(<ExperienceWithData />)

    const removeButton = screen.getByRole('button', { name: /remove/i })
    await user.click(removeButton)

    expect(screen.getByText(/no experience added/i)).toBeInTheDocument()
  })

  it('renders multiple experience entries', async () => {
    const user = userEvent.setup()
    render(<ExperienceWrapper />)

    const addButton = screen.getByRole('button', { name: /add experience/i })
    await user.click(addButton)
    await user.click(addButton)

    expect(screen.getByText(/experience 1/i)).toBeInTheDocument()
    expect(screen.getByText(/experience 2/i)).toBeInTheDocument()
  })
})
