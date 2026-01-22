/** Default values for profile form. */
import { ProfileData } from '../types/cv'

export const defaultProfileData: ProfileData = {
  personal_info: {
    name: '',
    email: '',
    phone: '',
    address: {
      street: '',
      city: '',
      state: '',
      zip: '',
      country: '',
    },
    linkedin: '',
    github: '',
    website: '',
    summary: '',
  },
  experience: [],
  education: [],
  skills: [],
  language: 'en',
}
