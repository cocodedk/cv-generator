import { CVData } from '../../types/cv'

export const defaultCvData: CVData = {
  personal_info: {
    name: '',
    title: '',
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
  theme: 'classic',
  layout: 'classic-two-column',
}
