import { useState } from 'react'

export type MessageType = 'success' | 'error'

export interface Message {
  type: MessageType
  text: string
}

export const useMessage = () => {
  const [message, setMessage] = useState<Message | null>(null)

  const showMessage = (type: MessageType, text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 5000)
  }

  return { message, showMessage }
}
