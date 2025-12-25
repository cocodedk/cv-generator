import axios from 'axios'
import { AIGenerateCVRequest, AIGenerateCVResponse } from '../types/ai'

export async function generateCvDraft(payload: AIGenerateCVRequest): Promise<AIGenerateCVResponse> {
  const response = await axios.post<AIGenerateCVResponse>('/api/ai/generate-cv', payload)
  return response.data
}
