# Profile Page Line Breaks Investigation

## Problem Description

On the #profile page, users cannot make line breaks in text editors. When pressing Enter, the text appears to revert to a previous state, as if it's being "reinstated from memory."

## Affected Components

This issue affects all RichTextarea components on the profile page:
1. **Personal Info Summary** (`PersonalInfo.tsx`)
2. **Experience Description** (`ExperienceItem.tsx`)
3. **Project Highlights** (`ProjectEditor.tsx`)

## Root Cause Analysis

### The Problem Flow

1. **User presses Enter** in TipTap editor
   - TipTap creates a new paragraph: `<p>existing text</p><p></p>` or `<p>existing text</p><p><br></p>`
   - TipTap's `onUpdate` callback fires

2. **onUpdate handler executes** (`RichTextarea.tsx:76-82`)
   ```typescript
   onUpdate: ({ editor: currentEditor }) => {
     const html = currentEditor.getHTML()
     lastKnownHtmlRef.current = html
     lastEmittedValueRef.current = html
     setTextLength(currentEditor.getText().length)
     onChange(html)  // Updates React Hook Form state
   }
   ```

3. **React Hook Form state updates**
   - `onChange` triggers React Hook Form's `field.onChange`
   - React Hook Form updates its internal state asynchronously
   - Component re-renders with new `value` prop

4. **useEffect runs** (`RichTextarea.tsx:85-147`)
   - Compares incoming `value` prop with current editor content
   - **THE PROBLEM**: TipTap normalizes HTML differently when:
     - Reading HTML via `getHTML()` (what we emit)
     - Setting HTML via `setContent()` (what we receive back)

5. **HTML Normalization Mismatch**
   - When TipTap outputs HTML via `getHTML()`, it might produce: `<p>text</p><p></p>`
   - When TipTap receives HTML via `setContent()`, it normalizes to: `<p>text</p><p><br></p>` (or vice versa)
   - The exact HTML format depends on TipTap's internal normalization rules

6. **Comparison Fails**
   - `normalizedValue === currentHtml` returns `false` due to normalization differences
   - Plain text comparison (`valueText === currentText`) might also fail if:
     - The empty paragraph affects text extraction
     - TipTap's `getText()` handles empty paragraphs differently than `stripHtml()`

7. **Editor Content Reset**
   - Since comparisons fail, `useEffect` treats this as an "external update"
   - Calls `editor.commands.setContent(normalizedValue, false)` with the old/stale value
   - **Result**: Editor content reverts to previous state, losing the line break

### Why the Existing Safeguards Don't Work

The `RichTextarea` component has several safeguards to prevent this issue:

1. **Focus Check** (line 97): Checks if editor is focused
   - **Issue**: Focus check alone isn't sufficient - the HTML normalization happens regardless of focus

2. **Last Emitted Value Tracking** (line 116): Compares with `lastEmittedValueRef.current`
   - **Issue**: React Hook Form's async state updates mean the `value` prop might not match `lastEmittedValueRef.current` immediately

3. **Plain Text Comparison** (line 134): Falls back to plain text comparison
   - **Issue**: When Enter is pressed, TipTap creates an empty paragraph, which might affect text extraction differently in `getText()` vs `stripHtml()`

4. **Current HTML Comparison** (line 121): Compares with `editor.getHTML()`
   - **Issue**: This is where the normalization mismatch occurs - TipTap normalizes HTML differently when reading vs writing

## Technical Details

### TipTap HTML Normalization

TipTap's StarterKit normalizes HTML in the following ways:
- Empty paragraphs: `<p></p>` vs `<p><br></p>` - TipTap may normalize these inconsistently
- Whitespace: Leading/trailing whitespace in paragraphs may be normalized
- Line breaks: `<br>` tags may be added/removed during normalization

### React Hook Form Async Updates

React Hook Form updates are asynchronous:
1. `onChange` is called → React Hook Form schedules state update
2. React re-renders → `useEffect` runs
3. `value` prop might still contain the old value (before React Hook Form processes the update)
4. Comparison fails → Editor content gets reset

### The Race Condition

The race condition occurs because:
- TipTap's `onUpdate` fires synchronously when Enter is pressed
- React Hook Form's state update is asynchronous
- `useEffect` runs before React Hook Form has processed the update
- The `value` prop contains stale data
- Comparison logic incorrectly identifies this as an external update

## How to Fix

### Solution 1: Improve HTML Normalization Comparison (Recommended)

