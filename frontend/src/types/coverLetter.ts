export interface CoverLetterRequest {
  job_description: string
  company_name: string
  hiring_manager_name?: string
  company_address?: string
  tone: 'professional' | 'enthusiastic' | 'conversational'
}

export interface CoverLetterResponse {
  cover_letter_html: string
  cover_letter_text: string
  highlights_used: string[]
  selected_experiences: string[]
  selected_skills: string[]
}

export interface CoverLetterPDFRequest {
  html: string
}

export interface CoverLetterData {
  cover_letter_id: string
  created_at: string
  updated_at: string
  job_description: string
  company_name: string
  hiring_manager_name?: string
  company_address?: string
  tone: string
  cover_letter_html: string
  cover_letter_text: string
  highlights_used: string[]
  selected_experiences: string[]
  selected_skills: string[]
}

export interface CoverLetterListItem {
  cover_letter_id: string
  created_at: string
  updated_at: string
  company_name: string
  hiring_manager_name?: string
  tone: string
}

export interface CoverLetterListResponse {
  cover_letters: CoverLetterListItem[]
  total: number
}

export interface CoverLetterSaveRequest {
  cover_letter_response: CoverLetterResponse
  request_data: CoverLetterRequest
}
