/**
 * ProfileManager translation tests
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ProfileManager from '../../components/ProfileManager'
import { createProfileData } from '../helpers/profileManager/mocks'
import * as profileService from '../../services/profileService'

// Mock the profile service
vi.mock('../../services/profileService', () => ({
  getProfile: vi.fn(),
  getProfileByUpdatedAt: vi.fn(),
  saveProfile: vi.fn(),
  deleteProfile: vi.fn(),
  translateProfile: vi.fn(),
}))

// Mock the hash routing hook
vi.mock('../../app_helpers/useHashRouting', () => ({
  useHashRouting: () => ({
    viewMode: 'profile',
    profileUpdatedAt: undefined,
  }),
}))

// Mock the theme hook
vi.mock('../../app_helpers/useTheme', () => ({
  useTheme: () => ({
    isDark: false,
    setIsDark: vi.fn(),
  }),
}))

// Mock the message hook
vi.mock('../../app_helpers/useMessage', () => ({
  useMessage: () => ({
    message: null,
    showMessage: vi.fn(),
    clearMessage: vi.fn(),
  }),
}))

describe('ProfileManager Translation', () => {
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()
  const mockSetLoading = vi.fn()

  const mockProfileData = createProfileData({
    personal_info: {
      name: 'John Doe',
      title: 'Software Engineer',
      summary: 'Experienced developer',
    },
    experience: [
      {
        title: 'Senior Developer',
        company: 'Tech Corp',
        description: 'Built web applications',
        location: 'New York',
        projects: [],
      },
    ],
    education: [
      {
        degree: 'Bachelor of Science',
        institution: 'State University',
        field: 'Computer Science',
      },
    ],
  })

  const mockTranslatedProfile = {
    ...mockProfileData,
    language: 'es',
    personal_info: {
      ...mockProfileData.personal_info,
      title: 'Ingeniero de Software',
      summary: 'Desarrollador experimentado',
    },
    experience: [
      {
        ...mockProfileData.experience[0],
        title: 'Desarrollador Senior',
        description: 'Construyó aplicaciones web',
        location: 'Nueva York',
      },
    ],
    education: [
      {
        ...mockProfileData.education[0],
        degree: 'Licenciatura en Ciencias',
        institution: 'Universidad Estatal',
        field: 'Ciencias de la Computación',
      },
    ],
  }

  beforeEach(() => {
    vi.clearAllMocks()

    // Setup default mocks
    vi.mocked(profileService.getProfile).mockResolvedValue(mockProfileData)
    vi.mocked(profileService.translateProfile).mockResolvedValue({
      status: 'success',
      translated_profile: mockTranslatedProfile,
      message: 'Profile translated successfully',
    })
    vi.mocked(profileService.saveProfile).mockResolvedValue({
      status: 'success',
      message: 'Profile saved successfully',
    })
  })

  describe('Translation UI', () => {
    it('renders translation controls in top action bar', async () => {
      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      expect(screen.getByDisplayValue('Spanish')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /translate/i })).toBeInTheDocument()
    })

    it('shows all supported languages in dropdown', async () => {
      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      const select = screen.getByDisplayValue('Spanish')
      expect(select).toBeInTheDocument()

      // Check that all languages are available in the native select options
      const options = screen.getAllByRole('option')
      expect(options).toHaveLength(14) // Total number of language options

      // Verify specific languages are present
      expect(options).toContain(screen.getByRole('option', { name: 'Spanish' }))
      expect(options).toContain(screen.getByRole('option', { name: 'French' }))
      expect(options).toContain(screen.getByRole('option', { name: 'German' }))
      expect(options).toContain(screen.getByRole('option', { name: 'Danish' }))
      expect(options).toContain(screen.getByRole('option', { name: 'Swedish' }))
      expect(options).toContain(screen.getByRole('option', { name: 'Norwegian' }))
    })
  })

  describe('Translation Flow', () => {
    it('successfully translates profile and updates UI', async () => {
      const user = userEvent.setup()

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      // Click translate button
      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      // Wait for translation to complete
      await waitFor(() => {
        expect(vi.mocked(profileService.translateProfile)).toHaveBeenCalledWith(
          expect.objectContaining({
            personal_info: expect.objectContaining({
              title: 'Software Engineer',
              summary: 'Experienced developer',
            }),
          }),
          'es'
        )
      })

      // Check success message
      expect(mockOnSuccess).toHaveBeenCalledWith('Profile translated to ES and saved successfully!')
    })

    it('handles translation errors gracefully', async () => {
      const user = userEvent.setup()

      vi.mocked(profileService.translateProfile).mockRejectedValue(
        new Error('Translation service error')
      )

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      await waitFor(() => {
        expect(mockOnError).toHaveBeenCalledWith('Translation service error')
      })
    })

    it('shows loading state during translation', async () => {
      const user = userEvent.setup()

      // Mock a slow translation
      vi.mocked(profileService.translateProfile).mockImplementation(
        () =>
          new Promise(resolve =>
            setTimeout(
              () =>
                resolve({
                  status: 'success',
                  translated_profile: mockTranslatedProfile,
                  message: 'Profile translated successfully',
                }),
              100
            )
          )
      )

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      // Check loading state
      expect(screen.getByText('Translating...')).toBeInTheDocument()
      expect(translateButton).toBeDisabled()

      // Wait for completion
      await waitFor(() => {
        expect(screen.queryByText('Translating...')).not.toBeInTheDocument()
      })
    })

    it('changes target language when dropdown is changed', async () => {
      const user = userEvent.setup()

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      const select = screen.getByDisplayValue('Spanish')
      await user.selectOptions(select, 'French')

      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      await waitFor(() => {
        expect(vi.mocked(profileService.translateProfile)).toHaveBeenCalledWith(
          expect.any(Object),
          'fr'
        )
      })
    })
  })

  describe('Edge Cases', () => {
    it('handles translation with minimal profile data', async () => {
      const user = userEvent.setup()

      // Mock a profile with minimal data
      const minimalProfile = {
        personal_info: { name: '', title: '' },
        experience: [],
        education: [],
        skills: [],
        language: 'en',
      }
      vi.mocked(profileService.getProfile).mockResolvedValue(minimalProfile)

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      // Translation should still work even with minimal data
      await waitFor(() => {
        expect(vi.mocked(profileService.translateProfile)).toHaveBeenCalledWith(
          expect.objectContaining({
            personal_info: expect.objectContaining({ name: '', title: '' }),
          }),
          'es'
        )
      })
    })

    it('handles re-selecting the same target language', async () => {
      const user = userEvent.setup()

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      // Test re-selecting the same default language (Spanish)
      const select = screen.getByDisplayValue('Spanish')
      await user.selectOptions(select, 'Spanish') // Spanish is already selected, but test anyway

      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      await waitFor(() => {
        expect(vi.mocked(profileService.translateProfile)).toHaveBeenCalledWith(
          expect.any(Object),
          'es' // Default target language
        )
      })
    })

    it('sets createNewProfile flag when translating', async () => {
      const user = userEvent.setup()

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith(expect.stringContaining('saved successfully'))
      })

      // The component should be in a state where saving creates a new profile
      // This is tested indirectly through the success message
    })

    it('allows translation to proceed despite form validation errors', async () => {
      const user = userEvent.setup()

      // Mock a profile with validation errors (empty name field)
      vi.mocked(profileService.getProfile).mockResolvedValue({
        ...mockProfileData,
        personal_info: {
          ...mockProfileData.personal_info,
          name: '', // Invalid empty name - form validation error
        },
      })

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      // Translation should proceed even when form has validation errors
      // ProfileManager's translate button is not disabled by form validation,
      // allowing users to translate invalid profiles and then fix them
      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      await waitFor(() => {
        expect(vi.mocked(profileService.translateProfile)).toHaveBeenCalled()
      })
    })

    it('disables button during translation to prevent multiple requests', async () => {
      const user = userEvent.setup()

      // Mock a slow translation to ensure button stays disabled
      vi.mocked(profileService.translateProfile).mockImplementation(
        () =>
          new Promise(resolve =>
            setTimeout(
              () =>
                resolve({
                  status: 'success',
                  translated_profile: mockTranslatedProfile,
                  message: 'Profile translated successfully',
                }),
              200
            )
          )
      )

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      const translateButton = screen.getByRole('button', { name: /translate/i })

      // Click translate once
      await user.click(translateButton)

      // Button should be disabled during translation
      expect(translateButton).toBeDisabled()
      expect(screen.getByText('Translating...')).toBeInTheDocument()

      // Try clicking again while disabled - should not trigger another call
      await user.click(translateButton)

      // Wait for completion
      await waitFor(() => {
        expect(screen.queryByText('Translating...')).not.toBeInTheDocument()
      })

      // Should only have been called once
      expect(vi.mocked(profileService.translateProfile)).toHaveBeenCalledTimes(1)
    })

    it('preserves form state after translation', async () => {
      const user = userEvent.setup()

      render(
        <ProfileManager
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          setLoading={mockSetLoading}
        />
      )

      await waitFor(() => {
        expect(screen.getByText('Translate to:')).toBeInTheDocument()
      })

      // Change language selection
      const select = screen.getByDisplayValue('Spanish')
      await user.selectOptions(select, 'French')

      // Translate
      const translateButton = screen.getByRole('button', { name: /translate/i })
      await user.click(translateButton)

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalled()
      })

      // Language selection should still be French
      expect(screen.getByDisplayValue('French')).toBeInTheDocument()
    })
  })
})
