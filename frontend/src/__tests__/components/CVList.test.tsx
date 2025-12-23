import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, render, screen, waitFor } from '@testing-library/react'
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
          filename: 'cv_1234.docx',
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
    await act(async () => {
      await user.click(editButton)
    })

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
          filename: 'cv_1234.docx',
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

  it('shows empty state when no CVs returned', async () => {
    mockedAxios.get.mockResolvedValue({ data: { cvs: [], total: 0 } })

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText(/no cvs found/i)).toBeInTheDocument()
    })
  })

  it('handles search on Enter key', async () => {
    const user = userEvent.setup()
    mockedAxios.get
      .mockResolvedValueOnce({ data: { cvs: [], total: 0 } })
      .mockResolvedValueOnce({ data: { cvs: [], total: 0 } })

    render(<CVList onError={mockOnError} />)

    const searchInput = screen.getByPlaceholderText(/search cvs/i)
    await act(async () => {
      await user.type(searchInput, 'john{enter}')
    })

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenLastCalledWith('/api/cvs', {
        params: { limit: 50, offset: 0, search: 'john' },
      })
    })
  })

  it('handles search button click', async () => {
    const user = userEvent.setup()
    mockedAxios.get
      .mockResolvedValueOnce({ data: { cvs: [], total: 0 } })
      .mockResolvedValueOnce({ data: { cvs: [], total: 0 } })

    render(<CVList onError={mockOnError} />)

    const searchInput = screen.getByPlaceholderText(/search cvs/i)
    await act(async () => {
      await user.type(searchInput, 'doe')
    })

    const searchButton = screen.getByRole('button', { name: /search/i })
    await act(async () => {
      await user.click(searchButton)
    })

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenLastCalledWith('/api/cvs', {
        params: { limit: 50, offset: 0, search: 'doe' },
      })
    })
  })

  it('downloads CV when filename is present', async () => {
    const user = userEvent.setup()
    const openMock = vi.fn()
    const mockCvs = {
      cvs: [
        {
          cv_id: 'cv-1',
          person_name: 'John Doe',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          filename: 'cv_1234.docx',
        },
      ],
      total: 1,
    }
    mockedAxios.get.mockResolvedValue({ data: mockCvs })
    window.open = openMock

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const downloadButton = screen.getByRole('button', { name: /download/i })
    await act(async () => {
      await user.click(downloadButton)
    })

    expect(openMock).toHaveBeenCalledWith(
      expect.stringMatching(/^\/api\/download-docx\/cv_1234\.docx\?t=\d+$/),
      '_blank'
    )
  })

  it('does not delete when confirmation is rejected', async () => {
    const user = userEvent.setup()
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
    window.confirm = vi.fn(() => false)

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const deleteButton = screen.getByRole('button', { name: /delete/i })
    await act(async () => {
      await user.click(deleteButton)
    })

    expect(mockedAxios.delete).not.toHaveBeenCalled()
  })

  it('handles delete error', async () => {
    const user = userEvent.setup()
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
    mockedAxios.delete.mockRejectedValue({
      response: { data: { detail: 'Delete failed' } },
    })
    window.confirm = vi.fn(() => true)

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const deleteButton = screen.getByRole('button', { name: /delete/i })
    await act(async () => {
      await user.click(deleteButton)
    })

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Delete failed')
    })
  })

  it('handles initial load error', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { data: { detail: 'Fetch failed' } },
    })

    render(<CVList onError={mockOnError} />)

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Fetch failed')
    })
  })
})
