import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from '../App'
import * as useHashRouting from '../app_helpers/useHashRouting'
import * as useTheme from '../app_helpers/useTheme'
import * as useMessage from '../app_helpers/useMessage'

// Mock hooks
vi.mock('../app_helpers/useHashRouting')
vi.mock('../app_helpers/useTheme')
vi.mock('../app_helpers/useMessage')
vi.mock('../components/CVForm', () => ({
  default: ({ cvId }: { cvId?: string | null }) => (
    <div data-testid="cv-form">CVForm {cvId ? `with cvId: ${cvId}` : 'without cvId'}</div>
  ),
}))
vi.mock('../components/CVList', () => ({
  default: () => <div data-testid="cv-list">CVList</div>,
}))
vi.mock('../components/ProfileManager', () => ({
  default: () => <div data-testid="profile-manager">ProfileManager</div>,
}))

const mockedUseHashRouting = useHashRouting as any
const mockedUseTheme = useTheme as any
const mockedUseMessage = useMessage as any

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedUseTheme.useTheme.mockReturnValue({
      isDark: false,
      setIsDark: vi.fn(),
    })
    mockedUseMessage.useMessage.mockReturnValue({
      message: null,
      showMessage: vi.fn(),
    })
  })

  it('renders CVForm when in form mode', () => {
    mockedUseHashRouting.useHashRouting.mockReturnValue({
      viewMode: 'form',
      cvId: null,
    })

    render(<App />)

    expect(screen.getByTestId('cv-form')).toBeInTheDocument()
    expect(screen.getByText('CVForm without cvId')).toBeInTheDocument()
  })

  it('renders CVForm with cvId when in edit mode', () => {
    mockedUseHashRouting.useHashRouting.mockReturnValue({
      viewMode: 'edit',
      cvId: 'test-cv-123',
    })

    render(<App />)

    expect(screen.getByTestId('cv-form')).toBeInTheDocument()
    expect(screen.getByText('CVForm with cvId: test-cv-123')).toBeInTheDocument()
  })

  it('renders CVList when in list mode', () => {
    mockedUseHashRouting.useHashRouting.mockReturnValue({
      viewMode: 'list',
      cvId: null,
    })

    render(<App />)

    expect(screen.getByTestId('cv-list')).toBeInTheDocument()
  })

  it('renders ProfileManager when in profile mode', () => {
    mockedUseHashRouting.useHashRouting.mockReturnValue({
      viewMode: 'profile',
      cvId: null,
    })

    render(<App />)

    expect(screen.getByTestId('profile-manager')).toBeInTheDocument()
  })

  it('passes cvId correctly to CVForm in edit mode', () => {
    const testCvId = 'cv-edit-456'
    mockedUseHashRouting.useHashRouting.mockReturnValue({
      viewMode: 'edit',
      cvId: testCvId,
    })

    render(<App />)

    expect(screen.getByText(`CVForm with cvId: ${testCvId}`)).toBeInTheDocument()
  })

  it('handles null cvId in edit mode', () => {
    mockedUseHashRouting.useHashRouting.mockReturnValue({
      viewMode: 'edit',
      cvId: null,
    })

    render(<App />)

    expect(screen.getByText('CVForm without cvId')).toBeInTheDocument()
  })
})
