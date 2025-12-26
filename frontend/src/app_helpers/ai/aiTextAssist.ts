const SAFE_PREFIX_REWRITES: Record<string, string> = {
  'responsible for ': '',
  'worked on ': '',
  'helped ': '',
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function normalizeWhitespace(value: string): string {
  return value.replace(/\s+/g, ' ').trim()
}

function rewriteLine(value: string): string {
  let text = normalizeWhitespace(value.replace(/^[-*•]\s*/, ''))
  const lowered = text.toLowerCase()
  for (const [prefix, replacement] of Object.entries(SAFE_PREFIX_REWRITES)) {
    if (lowered.startsWith(prefix)) {
      text = replacement + text.slice(prefix.length)
      break
    }
  }
  text = text.trim()
  if (text.endsWith('.')) text = text.slice(0, -1).trim()
  if (text) text = text[0].toUpperCase() + text.slice(1)
  return text
}

export function htmlToPlainLines(html: string): string[] {
  const textWithNewlines = (html || '')
    .replace(/\r\n/g, '\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|div|li|h[1-6])>/gi, '\n')
    .replace(/<(ul|ol)[^>]*>/gi, '\n')
    .replace(/<\/(ul|ol)>/gi, '\n')
    .replace(/&nbsp;/g, ' ')
    .replace(/<[^>]*>/g, '')

  return textWithNewlines
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean)
}

function sentencesToBullets(text: string): string[] {
  const prepared = text
    .replace(/\r\n/g, '\n')
    .replace(/[•]+/g, '\n')
    .replace(/[;]+/g, '\n')
    .replace(/[.!?]+\s+/g, '\n')
  return prepared
    .split('\n')
    .map(v => v.trim())
    .filter(Boolean)
}

function bulletsToHtml(bullets: string[]): string {
  return `<ul>${bullets.map(b => `<li>${escapeHtml(b)}</li>`).join('')}</ul>`
}

function textToHtml(text: string): string {
  return `<p>${escapeHtml(text)}</p>`
}

function enforceMaxLength(
  plainLines: string[],
  maxLength?: number
): { lines: string[]; plainText: string } {
  if (!maxLength) return { lines: plainLines, plainText: plainLines.join('\n') }
  const chosen: string[] = []
  let size = 0
  for (const line of plainLines) {
    const nextSize = size ? size + 1 + line.length : line.length
    if (nextSize > maxLength) break
    chosen.push(line)
    size = nextSize
  }
  return { lines: chosen, plainText: chosen.join('\n') }
}

export function buildAiRewriteHtml(
  currentHtml: string,
  options: { mode: 'rewrite' | 'bullets'; maxLength?: number }
): string {
  const currentLines = htmlToPlainLines(currentHtml)
  const plainText = currentLines.join('\n')

  const lines =
    options.mode === 'bullets'
      ? sentencesToBullets(plainText)
      : currentLines.length
        ? currentLines
        : sentencesToBullets(plainText)

  const rewritten = lines.map(rewriteLine).filter(Boolean)
  const limited = enforceMaxLength(rewritten, options.maxLength)

  if (options.mode === 'bullets') return bulletsToHtml(limited.lines)
  // For rewrite mode, always return paragraphs (even if multiple lines)
  return textToHtml(limited.plainText || rewriteLine(plainText))
}
