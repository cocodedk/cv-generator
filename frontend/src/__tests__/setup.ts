import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

globalThis.IS_REACT_ACT_ENVIRONMENT = true

// Cleanup after each test
afterEach(() => {
  cleanup()
})
