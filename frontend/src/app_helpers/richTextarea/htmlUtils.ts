/**
 * HTML utility functions for RichTextarea component
 */

/**
 * Strips HTML tags from a string and returns plain text
 */
export function stripHtml(html: string): string {
  const tmp = document.createElement('DIV')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

/**
 * Normalizes HTML for comparison to handle TipTap's normalization differences.
 * Normalizes TO TipTap's format (with paragraphs in list items), not FROM it.
 */
export function normalizeHtmlForComparison(html: string): string {
  if (!html) return ''

  // Normalize empty paragraphs - TipTap may use either format
  let normalized = html.replace(/<p><\/p>/g, '<p><br></p>')
  normalized = normalized.replace(/<p><br><\/p>/g, '<p><br></p>')

  // FIX: Normalize list items WITHOUT paragraphs TO have paragraphs
  // TipTap ALWAYS wraps list item content in <p> tags by default
  // So we normalize TO TipTap's format (with paragraphs), not FROM it
  // This handles: <li>Item</li> -> <li><p>Item</p></li>
  // And: <li><strong>Item</strong></li> -> <li><p><strong>Item</strong></p></li>
  // Match list items that don't start with <p> tag
  normalized = normalized.replace(/<li>(?!<p>)(.*?)<\/li>/gs, '<li><p>$1</p></li>')

  // Normalize list items that already have paragraphs but might have whitespace issues
  // <li><p>  Item  </p></li> -> <li><p>Item</p></li>
  normalized = normalized.replace(/<li><p>\s+/g, '<li><p>')
  normalized = normalized.replace(/\s+<\/p><\/li>/g, '</p></li>')

  // Normalize empty list items: <li></li> vs <li><p></p></li> -> <li><p></p></li>
  normalized = normalized.replace(/<li><\/li>/g, '<li><p></p></li>')
  normalized = normalized.replace(/<li><p><\/p><\/li>/g, '<li><p></p></li>')
  normalized = normalized.replace(/<li><p><br><\/p><\/li>/g, '<li><p></p></li>')

  // Normalize whitespace in tags (including newlines between tags)
  normalized = normalized.replace(/>\s+</g, '><')

  normalized = normalized.trim()
  return normalized
}
