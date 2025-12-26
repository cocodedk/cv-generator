import http from 'node:http'
import https from 'node:https'
import { vi } from 'vitest'

const formatUnknown = (value: unknown) => {
  if (value instanceof URL) return value.toString()
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'bigint' || typeof value === 'boolean')
    return String(value)
  if (
    typeof value === 'object' &&
    value &&
    'url' in value &&
    typeof (value as { url?: unknown }).url === 'string'
  ) {
    return (value as { url: string }).url
  }
  try {
    return JSON.stringify(value)
  } catch {
    return String(value)
  }
}

const unexpectedNetworkCallError = (kind: string, target?: string) => {
  const details = target ? `: ${target}` : ''
  return new Error(`[vitest] Unexpected network call via ${kind}${details}. Mock it in the test.`)
}

export const installNoNetworkGuards = () => {
  vi.stubGlobal('fetch', (async (input: RequestInfo | URL) => {
    throw unexpectedNetworkCallError('fetch', formatUnknown(input))
  }) as unknown as typeof fetch)

  class BlockedXMLHttpRequest {
    constructor() {
      throw unexpectedNetworkCallError('XMLHttpRequest')
    }
  }

  vi.stubGlobal('XMLHttpRequest', BlockedXMLHttpRequest as unknown as typeof XMLHttpRequest)

  vi.spyOn(http, 'request').mockImplementation(((...args: unknown[]) => {
    throw unexpectedNetworkCallError('http.request', formatUnknown(args[0]))
  }) as unknown as typeof http.request)

  vi.spyOn(http, 'get').mockImplementation(((...args: unknown[]) => {
    throw unexpectedNetworkCallError('http.get', formatUnknown(args[0]))
  }) as unknown as typeof http.get)

  vi.spyOn(https, 'request').mockImplementation(((...args: unknown[]) => {
    throw unexpectedNetworkCallError('https.request', formatUnknown(args[0]))
  }) as unknown as typeof https.request)

  vi.spyOn(https, 'get').mockImplementation(((...args: unknown[]) => {
    throw unexpectedNetworkCallError('https.get', formatUnknown(args[0]))
  }) as unknown as typeof https.get)
}
