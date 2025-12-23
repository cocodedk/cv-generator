import { vi } from 'vitest'
import axios from 'axios'

export const setupAxiosMock = () => {
  vi.mock('axios')
  return axios as any
}

export const setupWindowMocks = () => {
  global.window.open = vi.fn()
}

export const createMockCallbacks = () => ({
  mockOnSuccess: vi.fn(),
  mockOnError: vi.fn(),
  mockSetLoading: vi.fn(),
})
