# Profile Lists Disappearing After Save and Reload Investigation

## Summary

**Issue**: Lists created in rich text fields disappear after saving and reloading the profile. The plain text content is preserved, but the list structure (`<ul>`, `<ol>`, `<li>` tags) is lost.

**Previous Fix Attempt**: Enhanced `normalizeHtmlForComparison` to handle list HTML normalization by unwrapping paragraphs from list items. However, this fix did not resolve the issue.

**Status**: ⚠️ **NOT FIXED** - See [Real Investigation](./profile-lists-disappearing-real-investigation.md) for updated analysis.

**Note**: The initial fix attempted to normalize list HTML by unwrapping paragraphs (`<li><p>text</p></li>` → `<li>text</li>`), but this approach was incorrect. TipTap requires paragraphs inside list items, and unwrapping them causes comparison mismatches that skip necessary updates.

**Files Modified**:
- `frontend/src/components/RichTextarea.tsx` (lines 29-38) - Enhanced HTML normalization function
- `frontend/src/__tests__/components/RichTextarea.test.tsx` - Added 5 test cases for list preservation

## Problem Description

Lists created in rich text fields (using the bullet list or ordered list buttons in the toolbar) disappear after saving and reloading the profile. The plain text content is preserved, but the list structure (`<ul>`, `<ol>`, `<li>` tags) is lost.

## Affected Components

This issue affects all RichTextarea components on the profile page:
1. **Personal Info Summary** (`PersonalInfo.tsx`)
2. **Experience Description** (`ExperienceItem.tsx`)
3. **Project Highlights** (`ProjectEditor.tsx`)

## Data Flow Analysis

### Save Flow
1. User creates a list in RichTextarea (TipTap editor) using toolbar buttons
2. TipTap emits HTML via `onUpdate`: `currentEditor.getHTML()` → e.g., `<ul><li>Item 1</li><li>Item 2</li></ul>`
3. React Hook Form stores HTML in form state
4. Frontend: `ProfileManager.onSubmit()` → `saveProfile(data)`
5. Frontend: `normalizeProfileDataForApi()` normalizes data (only trims whitespace, preserves HTML)
6. Backend: POST `/api/profile` → `save_profile_endpoint()`
7. Backend: `queries.save_profile()` → `build_save_params()` → stores `summary` and `description` directly
8. Database: Neo4j stores HTML strings in `Person.summary` and `Experience.description` properties

### Load Flow
1. Frontend: `ProfileManager.loadInitialProfile()` → `getProfile()`
2. Frontend: `profileService.getProfile()` → GET `/api/profile`
3. Backend: `get_profile_endpoint()` → `queries.get_profile()`
4. Backend: `process_profile_record()` retrieves `person.get("summary")` and `exp.get("description")`
5. Backend: Returns profile data with HTML strings intact
6. Frontend: `reset(profile)` updates React Hook Form state
7. RichTextarea receives HTML via `value` prop
8. **ISSUE**: List HTML is lost at this point

## Root Cause Analysis

### Issue #1: HTML Normalization Function Doesn't Handle Lists

**Location**: `frontend/src/components/RichTextarea.tsx:29-38`

The `normalizeHtmlForComparison` function only normalizes paragraph tags:

```typescript
function normalizeHtmlForComparison(html: string): string {
  if (!html) return ''
  // Normalize empty paragraphs - TipTap may use either format
  let normalized = html.replace(/<p><\/p>/g, '<p><br></p>')
  normalized = normalized.replace(/<p><br><\/p>/g, '<p><br></p>')
  // Normalize whitespace in tags
  normalized = normalized.replace(/>\s+</g, '><')
  normalized = normalized.trim()
  return normalized
}
```

**Problem**: This function:
- Only handles `<p>` tag normalization
- Normalizes whitespace between tags (`>\s+<`), but this regex might not catch all list HTML variations
- Doesn't specifically normalize list HTML structure (`<ul>`, `<ol>`, `<li>`)

### Issue #2: TipTap List HTML Normalization Differences

