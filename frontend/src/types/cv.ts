/** TypeScript types for CV data structure */

export interface Address {
  street?: string
  city?: string
  state?: string
  zip?: string
  country?: string
}

export interface PersonalInfo {
  name: string
  title?: string
  email?: string
  phone?: string
  address?: Address
  linkedin?: string
  github?: string
  website?: string
  summary?: string
  photo?: string
}

export interface Project {
  name: string
  description?: string
  highlights?: string[]
  technologies?: string[]
  url?: string
}

export interface Experience {
  title: string
  company: string
  start_date: string
  end_date?: string
  description?: string
  location?: string
  projects?: Project[]
}

export interface Education {
  degree: string
  institution: string
  year?: string
  field?: string
  gpa?: string
}

export interface Skill {
  name: string
  category?: string
  level?: string
}

export interface CVData {
  personal_info: PersonalInfo
  experience: Experience[]
  education: Education[]
  skills: Skill[]
  theme?:
    | 'accented'
    | 'classic'
    | 'colorful'
    | 'creative'
    | 'elegant'
    | 'executive'
    | 'minimal'
    | 'modern'
    | 'professional'
    | 'tech'
}

export interface CVResponse {
  cv_id: string
  filename?: string
  status: string
}

export interface CVListItem {
  cv_id: string
  created_at: string
  updated_at: string
  person_name?: string
  filename?: string
}

export interface CVListResponse {
  cvs: CVListItem[]
  total: number
}

export interface ProfileData {
  personal_info: PersonalInfo
  experience: Experience[]
  education: Education[]
  skills: Skill[]
  updated_at?: string
}

export interface ProfileResponse {
  status: string
  message?: string
}

export interface ProfileListItem {
  name: string
  updated_at: string
}

export interface ProfileListResponse {
  profiles: ProfileListItem[]
}
