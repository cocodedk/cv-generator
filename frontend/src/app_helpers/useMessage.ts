import { useState } from 'react'

export type MessageType = 'success' | 'error'

export interface Message {
  type: MessageType
  text: string | string[]
}

export const useMessage = () => {
  const [message, setMessage] = useState<Message | null>(null)

  const showMessage = (type: MessageType, text: string | string[]) => {
    setMessage({ type, text })
    // Don't auto-hide - user must close manually
  }

  const clearMessage = () => {
    setMessage(null)
  }

  return { message, showMessage, clearMessage }
}