TipTap may output list HTML in different formats:
- **Output format**: `<ul><li>Item 1</li><li>Item 2</li></ul>` (compact, no newlines)
- **Input normalization**: TipTap might normalize to `<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n</ul>` (with newlines)
- **Or vice versa**: Input might have newlines, output might be compact

The whitespace normalization regex `/>\s+</g` should catch newlines between tags, but there might be edge cases:
- Newlines inside `<li>` tags: `<li>\nItem 1\n</li>` vs `<li>Item 1</li>`
- Whitespace around list items
- Empty list items: `<li></li>` vs `<li><p></p></li>`

### Issue #3: Comparison Logic May Skip List Updates

**Location**: `frontend/src/components/RichTextarea.tsx:109-191`

The `useEffect` hook has multiple comparison checks. If list HTML normalization fails, the comparison might incorrectly identify lists as "matching" when they don't, or skip updates when they should happen.

**Scenario**:
1. User creates list: TipTap outputs `<ul><li>Item 1</li><li>Item 2</li></ul>`
2. Profile is saved with this HTML
3. Profile is loaded: HTML might be `<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n</ul>` (with newlines)
4. `normalizeHtmlForComparison` normalizes whitespace: both become `<ul><li>Item 1</li><li>Item 2</li></ul>`
5. Comparison should match... **BUT** if TipTap's internal normalization differs, the comparison might fail
6. If plain text matches but HTML comparison fails, the update might be skipped incorrectly

### Issue #4: TipTap StarterKit List Support

**Location**: `frontend/src/components/RichTextarea.tsx:62-70`

```typescript
const extensions = useMemo(
  () => [
    StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
    Underline,
    Link.configure({ openOnClick: false, autolink: false }),
    Placeholder.configure({ placeholder: placeholder || '' }),
  ],
  [placeholder]
)
```

**Analysis**: TipTap StarterKit includes `BulletList` and `OrderedList` extensions by default, so list support should be available. The toolbar buttons (`RichTextToolbar.tsx`) confirm this with `toggleBulletList()` and `toggleOrderedList()` commands.

### Issue #5: Missing Test Coverage

**Location**: `frontend/src/__tests__/components/RichTextarea.test.tsx`

The test suite includes tests for:
- Paragraph preservation
- Bold/italic formatting preservation
- Line break preservation
- HTML normalization differences

**BUT** there are **NO tests** for list HTML preservation. This is a gap in test coverage.

## Potential Root Causes (Ranked by Likelihood)

### 1. **HTML Normalization Doesn't Handle List Edge Cases** (Most Likely)

The `normalizeHtmlForComparison` function normalizes whitespace between tags, but TipTap might:
- Wrap list items in paragraphs: `<ul><li><p>Item 1</p></li></ul>` vs `<ul><li>Item 1</li></ul>`
- Add/remove whitespace inside list items
- Normalize empty list items differently

**Evidence**: The function only handles `<p>` tags specifically, not list structure.

### 2. **TipTap List HTML Format Differences**

TipTap might output list HTML in a format that differs from what it accepts as input:
- Output: `<ul><li>Item</li></ul>`
- Input normalization: TipTap might expect or normalize to a different format
- If the formats don't match exactly, TipTap might strip the list structure

**Evidence**: Similar issues were found with paragraph normalization (see `profile-line-breaks-investigation.md`).

### 3. **Comparison Logic Skips List Updates**

If the HTML comparison fails but plain text matches, the update might be skipped:
- List HTML: `<ul><li>Item 1</li><li>Item 2</li></ul>`
- Plain text: `"Item 1\nItem 2"` (or similar)
- If normalization doesn't match exactly, but plain text does, update might be skipped

**Evidence**: The comparison logic at lines 168-175 checks both plain text AND HTML, but if HTML normalization fails, the check might not work correctly for lists.

## How to Verify

### 1. Check What HTML TipTap Outputs for Lists

Add logging to see what HTML TipTap generates:

