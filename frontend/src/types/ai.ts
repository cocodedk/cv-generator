import { CVData } from './cv'

export type AIGenerateStyle = 'select_and_reorder' | 'rewrite_bullets' | 'llm_tailor'

export interface AIGenerateCVRequest {
  job_description: string
  target_role?: string
  seniority?: string
  style?: AIGenerateStyle
  max_experiences?: number
}

export interface EvidenceItem {
  path: string
  quote: string
}

export interface EvidenceMapping {
  requirement: string
  evidence: EvidenceItem[]
}

export interface AIGenerateCVResponse {
  draft_cv: CVData
  warnings: string[]
  questions: string[]
  summary: string[]
  evidence_map?: EvidenceMapping[] | null
}

export interface AIRewriteRequest {
  text: string
  prompt: string
}

export interface AIRewriteResponse {
  rewritten_text: string
}
