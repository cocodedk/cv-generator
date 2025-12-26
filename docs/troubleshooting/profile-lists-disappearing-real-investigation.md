# Profile Lists Disappearing - Real Investigation

## Problem

Tests pass but lists still disappear after profile page reload. The tests are checking the DOM (`editor.innerHTML`), but TipTap's actual HTML format (`editor.getHTML()`) may differ.

## Key Insight: TipTap's List HTML Format

**TipTap ALWAYS wraps list item content in `<p>` tags by default.**

When TipTap outputs HTML via `getHTML()`:
- Output: `<ul><li><p>Item 1</p></li><li><p>Item 2</p></li></ul>`

When TipTap receives HTML via `setContent()`:
- Input: `<ul><li>Item 1</li><li>Item 2</li></ul>`
- TipTap normalizes to: `<ul><li><p>Item 1</p></li><li><p>Item 2</p></li></ul>`

## The Problem with Current Normalization

The `normalizeHtmlForComparison` function unwraps paragraphs:
```typescript
normalized = normalized.replace(/<li><p>(.*?)<\/p><\/li>/gs, '<li>$1</li>')
```

This means:
1. **Saved HTML** (from TipTap `getHTML()`): `<ul><li><p>Item</p></li></ul>`
2. **Normalized saved**: `<ul><li>Item</li></ul>` (paragraphs unwrapped)
3. **Loaded HTML** (from database): `<ul><li><p>Item</p></li></ul>` (if saved correctly)
4. **Normalized loaded**: `<ul><li>Item</li></ul>` (paragraphs unwrapped)
5. **Comparison**: They match! ✅
6. **BUT**: When TipTap receives `<ul><li>Item</li></ul>` via `setContent()`, it wraps it back: `<ul><li><p>Item</p></li></ul>`

So the normalization works for comparison, but the actual HTML being set might be wrong.

## Potential Root Causes

### Issue #1: Normalization Unwraps Paragraphs But TipTap Requires Them

**Problem**: The normalization function unwraps `<li><p>Item</p></li>` to `<li>Item</li>`, but TipTap's schema requires paragraphs inside list items. When we set content without paragraphs, TipTap adds them back, but this might cause issues.

**Evidence**: TipTap's StarterKit ListItem extension wraps content in paragraphs by default.

### Issue #2: Tests Check DOM, Not TipTap's HTML

**Problem**: Tests check `editor.innerHTML` (DOM), but TipTap's `getHTML()` returns ProseMirror's HTML representation, which might differ.

**Test code**:
```typescript
const editorHtml = editor.innerHTML
expect(editorHtml).toContain('<ul>')
```

**Issue**: `editor.innerHTML` shows what's rendered in the DOM, but `editor.getHTML()` shows TipTap's internal representation. These might differ!

### Issue #3: Comparison Logic May Skip Updates Incorrectly

**Problem**: If normalization makes saved and loaded HTML match, the comparison logic skips the update. But if the actual HTML format differs (with/without paragraphs), TipTap might not render lists correctly.

**Location**: `RichTextarea.tsx:180-184`
```typescript
if (normalizedValueHtml === normalizedCurrentHtml) {
  lastKnownHtmlRef.current = normalizedValue
  lastEmittedValueRef.current = normalizedValue
  return  // ⚠️ Skips update!
}
```

### Issue #4: HTML Saved to Database May Be Wrong Format

**Problem**: When TipTap outputs HTML via `getHTML()`, it includes paragraph wrappers. But if the normalization function is applied BEFORE saving, we might be saving unwrapped HTML to the database.

**Check**: What HTML is actually saved to the database? Is it `<ul><li><p>Item</p></li></ul>` or `<ul><li>Item</li></ul>`?

## Investigation Steps

### Step 1: Check What HTML TipTap Actually Outputs

Add logging to see TipTap's actual HTML format:

```typescript
// In RichTextarea.tsx onUpdate handler
onUpdate: ({ editor: currentEditor }) => {
  const html = currentEditor.getHTML()
  console.log('TipTap getHTML() output:', html)
  console.log('TipTap getHTML() for list:', html.includes('<ul>') || html.includes('<ol>') ? html : 'no list')
  // ... rest of code
}
```

Create a list, save, and check console output.

### Step 2: Check What HTML Is Saved to Database

Add logging to see what's being saved:

```typescript
// In ProfileManager.tsx onSubmit
const onSubmit = async (data: CVData) => {
  console.log('Saving profile with HTML:', JSON.stringify(data.personal_info.summary))
  // ... rest of code
}
```

### Step 3: Check What HTML Is Loaded from Database

Add logging to see what's loaded:

