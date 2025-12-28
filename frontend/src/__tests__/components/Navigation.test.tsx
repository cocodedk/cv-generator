import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Navigation from '../../components/Navigation'

describe('Navigation', () => {
  beforeEach(() => {
    window.location.hash = ''
  })

  it('renders all navigation buttons', () => {
    render(<Navigation viewMode="form" isDark={false} onThemeToggle={() => {}} />)

    expect(screen.getByText('Introduction')).toBeInTheDocument()
    expect(screen.getByText('Create CV')).toBeInTheDocument()
    expect(screen.getByText('My CVs')).toBeInTheDocument()
    expect(screen.getByText('Profile')).toBeInTheDocument()
  })

  it('highlights active introduction button', () => {
    render(<Navigation viewMode="introduction" isDark={false} onThemeToggle={() => {}} />)

    const introductionButton = screen.getByText('Introduction')
    expect(introductionButton).toHaveClass('bg-blue-600')
  })

  it('highlights active form button', () => {
    render(<Navigation viewMode="form" isDark={false} onThemeToggle={() => {}} />)

    const createButton = screen.getByText('Create CV')
    expect(createButton).toHaveClass('bg-blue-600')
  })

  it('highlights active list button', () => {
    render(<Navigation viewMode="list" isDark={false} onThemeToggle={() => {}} />)

    const listButton = screen.getByText('My CVs')
    expect(listButton).toHaveClass('bg-blue-600')
  })

  it('highlights active profile button', () => {
    render(<Navigation viewMode="profile" isDark={false} onThemeToggle={() => {}} />)

    const profileButton = screen.getByText('Profile')
    expect(profileButton).toHaveClass('bg-blue-600')
  })

  it('shows Edit CV label in edit mode', () => {
    render(<Navigation viewMode="edit" isDark={false} onThemeToggle={() => {}} />)

    expect(screen.getByText('Edit CV')).toBeInTheDocument()
  })

  it('calls onThemeToggle when theme button clicked', async () => {
    const user = userEvent.setup()
    const onThemeToggle = vi.fn()
    render(<Navigation viewMode="form" isDark={false} onThemeToggle={onThemeToggle} />)

    const themeButton = screen.getByText('Dark mode')
    await act(async () => {
      await user.click(themeButton)
    })

    expect(onThemeToggle).toHaveBeenCalledOnce()
  })

  it('displays Light mode when dark', () => {
    render(<Navigation viewMode="form" isDark={true} onThemeToggle={() => {}} />)

    expect(screen.getByText('Light mode')).toBeInTheDocument()
  })

  it('navigates to form when Create CV clicked', async () => {
    const user = userEvent.setup()
    render(<Navigation viewMode="list" isDark={false} onThemeToggle={() => {}} />)

    const createButton = screen.getByText('Create CV')
    await act(async () => {
      await user.click(createButton)
    })

    expect(window.location.hash).toBe('#form')
  })

  it('navigates to list when My CVs clicked', async () => {
    const user = userEvent.setup()
    render(<Navigation viewMode="form" isDark={false} onThemeToggle={() => {}} />)

    const listButton = screen.getByText('My CVs')
    await act(async () => {
      await user.click(listButton)
    })

    expect(window.location.hash).toBe('#list')
  })

  it('navigates to profile when Profile clicked', async () => {
    const user = userEvent.setup()
    render(<Navigation viewMode="form" isDark={false} onThemeToggle={() => {}} />)

    const profileButton = screen.getByText('Profile')
    await act(async () => {
      await user.click(profileButton)
    })

    expect(window.location.hash).toBe('#profile')
  })

  it('navigates to introduction when Introduction clicked', async () => {
    const user = userEvent.setup()
    render(<Navigation viewMode="form" isDark={false} onThemeToggle={() => {}} />)

    const introductionButton = screen.getByText('Introduction')
    await act(async () => {
      await user.click(introductionButton)
    })

    expect(window.location.hash).toBe('#introduction')
  })
})
