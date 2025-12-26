import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

// Mock axios completely to prevent real HTTP calls
vi.mock('axios', () => {
  const mockAxios = {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  }
  return {
    default: mockAxios,
  }
})

const mockedAxios = axios as any

// Import service AFTER mocking axios
import { getProfile, saveProfile, deleteProfile } from '../../services/profileService'

describe('profileService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Verify axios is mocked - if not, tests will fail
    if (!vi.isMockFunction(mockedAxios.delete)) {
      throw new Error('axios.delete is not mocked - mock setup failed')
    }
  })

  describe('getProfile', () => {
    it('returns profile data on success', async () => {
      const profileData = {
        personal_info: { name: 'John Doe' },
        experience: [],
        education: [],
        skills: [],
      }
      mockedAxios.get.mockResolvedValue({ data: profileData })

      const result = await getProfile()

      expect(result).toEqual(profileData)
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/profile')
    })

    it('returns null on 404', async () => {
      const error = {
        response: { status: 404 },
      }
      mockedAxios.get.mockRejectedValue(error)

      const result = await getProfile()

      expect(result).toBe(null)
    })

    it('throws error on other failures', async () => {
      const error = {
        response: {
          status: 500,
          data: { detail: 'Server error' },
        },
      }
      mockedAxios.get.mockRejectedValue(error)

      await expect(getProfile()).rejects.toThrow('Server error')
    })
  })

  describe('saveProfile', () => {
    it('saves profile successfully', async () => {
      const profileData = {
        personal_info: { name: 'John Doe' },
        experience: [],
        education: [],
        skills: [],
      }
      const response = { status: 'success' }
      mockedAxios.post.mockResolvedValue({ data: response })

      const result = await saveProfile(profileData)

      expect(result).toEqual(response)
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/profile', profileData)
    })

    it('throws error on failure', async () => {
      const error = {
        response: {
          data: { detail: 'Failed to save profile' },
        },
      }
      mockedAxios.post.mockRejectedValue(error)

      await expect(saveProfile({} as any)).rejects.toThrow('Failed to save profile')
    })
  })

  describe('deleteProfile', () => {
    it('deletes profile successfully', async () => {
      const response = { status: 'success' }
      mockedAxios.delete.mockResolvedValue({ data: response })

      const result = await deleteProfile()

      expect(result).toEqual(response)
      expect(mockedAxios.delete).toHaveBeenCalledWith('/api/profile', {
        headers: { 'X-Confirm-Delete-Profile': 'true' },
      })
    })

    it('throws error on failure', async () => {
      const error = {
        response: {
          data: { detail: 'Delete failed' },
        },
      }
      mockedAxios.delete.mockRejectedValue(error)

      await expect(deleteProfile()).rejects.toThrow('Delete failed')
    })
  })
})
