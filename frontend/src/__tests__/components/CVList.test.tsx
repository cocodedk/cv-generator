import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import axios from 'axios'
import CVList from '../../components/CVList'

// Mock axios
vi.mock('axios')
const mockedAxios = axios as any

// Mock window.location.hash
const mockHashChange = vi.fn()
Object.defineProperty(window, 'location', {
  value: {
    hash: '',
  },
  writable: true,
})

describe('CVList', () => {
  const mockOnError = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock window.location.hash setter
    let hashValue = ''
    Object.defineProperty(window, 'location', {
      value: {
        get hash() {
          return hashValue
        },
        set hash(value) {
          hashValue = value
          mockHashChange(value)
        },
      },
      writable: true,
    })
  })

  it('renders CV list with Edit buttons', async () => {
    const mockCvs = {
      cvs: [
        {
          cv_id: 'cv-1',
          person_name: 'John Doe',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          filename: 'cv_1234.odt',
        },
        {
          cv_id: 'cv-2',
          person_name: 'Jane Smith',
          created_at: '2024-01-02T00:00:00Z',
          updated_at: '2024-01-02T00:00:00Z',
        },
      ],
      total: 2,
    }
    mockedAxios.get.mockResolvedValue({ data: mockCvs })

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const editButtons = screen.getAllByRole('button', { name: /edit/i })
    expect(editButtons).toHaveLength(2)
  })

  it('navigates to edit mode when Edit button is clicked', async () => {
    const user = userEvent.setup()
    const mockCvs = {
      cvs: [
        {
          cv_id: 'cv-123',
          person_name: 'John Doe',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
    }
    mockedAxios.get.mockResolvedValue({ data: mockCvs })

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const editButton = screen.getByRole('button', { name: /edit/i })
    await user.click(editButton)

    await waitFor(() => {
      expect(window.location.hash).toBe('#edit/cv-123')
    })
  })

  it('shows Edit button alongside Download and Delete buttons', async () => {
    const mockCvs = {
      cvs: [
        {
          cv_id: 'cv-1',
          person_name: 'John Doe',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          filename: 'cv_1234.odt',
        },
      ],
      total: 1,
    }
    mockedAxios.get.mockResolvedValue({ data: mockCvs })

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /download/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
  })

  it('shows Edit button even when CV has no filename', async () => {
    const mockCvs = {
      cvs: [
        {
          cv_id: 'cv-1',
          person_name: 'John Doe',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
    }
    mockedAxios.get.mockResolvedValue({ data: mockCvs })

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /download/i })).not.toBeInTheDocument()
  })
})
