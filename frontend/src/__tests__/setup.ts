import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

declare global {
  interface GlobalThis {
    IS_REACT_ACT_ENVIRONMENT: boolean
  }
}

;(globalThis as unknown as { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

// Cleanup after each test
afterEach(() => {
  cleanup()
})

export {}
