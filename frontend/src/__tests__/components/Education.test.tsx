import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useForm } from 'react-hook-form'
import Education from '../../components/Education'
import { CVData } from '../../types/cv'

// Wrapper component to provide form context
function EducationWrapper() {
  const { control, register } = useForm<CVData>({
    defaultValues: {
      personal_info: { name: 'Test' },
      education: [],
    },
  })

  return <Education control={control} register={register} />
}

describe('Education', () => {
  it('renders education section', () => {
    render(<EducationWrapper />)

    expect(screen.getByRole('heading', { name: /education/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add education/i })).toBeInTheDocument()
  })

  it('displays message when no education added', () => {
    render(<EducationWrapper />)

    expect(screen.getByText(/no education added/i)).toBeInTheDocument()
  })

  it('adds new education entry', async () => {
    const user = userEvent.setup()
    render(<EducationWrapper />)

    const addButton = screen.getByRole('button', { name: /add education/i })
    await user.click(addButton)

    expect(screen.getByText(/education 1/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/degree/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/institution/i)).toBeInTheDocument()
  })

  it('removes education entry', async () => {
    const user = userEvent.setup()

    function EducationWithData() {
      const { control, register } = useForm<CVData>({
        defaultValues: {
          personal_info: { name: 'Test' },
          education: [
            {
              degree: 'BS Computer Science',
              institution: 'University',
              year: '',
              field: '',
              gpa: '',
            },
          ],
        },
      })

      return <Education control={control} register={register} />
    }

    render(<EducationWithData />)

    const removeButton = screen.getByRole('button', { name: /remove/i })
    await user.click(removeButton)

    expect(screen.getByText(/no education added/i)).toBeInTheDocument()
  })

  it('renders all education fields', async () => {
    const user = userEvent.setup()
    render(<EducationWrapper />)

    const addButton = screen.getByRole('button', { name: /add education/i })
    await user.click(addButton)

    expect(screen.getByLabelText(/degree/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/institution/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/year/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/field of study/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/gpa/i)).toBeInTheDocument()
  })
})
