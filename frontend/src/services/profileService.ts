/** Profile API service for managing profile operations. */
import axios from 'axios'
import { ProfileData, ProfileResponse } from '../types/cv'
import { normalizeProfileDataForApi } from '../app_helpers/cvForm/normalizeCvData'

/**
 * Get the master profile from the server.
 * @returns Profile data or null if not found
 * @throws Error if request fails
 */
export async function getProfile(): Promise<ProfileData | null> {
  try {
    const response = await axios.get<ProfileData>('/api/profile')
    return response.data || null
  } catch (error: any) {
    if (error.response?.status === 404) {
      return null
    }
    throw new Error(error.response?.data?.detail || 'Failed to load profile')
  }
}

/**
 * Save or update the master profile.
 * @param profileData - Profile data to save
 * @returns Success response
 * @throws Error if save fails
 */
export async function saveProfile(profileData: ProfileData): Promise<ProfileResponse> {
  try {
    const payload = normalizeProfileDataForApi(profileData)
    const response = await axios.post<ProfileResponse>('/api/profile', payload)
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to save profile')
  }
}

/**
 * Delete the master profile.
 * @returns Success response
 * @throws Error if delete fails
 */
export async function deleteProfile(): Promise<ProfileResponse> {
  try {
    const response = await axios.delete<ProfileResponse>('/api/profile')
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to delete profile')
  }
}
