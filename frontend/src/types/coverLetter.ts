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