```typescript
// In RichTextarea.tsx onUpdate handler
onUpdate: ({ editor: currentEditor }) => {
  const html = currentEditor.getHTML()
  console.log('TipTap output HTML:', html)
  // ... rest of code
}
```

Create a list, save, and check the console output.

### 2. Check What HTML Is Loaded from Database

Add logging to see what HTML is received when loading:

```typescript
// In RichTextarea.tsx useEffect
useEffect(() => {
  if (!editor) return
  console.log('Received value HTML:', value)
  console.log('Current editor HTML:', editor.getHTML())
  // ... rest of code
}, [editor, value])
```

Load a profile with lists and check the console output.

### 3. Check HTML Normalization

Add logging to see how HTML is normalized:

```typescript
// In normalizeHtmlForComparison function
function normalizeHtmlForComparison(html: string): string {
  console.log('Input HTML:', html)
  // ... normalization code ...
  console.log('Normalized HTML:', normalized)
  return normalized
}
```

Compare input vs normalized HTML for lists.

### 4. Test with Minimal List HTML

Test with simple list HTML:
- Save: `<ul><li>Test</li></ul>`
- Reload and check if `<ul>` and `<li>` tags are preserved

### 5. Check Browser DevTools

1. Inspect network request to `/api/profile` - verify list HTML is in the response
2. Check React Hook Form state after `reset()` - verify list HTML is in form state
3. Check RichTextarea props - verify list HTML is passed as `value` prop
4. Inspect editor DOM - check if `<ul>`/`<ol>` elements exist in the editor

## How to Fix

### Solution 1: Enhance HTML Normalization for Lists (Recommended)

Update `normalizeHtmlForComparison` to handle list HTML:

```typescript
function normalizeHtmlForComparison(html: string): string {
  if (!html) return ''

  // Normalize empty paragraphs - TipTap may use either format
  let normalized = html.replace(/<p><\/p>/g, '<p><br></p>')
  normalized = normalized.replace(/<p><br><\/p>/g, '<p><br></p>')

  // Normalize list items wrapped in paragraphs: <li><p>text</p></li> -> <li>text</li>
  // TipTap might wrap list item content in paragraphs
  normalized = normalized.replace(/<li><p>(.*?)<\/p><\/li>/g, '<li>$1</li>')

  // Normalize empty list items: <li></li> vs <li><p></p></li>
  normalized = normalized.replace(/<li><p><\/p><\/li>/g, '<li></li>')
  normalized = normalized.replace(/<li><p><br><\/p><\/li>/g, '<li></li>')

  // Normalize whitespace in tags (including newlines)
  normalized = normalized.replace(/>\s+</g, '><')

  // Normalize whitespace inside list items (but preserve content)
  // This handles cases like <li>\nItem\n</li> vs <li>Item</li>
  normalized = normalized.replace(/<li>\s+/g, '<li>')
  normalized = normalized.replace(/\s+<\/li>/g, '</li>')

  normalized = normalized.trim()
  return normalized
}
```

### Solution 2: Add List-Specific Comparison Logic

Add explicit checks for list HTML in the comparison logic:

```typescript
// In RichTextarea.tsx useEffect
useEffect(() => {
  if (!editor) return

  // ... existing checks ...

  // Check if content contains lists
  const hasListsInValue = /<(ul|ol)>/i.test(normalizedValue)
  const hasListsInEditor = /<(ul|ol)>/i.test(currentHtml)

  // If lists are present, be more strict about HTML matching
  if (hasListsInValue || hasListsInEditor) {
    // Force update if lists are involved, even if plain text matches
    if (normalizedValueHtml !== normalizedCurrentHtml) {
      lastKnownHtmlRef.current = normalizedValue
      lastEmittedValueRef.current = normalizedValue
      editor.commands.setContent(normalizedValue, false)
      setTextLength(editor.getText().length)
      return
    }
  }

  // ... rest of comparison logic ...
}, [editor, value])
```

### Solution 3: Verify TipTap List Extensions Configuration

Ensure list extensions are properly configured:

