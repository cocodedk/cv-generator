import { vi } from 'vitest'

// Note: Mock must be hoisted in each test file that uses it
// This file only exports helper functions, not the mocked service

export const createMockCallbacks = () => ({
  mockOnSuccess: vi.fn(),
  mockOnError: vi.fn(),
  mockSetLoading: vi.fn(),
})

export const setupWindowMocks = () => {
  global.window.confirm = vi.fn(() => true)
}

export const createEmptyProfileData = () => ({
  personal_info: {
    name: '',
    email: '',
    phone: '',
    title: '',
    linkedin: '',
    github: '',
    website: '',
    address: {
      street: '',
      city: '',
      state: '',
      zip: '',
      country: '',
    },
    summary: '',
  },
  experience: [],
  education: [],
  skills: [],
})

export const createProfileData = (overrides: any = {}) => ({
  personal_info: {
    name: 'John Doe',
    email: 'john@example.com',
    phone: '',
    title: '',
    linkedin: '',
    github: '',
    website: '',
    address: {
      street: '',
      city: '',
      state: '',
      zip: '',
      country: '',
    },
    summary: '',
    ...overrides.personal_info,
  },
  experience: overrides.experience || [],
  education: overrides.education || [],
  skills: overrides.skills || [],
})
