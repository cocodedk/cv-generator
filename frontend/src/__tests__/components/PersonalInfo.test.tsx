import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { useForm } from 'react-hook-form'
import PersonalInfo from '../../components/PersonalInfo'
import { CVData } from '../../types/cv'

// Wrapper component to provide form context
function PersonalInfoWrapper() {
  const {
    register,
    control,
    formState: { errors },
  } = useForm<CVData>({
    defaultValues: {
      personal_info: {
        name: '',
        email: '',
        phone: '',
        address: {
          street: '',
          city: '',
          state: '',
          zip: '',
          country: '',
        },
      },
    },
  })

  return <PersonalInfo register={register} errors={errors} control={control} />
}

describe('PersonalInfo', () => {
  it('renders all form fields', () => {
    render(<PersonalInfoWrapper />)

    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/professional title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/linkedin/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/github/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/website/i)).toBeInTheDocument()
  })

  it('renders address fields', () => {
    render(<PersonalInfoWrapper />)

    expect(screen.getByLabelText(/street address/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/city/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/state/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/zip/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/country/i)).toBeInTheDocument()
  })

  it('renders summary rich text editor', () => {
    render(<PersonalInfoWrapper />)

    expect(screen.getByLabelText(/professional summary/i)).toBeInTheDocument()
    // Check that RichTextarea (ReactQuill) is rendered
    expect(document.querySelector('.ql-editor')).toBeInTheDocument()
  })

  it('displays validation error for required name field', () => {
    function PersonalInfoWithError() {
      const {
        register,
        control,
        formState: { errors },
      } = useForm<CVData>({
        defaultValues: {
          personal_info: { name: '' },
        },
      })

      // Manually set error for testing
      errors.personal_info = {
        name: { type: 'required', message: 'Name is required' },
      } as any

      return <PersonalInfo register={register} errors={errors} control={control} />
    }

    render(<PersonalInfoWithError />)
    expect(screen.getByText(/name is required/i)).toBeInTheDocument()
  })
})