```typescript
// In RichTextarea.tsx
const extensions = useMemo(
  () => [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
      // Explicitly ensure list extensions are enabled
      bulletList: {},
      orderedList: {},
      listItem: {},
    }),
    Underline,
    Link.configure({ openOnClick: false, autolink: false }),
    Placeholder.configure({ placeholder: placeholder || '' }),
  ],
  [placeholder]
)
```

### Solution 4: Add Test Coverage for Lists

Add tests to verify list preservation:

```typescript
// In RichTextarea.test.tsx
it('preserves bullet list HTML when profile is loaded', async () => {
  const onChange = vi.fn()
  const { rerender } = render(<RichTextarea id="test-textarea" value="" onChange={onChange} />)

  const editor = document.querySelector('.ql-editor') as HTMLElement

  // Simulate profile load with list HTML
  const listHtml = '<ul><li>Item 1</li><li>Item 2</li></ul>'
  rerender(<RichTextarea id="test-textarea" value={listHtml} onChange={onChange} />)

  await waitFor(() => {
    expect(editor.textContent).toContain('Item 1')
    expect(editor.textContent).toContain('Item 2')
  })

  // Verify list HTML is preserved
  const editorHtml = editor.innerHTML
  expect(editorHtml).toContain('<ul>')
  expect(editorHtml).toContain('<li>')
})

it('preserves ordered list HTML when profile is loaded', async () => {
  // Similar test for <ol> lists
})
```

## Recommended Fix

**Combine Solution 1 and Solution 4**:
1. Enhance `normalizeHtmlForComparison` to handle list HTML normalization
2. Add test coverage for list preservation
3. Add logging to diagnose the exact issue

This approach:
- ✅ Handles list HTML normalization differences
- ✅ Provides test coverage to prevent regressions
- ✅ Maintains existing safeguards for race conditions
- ✅ Doesn't break existing functionality

## Testing Strategy

1. **Test List Preservation**:
   - Create bullet list, save profile, reload → verify list structure preserved
   - Create ordered list, save profile, reload → verify list structure preserved
   - Create nested lists, save profile, reload → verify nested structure preserved

2. **Test Edge Cases**:
   - Empty list items: `<ul><li></li></ul>`
   - Lists with formatting: `<ul><li><strong>Bold</strong> item</li></ul>`
   - Lists with links: `<ul><li>Item with <a href="#">link</a></li></ul>`
   - Mixed content: Lists with paragraphs

3. **Test Normalization**:
   - Save with compact HTML: `<ul><li>Item</li></ul>`
   - Load with newlines: `<ul>\n<li>Item</li>\n</ul>`
   - Verify both formats are handled correctly

## Related Issues

- Similar issue was fixed for HTML formatting: `docs/troubleshooting/profile-html-formatting-lost.md`
- Similar issue was fixed for line breaks: `docs/troubleshooting/profile-line-breaks-investigation.md`
- This appears to be a more specific case of list HTML not being preserved during form reset

## Implementation Status

**Status**: ⚠️ **NOT FIXED** - Previous fix did not resolve the issue

The previous fix attempted to normalize list HTML by unwrapping paragraphs, but this was incorrect. TipTap requires paragraphs inside list items, and the normalization approach caused comparison mismatches.

**Issue with Previous Fix**:
- Normalization unwrapped paragraphs: `<li><p>text</p></li>` → `<li>text</li>`
- But TipTap requires paragraphs inside list items
- This caused comparison logic to skip updates incorrectly
- Tests passed because they checked DOM (`innerHTML`), not TipTap's HTML (`getHTML()`)

**See**: [Real Investigation](./profile-lists-disappearing-real-investigation.md) for updated root cause analysis and proper fix approach.

## Files Modified (Previous Attempt)

- `frontend/src/components/RichTextarea.tsx` - Enhanced HTML normalization function (lines 29-38) - **This fix was incorrect**
- `frontend/src/__tests__/components/RichTextarea.test.tsx` - Added 5 test cases - **Tests check DOM, not TipTap HTML**