```typescript
// In ProfileManager.tsx loadInitialProfile
const loadInitialProfile = async () => {
  const profile = await getProfile()
  if (profile) {
    console.log('Loaded profile HTML:', JSON.stringify(profile.personal_info.summary))
    // ... rest of code
  }
}
```

### Step 4: Check What HTML TipTap Receives

Add logging in RichTextarea useEffect:

```typescript
useEffect(() => {
  if (!editor) return
  console.log('RichTextarea received value:', value)
  console.log('TipTap current HTML:', editor.getHTML())
  console.log('Normalized value:', normalizeHtmlForComparison(value))
  console.log('Normalized current:', normalizeHtmlForComparison(editor.getHTML()))
  // ... rest of code
}, [editor, value])
```

### Step 5: Check DOM vs TipTap HTML

Compare what's in the DOM vs what TipTap reports:

```typescript
// In test or browser console
const editor = document.querySelector('.ql-editor')
console.log('DOM innerHTML:', editor.innerHTML)
console.log('TipTap getHTML():', editorInstance.getHTML())
```

## Expected Findings

Based on TipTap's behavior:

1. **TipTap outputs**: `<ul><li><p>Item</p></li></ul>` (with paragraphs)
2. **Database should store**: `<ul><li><p>Item</p></li></ul>` (same format)
3. **TipTap receives**: `<ul><li><p>Item</p></li></ul>` (from database)
4. **Normalization unwraps**: `<ul><li>Item</li></ul>` (for comparison)
5. **Comparison matches**: ✅ (both normalized to same format)
6. **Update skipped**: ⚠️ (because normalized HTML matches)
7. **BUT**: If editor already has different format, lists might not render correctly

## Potential Fixes

### Fix #1: Don't Unwrap Paragraphs in Normalization

Instead of unwrapping paragraphs, normalize TO TipTap's format (with paragraphs):

```typescript
function normalizeHtmlForComparison(html: string): string {
  if (!html) return ''

  // Normalize empty paragraphs
  let normalized = html.replace(/<p><\/p>/g, '<p><br></p>')
  normalized = normalized.replace(/<p><br><\/p>/g, '<p><br></p>')

  // Normalize list items WITHOUT paragraphs TO have paragraphs
  // TipTap requires paragraphs inside list items
  normalized = normalized.replace(/<li>([^<]+)<\/li>/g, '<li><p>$1</p></li>')

  // Normalize whitespace
  normalized = normalized.replace(/>\s+</g, '><')
  normalized = normalized.trim()
  return normalized
}
```

### Fix #2: Always Use TipTap's Format (With Paragraphs)

Ensure we always save and load HTML in TipTap's native format (with paragraph wrappers):

```typescript
// In onUpdate handler
onUpdate: ({ editor: currentEditor }) => {
  const html = currentEditor.getHTML()  // Already has paragraphs
  onChange(html)  // Save as-is
}

// In useEffect, set content as-is (TipTap will normalize if needed)
editor.commands.setContent(value, false)
```

### Fix #3: Fix Tests to Check TipTap's HTML, Not DOM

Update tests to check `editor.getHTML()` instead of `editor.innerHTML`:

```typescript
it('preserves bullet list HTML when profile is loaded', async () => {
  // ... setup ...

  // Get TipTap's HTML representation, not DOM
  const editorInstance = // ... get editor instance ...
  const tipTapHtml = editorInstance.getHTML()
  expect(tipTapHtml).toContain('<ul>')
  expect(tipTapHtml).toContain('<li>')
  expect(tipTapHtml).toContain('<p>')  // TipTap wraps in paragraphs!
})
```

### Fix #4: Force Update When Lists Are Present

Add special handling for lists to ensure they're always updated:

```typescript
// In useEffect
const hasLists = /<(ul|ol)>/i.test(value) || /<(ul|ol)>/i.test(editor.getHTML())

if (hasLists) {
  // For lists, always update if HTML differs (even if normalized matches)
  // This ensures TipTap's internal format is correct
  if (value !== editor.getHTML()) {
    editor.commands.setContent(value, false)
    return
  }
}
```

## Most Likely Root Cause

**The normalization function unwraps paragraphs, but TipTap requires them. When we compare normalized HTML, they match, so the update is skipped. But the actual HTML format might be wrong, causing TipTap to not render lists correctly.**

The fix should be to:
1. Normalize TO TipTap's format (with paragraphs), not FROM it
2. OR: Don't normalize list HTML at all, let TipTap handle it
3. OR: Always force update when lists are present

## Next Steps

1. Add logging to see actual HTML formats at each step
2. Verify what HTML is saved to database
3. Verify what HTML TipTap outputs vs receives
4. Fix normalization or comparison logic based on findings
5. Update tests to check TipTap's HTML format, not DOM
