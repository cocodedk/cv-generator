import axios from 'axios'
import {
  AIGenerateCVRequest,
  AIGenerateCVResponse,
  AIRewriteRequest,
  AIRewriteResponse,
} from '../types/ai'

export async function generateCvDraft(payload: AIGenerateCVRequest): Promise<AIGenerateCVResponse> {
  const response = await axios.post<AIGenerateCVResponse>('/api/ai/generate-cv', payload)
  return response.data
}

export async function rewriteText(payload: AIRewriteRequest): Promise<AIRewriteResponse> {
  const response = await axios.post<AIRewriteResponse>('/api/ai/rewrite', payload)
  return response.data
}
