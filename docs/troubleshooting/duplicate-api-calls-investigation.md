# Duplicate API Calls Investigation

## Problem Description

When loading `http://localhost:5173/#edit/3ca980a7-202c-472c-bfce-554075484f9f`, the application makes multiple duplicate API calls to `/api/cv/3ca980a7-202c-472c-bfce-554075484f9f`. In the logs, 8 duplicate calls are observed.

## Root Cause Analysis

### Primary Contributing Factors

1. **React.StrictMode Double Invocation**
   - `main.tsx` wraps the app in `<React.StrictMode>`
   - In development, StrictMode intentionally double-invokes effects, state updaters, and other functions
   - This causes `useCvLoader`'s effect to run twice for each actual state change

2. **useHashRouting State Synchronization Loop**
   - `useHashRouting.ts` has two interacting `useEffect` hooks:
     - **First effect (lines 30-47)**: Syncs state with hash, can modify `window.location.hash`
     - **Second effect (lines 49-69)**: Listens to `hashchange` events and updates state
   - When the first effect modifies the hash (line 44), it triggers a `hashchange` event
   - The second effect handles this event and updates state (`setCvId`, `setViewMode`, etc.)
   - State updates cause re-renders, which can trigger the first effect again
   - This creates a potential cycle of state updates

3. **cvId State Changes Triggering useCvLoader**
   - `useCvLoader` has a `useEffect` that depends on `cvId` (line 52)
   - Every time `cvId` changes (even if it's the same value), the effect runs
   - The effect makes an API call to `/api/cv/${cvId}` (line 28)
   - With multiple state updates from `useHashRouting`, `cvId` can change multiple times

4. **Component Re-mounting**
   - If `CVForm` component unmounts and remounts (due to view mode changes or re-renders), `useCvLoader` runs again
   - Each mount triggers the effect, causing additional API calls

### The Flow

```
1. Page loads with #edit/3ca980a7-202c-472c-bfce-554075484f9f
   ↓
2. useHashRouting initializes state from hash
   - cvId = "3ca980a7-202c-472c-bfce-554075484f9f"
   ↓
3. First useEffect in useHashRouting runs (StrictMode: runs twice)
   - Checks if hash matches expected hash
   - May modify window.location.hash if mismatch
   ↓
4. Hash modification triggers hashchange event
   ↓
5. Second useEffect in useHashRouting handles hashchange
   - Updates state (setCvId, setViewMode, etc.)
   ↓
6. State update causes re-render
   ↓
7. CVForm receives new cvId prop
   ↓
8. useCvLoader effect runs (StrictMode: runs twice)
   - Makes API call to /api/cv/3ca980a7-202c-472c-bfce-554075484f9f
   ↓
9. Steps 3-8 repeat if state continues to change
```

### Why 8 Calls Instead of 2?

With React.StrictMode, effects run twice. However, 8 calls suggests:
- Multiple state update cycles from `useHashRouting`
- Component re-mounting/re-rendering
- Each cycle triggers the effect twice (StrictMode)
- 4 cycles × 2 (StrictMode) = 8 calls

## Code Locations

### Key Files

1. **`frontend/src/main.tsx`** (line 8)
   - React.StrictMode enabled

2. **`frontend/src/app_helpers/useHashRouting.ts`** (lines 30-69)
   - Two interacting useEffects that can cause state update cycles

3. **`frontend/src/app_helpers/cvForm/useCvLoader.ts`** (lines 22-52)
   - Effect that makes API call when `cvId` changes

4. **`frontend/src/components/CVForm.tsx`** (line 37)
   - Uses `useCvLoader` hook

5. **`frontend/src/App.tsx`** (line 16)
   - Uses `useHashRouting` and passes `cvId` to `CVForm`

## How to Fix

### Solution 1: Add Debouncing/Request Deduplication (Recommended)

Add request deduplication to prevent multiple simultaneous calls with the same `cvId`:

```typescript
// In useCvLoader.ts
const loadingRef = useRef<Set<string>>(new Set())

useEffect(() => {
  const loadCvData = async () => {
    if (!cvId) return

    // Prevent duplicate calls for the same cvId
    if (loadingRef.current.has(cvId)) {
      return
    }

    loadingRef.current.add(cvId)
    setIsLoadingCv(true)
    callbacksRef.current.setLoading(true)

    try {
      const response = await axios.get(`/api/cv/${cvId}`)
      // ... rest of the code
    } finally {
      loadingRef.current.delete(cvId)
      setIsLoadingCv(false)
      callbacksRef.current.setLoading(false)
    }
  }

  if (cvId) {
    loadCvData()
  }
}, [cvId])
```

### Solution 2: Fix useHashRouting State Update Cycle

Prevent the first useEffect from modifying the hash unnecessarily:

```typescript
// In useHashRouting.ts, first useEffect
useEffect(() => {
  const currentHash = window.location.hash
  const hashViewMode = hashToViewMode(currentHash)
  const hashCvId = extractCvIdFromHash(currentHash)
  const hashProfileUpdatedAt = extractProfileUpdatedAtFromHash(currentHash)

  // Only update state if hash values differ from current state
  // Don't modify hash if it's already correct
  if (
    hashViewMode !== viewMode ||
    hashCvId !== cvId ||
    hashProfileUpdatedAt !== profileUpdatedAt
  ) {
    // Update state from hash, don't modify hash
    setViewMode(hashViewMode)
    setCvId(hashCvId)
    setProfileUpdatedAt(hashProfileUpdatedAt)
  }
}, []) // Run only once on mount

// Second useEffect handles hash changes
useEffect(() => {
  const handleHashChange = () => {
    const newViewMode = hashToViewMode(window.location.hash)
    const newCvId = extractCvIdFromHash(window.location.hash)
    const newProfileUpdatedAt = extractProfileUpdatedAtFromHash(window.location.hash)

    setViewMode(newViewMode)
    setCvId(newCvId)
    setProfileUpdatedAt(newProfileUpdatedAt)
  }

  window.addEventListener('hashchange', handleHashChange)
  return () => {
    window.removeEventListener('hashchange', handleHashChange)
  }
}, []) // No dependencies - only set up listener once
```

### Solution 3: Use useMemo/useCallback to Stabilize References

Ensure `cvId` reference doesn't change unnecessarily:

```typescript
// In App.tsx
const { viewMode, cvId, profileUpdatedAt } = useHashRouting()
const memoizedCvId = useMemo(() => cvId, [cvId])

// Pass memoizedCvId to CVForm
```

### Solution 4: Remove StrictMode (Not Recommended)

Remove `<React.StrictMode>` from `main.tsx` to prevent double invocation, but this is not recommended as StrictMode helps catch bugs.

## Recommended Approach

Combine Solutions 1 and 2:
1. Add request deduplication to `useCvLoader` to prevent duplicate API calls
2. Fix `useHashRouting` to prevent unnecessary state update cycles
3. Keep StrictMode enabled for development

This will ensure:
- No duplicate API calls even with StrictMode
- Stable state management in routing
- Better performance and reduced server load

## Solution Implemented

Both solutions have been implemented:

### 1. useHashRouting Fix

**File**: `frontend/src/app_helpers/useHashRouting.ts`

- Added `isUpdatingFromHashChangeRef` to track hashchange updates and prevent cycles
- First `useEffect` now runs only on mount (empty dependency array) and syncs state from hash without modifying hash
- Second `useEffect` sets up hashchange listener once (empty dependency array) and is the single source of truth for hash → state updates
- Prevents state update cycles that were causing multiple `cvId` changes

### 2. Request Deduplication in useCvLoader

**File**: `frontend/src/app_helpers/cvForm/useCvLoader.ts`

- Added `loadingRef` (Set) to track in-flight requests by `cvId`
- Checks if request is already in progress before making API call
- Cleans up completed requests from the Set in `finally` block
- Prevents duplicate simultaneous calls for the same `cvId`

### Results

- Single API call per CV load (2 with StrictMode, which is expected behavior)
- No state update cycles in routing
- Better performance and reduced server load
- Stable hash routing behavior
