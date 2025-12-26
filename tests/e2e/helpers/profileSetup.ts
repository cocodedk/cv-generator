/**
 * Profile setup helpers for E2E tests
 */

import { APIRequestContext } from '@playwright/test'
import { BACKEND_URL } from './constants'

/**
 * Sample profile data for testing
 */
export function getTestProfileData() {
  return {
    personal_info: {
      name: 'Test User',
      email: 'test@example.com',
      phone: '+1234567890',
      address: {
        street: '123 Test St',
        city: 'Test City',
        state: 'TS',
        zip: '12345',
        country: 'USA',
      },
      linkedin: 'https://linkedin.com/in/testuser',
      github: 'https://github.com/testuser',
      summary: 'Experienced software developer with expertise in React and FastAPI',
    },
    experience: [
      {
        title: 'Senior Full Stack Developer',
        company: 'Tech Corp',
        start_date: '2020-01',
        end_date: '2023-12',
        description: 'Led development of scalable web applications',
        location: 'Remote',
        projects: [
          {
            name: 'Internal Platform',
            description: 'Unified services into a single developer platform',
            technologies: ['React', 'FastAPI', 'Docker', 'Neo4j'],
            highlights: [
              'Reduced onboarding time by 50% with standardized templates',
              'Improved system reliability by 30% with automated health checks',
              'Deployed microservices architecture handling 1M+ requests/day',
            ],
            url: 'https://example.com/platform',
          },
        ],
      },
    ],
    education: [
      {
        degree: 'BS Computer Science',
        institution: 'University of Technology',
        year: '2018',
        field: 'Computer Science',
        gpa: '3.8',
      },
    ],
    skills: [
      { name: 'React', category: 'Frontend', level: 'Expert' },
      { name: 'FastAPI', category: 'Backend', level: 'Advanced' },
      { name: 'Docker', category: 'DevOps', level: 'Advanced' },
      { name: 'Python', category: 'Programming', level: 'Expert' },
      { name: 'TypeScript', category: 'Programming', level: 'Advanced' },
    ],
  }
}

/**
 * Verify profile exists via API
 * @param request - Playwright API request context
 */
export async function verifyProfileExists(request: APIRequestContext): Promise<boolean> {
  try {
    const response = await request.get(`${BACKEND_URL}/api/profile`)
    return response.status() === 200
  } catch {
    return false
  }
}

/**
 * Create a test profile via API
 * @param request - Playwright API request context
 * @returns The created profile's updated_at timestamp
 */
export async function createTestProfile(
  request: APIRequestContext
): Promise<string | null> {
  const profileData = getTestProfileData()
  try {
    const response = await request.post(`${BACKEND_URL}/api/profile`, {
      data: profileData,
    })
    if (response.status() !== 200) {
      const body = await response.text().catch(() => '')
      throw new Error(`Failed to create profile: ${response.status()} - ${body}`)
    }
    // Verify profile was created and is accessible, then get its updated_at
    let retries = 5
    while (retries > 0) {
      const profileResponse = await request.get(`${BACKEND_URL}/api/profile`)
      if (profileResponse.status() === 200) {
        const profile = await profileResponse.json()
        return profile.updated_at || null
      }
      await new Promise(resolve => setTimeout(resolve, 200))
      retries--
    }
    throw new Error('Profile created but not accessible after creation')
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error(`Failed to create test profile: ${String(error)}`)
  }
}