Normalize HTML before comparing to handle TipTap's normalization differences:

```typescript
function normalizeHtml(html: string): string {
  // Normalize empty paragraphs
  html = html.replace(/<p><\/p>/g, '<p><br></p>')
  html = html.replace(/<p><br><\/p>/g, '<p><br></p>')
  // Normalize whitespace
  html = html.replace(/\s+/g, ' ').trim()
  return html
}

// In useEffect:
const normalizedCurrentHtml = normalizeHtml(currentHtml)
const normalizedValueHtml = normalizeHtml(normalizedValue)

if (normalizedValueHtml === normalizedCurrentHtml) {
  // Skip update
  return
}
```

### Solution 2: Delay useEffect Execution When Editor is Focused

Add a small delay when editor is focused to allow React Hook Form to process updates:

```typescript
if (isFocused) {
  // Use setTimeout to allow React Hook Form to process async updates
  const timeoutId = setTimeout(() => {
    // Re-check after React Hook Form has processed the update
    const updatedHtml = editor.getHTML()
    const updatedValue = value || ''
    if (normalizeHtml(updatedValue) === normalizeHtml(updatedHtml)) {
      return
    }
    // Only update if still different after delay
  }, 0)

  return () => clearTimeout(timeoutId)
}
```

### Solution 3: Use TipTap's JSON Format for Comparison

Instead of comparing HTML strings, compare TipTap's internal JSON representation:

```typescript
const currentJson = JSON.stringify(editor.getJSON())
const valueJson = JSON.stringify(editor.state.schema.nodeFromJSON(value).toJSON())

if (currentJson === valueJson) {
  return
}
```

**Note**: This requires converting HTML to TipTap JSON format, which adds complexity.

### Solution 4: Track Editing State More Precisely

Track when user is actively typing (not just focused):

```typescript
const [isEditing, setIsEditing] = useState(false)

// In onUpdate:
onUpdate: ({ editor: currentEditor }) => {
  setIsEditing(true)
  // ... existing code ...
  setTimeout(() => setIsEditing(false), 100)
}

// In useEffect:
if (isEditing) {
  // Skip updates while user is actively editing
  return
}
```

## Recommended Fix

**Combine Solution 1 and Solution 4**:
1. Add HTML normalization function to handle TipTap's normalization differences
2. Track active editing state to prevent updates during typing
3. Improve the comparison logic to use normalized HTML

This approach:
- ✅ Handles HTML normalization differences
- ✅ Prevents race conditions during active editing
- ✅ Maintains existing functionality (form reset, profile load)
- ✅ Minimal performance impact

## Implementation Status

**Status**: ✅ **FIXED**

The fix has been implemented in `frontend/src/components/RichTextarea.tsx`:
- Added `normalizeHtmlForComparison()` function to handle HTML normalization
- Added `isEditingRef` and `editingTimeoutRef` for active editing state tracking
- Updated `onUpdate` handler to set editing flag with 150ms delay
- Enhanced `useEffect` comparison logic to use normalized HTML and check editing state
- Added cleanup effect for timeout on unmount

All tests pass (23/23) including new tests for:
- Enter key line break preservation
- Shift+Enter line break preservation
- Multiple paragraphs preservation
- Rapid Enter key presses
- HTML normalization differences

See commit history for implementation details.

## Testing Strategy

1. **Test Enter Key**: Press Enter in each RichTextarea field and verify line break is preserved
2. **Test Shift+Enter**: Press Shift+Enter to create `<br>` tags and verify they're preserved
3. **Test Multiple Line Breaks**: Create multiple paragraphs and verify all are preserved
4. **Test Form Reset**: Verify form reset still works correctly
5. **Test Profile Load**: Verify loading a profile doesn't interfere with editing
6. **Test Rapid Typing**: Type quickly and press Enter multiple times to test race conditions

## Related Issues

- Similar issue was fixed for text clearing: `docs/troubleshooting/richtextarea-text-clearing.md`
- This is a more specific case of the same underlying race condition
- The fix should be compatible with the existing text clearing prevention logic

## Files to Modify

- `frontend/src/components/RichTextarea.tsx`
  - Add HTML normalization function
  - Improve comparison logic in `useEffect`
  - Add active editing state tracking

## Impact

- **Fixed**: Users can now create line breaks in profile text editors
- **Preserved**: Form reset and profile load functionality
- **Preserved**: AI rewrite and AI bullets features
- **No breaking changes**: Component API remains the same
