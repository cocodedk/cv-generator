/** TypeScript types for CV data structure */

export interface PersonalInfo {
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  linkedin?: string;
  github?: string;
  website?: string;
  summary?: string;
}

export interface Experience {
  title: string;
  company: string;
  start_date: string;
  end_date?: string;
  description?: string;
  location?: string;
}

export interface Education {
  degree: string;
  institution: string;
  year?: string;
  field?: string;
  gpa?: string;
}

export interface Skill {
  name: string;
  category?: string;
  level?: string;
}

export interface CVData {
  personal_info: PersonalInfo;
  experience: Experience[];
  education: Education[];
  skills: Skill[];
}

export interface CVResponse {
  cv_id: string;
  filename?: string;
  status: string;
}

export interface CVListItem {
  cv_id: string;
  created_at: string;
  updated_at: string;
  person_name?: string;
}

export interface CVListResponse {
  cvs: CVListItem[];
  total: number;
}
