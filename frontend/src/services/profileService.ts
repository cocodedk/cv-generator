/** Profile API service for managing profile operations. */
import axios from 'axios'
import { ProfileData, ProfileResponse, ProfileListResponse } from '../types/cv'

interface TranslateProfileRequest {
  profile_data: ProfileData
  target_language: string
}

interface TranslateProfileResponse {
  status: string
  translated_profile: ProfileData
  message?: string
  saved_profile_updated_at?: string
}
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
export async function saveProfile(
  profileData: ProfileData,
  createNew: boolean = false
): Promise<ProfileResponse> {
  try {
    const payload = normalizeProfileDataForApi(profileData)
    const response = await axios.post<ProfileResponse>('/api/profile', payload, {
      params: createNew ? { create_new: true } : undefined,
    })
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
    const response = await axios.delete<ProfileResponse>('/api/profile', {
      headers: { 'X-Confirm-Delete-Profile': 'true' },
    })
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to delete profile')
  }
}

/**
 * List all profiles with basic info.
 * @returns List of profiles with name and updated_at
 * @throws Error if request fails
 */
export async function listProfiles(): Promise<ProfileListResponse> {
  try {
    const response = await axios.get<ProfileListResponse>('/api/profiles')
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to list profiles')
  }
}

/**
 * Get a specific profile by its updated_at timestamp.
 * @param updatedAt - ISO timestamp string identifying the profile
 * @returns Profile data or null if not found
 * @throws Error if request fails
 */
export async function getProfileByUpdatedAt(updatedAt: string): Promise<ProfileData | null> {
  try {
    const response = await axios.get<ProfileData>(`/api/profile/${encodeURIComponent(updatedAt)}`)
    return response.data || null
  } catch (error: any) {
    if (error.response?.status === 404) {
      return null
    }
    throw new Error(error.response?.data?.detail || 'Failed to load profile')
  }
}

/**
 * Delete a specific profile by its updated_at timestamp.
 * @param updatedAt - ISO timestamp string identifying the profile
 * @returns Success response
 * @throws Error if delete fails
 */
export async function deleteProfileByUpdatedAt(updatedAt: string): Promise<ProfileResponse> {
  try {
    const response = await axios.delete<ProfileResponse>(
      `/api/profile/${encodeURIComponent(updatedAt)}`,
      { headers: { 'X-Confirm-Delete-Profile': 'true' } }
    )
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to delete profile')
  }
}

/**
 * Translate a profile to another language using AI.
 * @param profileData - Profile data to translate
 * @param targetLanguage - ISO 639-1 language code for target language
 * @returns Translated profile data
 * @throws Error if translation fails
 */
export async function translateProfile(
  profileData: ProfileData,
  targetLanguage: string
): Promise<TranslateProfileResponse> {
  try {
    const payload: TranslateProfileRequest = {
      profile_data: profileData,
      target_language: targetLanguage,
    }
    const response = await axios.post<TranslateProfileResponse>('/api/profile/translate', payload)
    return response.data
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Failed to translate profile')
  }
}
