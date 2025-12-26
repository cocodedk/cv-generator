import { describe, it, expect } from 'vitest'
import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useForm } from 'react-hook-form'
import Skills from '../../components/Skills'
import { CVData } from '../../types/cv'

// Wrapper component to provide form context
function SkillsWrapper() {
  const { control, register } = useForm<CVData>({
    defaultValues: {
      personal_info: { name: 'Test' },
      skills: [],
    },
  })

  return <Skills control={control} register={register} />
}

describe('Skills', () => {
  it('renders skills section', () => {
    render(<SkillsWrapper />)

    expect(screen.getByRole('heading', { name: /skills/i })).toBeInTheDocument()
    const addButtons = screen.getAllByRole('button', { name: /add skill/i })
    expect(addButtons).toHaveLength(2)
  })

  it('displays message when no skills added', () => {
    render(<SkillsWrapper />)

    expect(screen.getByText(/no skills added/i)).toBeInTheDocument()
  })

  it('adds new skill entry', async () => {
    const user = userEvent.setup()
    render(<SkillsWrapper />)

    const addButtons = screen.getAllByRole('button', { name: /add skill/i })
    await act(async () => {
      await user.click(addButtons[0])
    })

    await waitFor(() => {
      expect(screen.getByText(/skill 1/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/skill name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/level/i)).toBeInTheDocument()
    })
  })

  it('removes skill entry', async () => {
    const user = userEvent.setup()

    function SkillsWithData() {
      const { control, register } = useForm<CVData>({
        defaultValues: {
          personal_info: { name: 'Test' },
          skills: [
            {
              name: 'Python',
              category: 'Programming',
              level: 'Expert',
            },
          ],
        },
      })

      return <Skills control={control} register={register} />
    }

    render(<SkillsWithData />)

    const removeButton = screen.getByRole('button', { name: /remove/i })
    await act(async () => {
      await user.click(removeButton)
    })

    await waitFor(() => {
      expect(screen.getByText(/no skills added/i)).toBeInTheDocument()
    })
  })

  it('renders multiple skill entries', async () => {
    const user = userEvent.setup()
    render(<SkillsWrapper />)

    const addButtons = screen.getAllByRole('button', { name: /add skill/i })
    await act(async () => {
      await user.click(addButtons[0])
      await user.click(addButtons[0])
    })

    await waitFor(() => {
      expect(screen.getByText(/skill 1/i)).toBeInTheDocument()
      expect(screen.getByText(/skill 2/i)).toBeInTheDocument()
    })
  })
})
