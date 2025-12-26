# RichTextarea Text Clearing Issue

## Problem Description

When users type text in the work experience role summary text editor (and potentially other RichTextarea fields), the text vanishes immediately after being typed. The text appears to flash/disappear right away, making it impossible to enter content.

## Root Cause

The issue is caused by a race condition between TipTap editor's `onUpdate` callback and React Hook Form's asynchronous state updates:

1. **User types** → TipTap's `onUpdate` fires → calls `onChange(html)` → updates React Hook Form state
2. **React re-renders** → `useEffect` hook runs to sync the `value` prop back to the editor
3. **Race condition**: React Hook Form's state updates are asynchronous, so when `useEffect` runs:
   - The `value` prop might still be the old/stale value (before React Hook Form processes the update)
   - The comparison `value === lastKnownHtmlRef.current` fails
   - The effect calls `editor.commands.setContent(value || '', false)` with the stale/empty value
   - **Result**: Editor content is cleared, wiping out what the user just typed

### Additional Contributing Factors

- **HTML normalization differences**: TipTap might output slightly different HTML than what React Hook Form stores (whitespace, empty paragraphs, etc.), causing comparison failures
- **Multiple re-renders**: React's batching and React Hook Form's internal state management can cause multiple re-renders in quick succession
- **Timing sensitivity**: The issue is timing-dependent and may not occur consistently, making it harder to debug

## Solution

Implemented a multi-layered approach to prevent clearing user input. Additional enhancements were later added to handle line break issues (see Related Issues below):

### 1. Track Last Emitted Value

Added `lastEmittedValueRef` to track the exact value we send via `onChange`:

```typescript
const lastEmittedValueRef = useRef<string>(value || '')

onUpdate: ({ editor: currentEditor }) => {
  const html = currentEditor.getHTML()
  lastEmittedValueRef.current = html  // Track what we emitted
  onChange(html)
}
```

### 2. Multiple Comparison Strategies

The `useEffect` hook now uses multiple checks before updating the editor:

```typescript
// Skip update if:
// 1. Value HTML matches what we last emitted (this update came from our onChange)
// 2. Value HTML matches current editor content (already in sync)
// 3. Value HTML matches last known value (already synced)
// 4. Plain text content matches AND editor is focused (user is typing)
// 5. Plain text matches (handles HTML normalization differences)
```

### 3. Plain Text Fallback Comparison

Added plain text comparison as a fallback to handle HTML normalization differences:

```typescript
const currentText = editor.getText()
const valueText = stripHtml(normalizedValue)

if (valueText === currentText && valueText.length > 0) {
  // Skip update - content is the same, just HTML format differs
  return
}
```

### 4. Editor Focus Check

Added focus check as an additional safeguard:

```typescript
const isFocused = editor.isFocused

if (valueText === currentText && valueText.length > 0 && isFocused) {
  // User is actively typing - definitely skip update
  return
}
```

## Files Modified

- `frontend/src/components/RichTextarea.tsx`
  - Added `lastEmittedValueRef` to track emitted values
  - Enhanced `useEffect` with multiple comparison strategies
  - Updated `onUpdate` handler to track emitted values
  - Updated AI assist functions to maintain ref consistency

## Testing

All existing tests pass:
- ✅ RichTextarea component tests (23/23) - includes tests for line break preservation
- ✅ RichTextarea AI Assist tests (5/5)
- ✅ Experience component tests (6/6)

## Impact

- **Fixed**: Users can now type in work experience role summary without text clearing
- **Preserved**: Form reset and profile load functionality still work correctly
- **Preserved**: AI rewrite and AI bullets features continue to function
- **No breaking changes**: Component API and behavior remain the same

## Related Components

This fix applies to all RichTextarea usages:
1. **Personal Info Summary** (`PersonalInfo.tsx`)
2. **Experience Description** (`ExperienceItem.tsx`) - **Primary issue location**
3. **Project Highlights** (`ProjectEditor.tsx`)

## Related Issues

A similar but more specific issue was later identified and fixed:
- **Line Break Issue**: Users couldn't create line breaks (Enter key) in profile page text editors
- See [Profile Line Breaks Investigation](./profile-line-breaks-investigation.md) for details
- The fix added HTML normalization and active editing state tracking to the existing safeguards

## Prevention

To prevent similar issues in the future:

1. **Always track emitted values** when using controlled components with async state updates
2. **Use multiple comparison strategies** (HTML, plain text, refs) to handle normalization differences
3. **Check editor state** (focus, content) before syncing props back to editor
4. **Test with real user typing scenarios** - unit tests may not catch timing-dependent race conditions
5. **Normalize HTML before comparison** - TipTap may normalize HTML differently when reading vs writing
6. **Track active editing state** - prevent updates during user input to avoid race conditions
