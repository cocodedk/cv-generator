# Profile URL Timestamp Investigation

## Issue Description
- URL `http://localhost:5173/#profile-edit/2025-12-26T10%3A26%3A34.160030` does NOT load the profile
- URL `http://localhost:5173/#profile-edit/2025-12-26T10%3A53%3A36.562457` DOES load the profile

## Root Cause Analysis

### How Profile URLs Work

1. **URL Generation**: Profile URLs are generated in `ProfileList.tsx` when clicking "Edit":
   ```73:75:frontend/src/components/ProfileList.tsx
   const handleEdit = (updatedAt: string) => {
     window.location.hash = `#profile-edit/${encodeURIComponent(updatedAt)}`
   }
   ```

2. **Profile Loading**: When a profile-edit URL is accessed, `ProfileManager` extracts the timestamp and loads the profile:
   ```128:152:frontend/src/components/ProfileManager.tsx
   const loadInitialProfile = async () => {
     setIsLoadingProfile(true)
     try {
       let profile: ProfileData | null = null
       if (profileUpdatedAt) {
         // Load specific profile from hash
         profile = await getProfileByUpdatedAt(profileUpdatedAt)
       } else {
         // Load most recent profile
         profile = await getProfile()
       }
       if (profile) {
         reset(profile)
         setHasProfile(true)
       } else {
         reset(defaultProfileData)
         setHasProfile(false)
       }
     } catch (error: any) {
       setHasProfile(false)
       onError(`Failed to load profile: ${error.message || 'Unknown error'}`)
     } finally {
       setIsLoadingProfile(false)
     }
   }
   ```

3. **Database Query**: The backend uses exact timestamp matching:
   ```139:166:backend/database/queries/profile_queries.py
   GET_PROFILE_BY_UPDATED_AT_QUERY = """
   MATCH (profile:Profile { updated_at: $updated_at })
   OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
   ...
   RETURN profile, person, experiences, educations, skills
   """
   ```

### The Problem

**When a profile is updated, its `updated_at` timestamp changes:**

```46:51:backend/database/queries/profile_queries.py
UPDATE_QUERY = """
MATCH (profile:Profile)
WITH profile
ORDER BY profile.updated_at DESC
LIMIT 1
SET profile.updated_at = $updated_at
```

Every time `save_profile()` is called on an existing profile:
1. It calls `update_profile()` which generates a NEW timestamp: `datetime.utcnow().isoformat()`
2. The old timestamp is replaced with the new one
3. Any URLs with the old timestamp become invalid

**The save endpoint doesn't return the new timestamp:**

```15:26:backend/app_helpers/routes/profile.py
@router.post("/api/profile", response_model=ProfileResponse)
@limiter.limit("30/minute")
async def save_profile_endpoint(request: Request, profile_data: ProfileData):
    """Save or update master profile."""
    try:
        profile_dict = profile_data.model_dump()
        success = queries.save_profile(profile_dict)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save profile")
        return ProfileResponse(
            status="success", message="Profile saved successfully"
        )
```

`ProfileResponse` only contains `status` and `message` - no `updated_at` field.

**The frontend doesn't update the URL after saving:**

```48:64:frontend/src/components/ProfileManager.tsx
const onSubmit = useCallback(
  async (data: ProfileData) => {
    setIsSubmitting(true)
    setLoading(true)
    try {
      await saveProfile(data)
      setHasProfile(true)
      onSuccess('Profile saved successfully!')
    } catch (error: any) {
      onError(error.message)
    } finally {
      setIsSubmitting(false)
      setLoading(false)
    }
  },
  [setLoading, onSuccess, onError]
)
```

After saving, the URL hash is not updated with the new timestamp.

## Where the URL Comes From

The URL `http://localhost:5173/#profile-edit/2025-12-26T10%3A26%3A34.160030` likely comes from:

1. **ProfileList Edit Button**: User clicked "Edit" on a profile that had timestamp `2025-12-26T10:26:34.160030`
2. **Bookmark/History**: User bookmarked or saved the URL from a previous session
3. **Direct Navigation**: User manually typed or pasted the URL
4. **Browser History**: Browser autocomplete or history suggested the old URL

After the profile was saved again (at `2025-12-26T10:53:36.562457`), the old timestamp no longer exists in the database, so the URL fails.

## How to Fix

### Option 1: Return Updated Timestamp in Save Response (Recommended)

1. **Update `ProfileResponse` model** to include `updated_at`:
   ```python
   class ProfileResponse(BaseModel):
       status: str = "success"
       message: Optional[str] = None
       updated_at: Optional[str] = None  # Add this
   ```

2. **Modify save endpoint** to return the new timestamp:
   ```python
   @router.post("/api/profile", response_model=ProfileResponse)
   async def save_profile_endpoint(request: Request, profile_data: ProfileData):
       # ... existing code ...
       # Get the updated profile to retrieve new timestamp
       updated_profile = queries.get_profile()
       return ProfileResponse(
           status="success",
           message="Profile saved successfully",
           updated_at=updated_profile["updated_at"] if updated_profile else None
       )
   ```

3. **Update frontend** to update URL after save:
   ```typescript
   const onSubmit = useCallback(
     async (data: ProfileData) => {
       setIsSubmitting(true)
       setLoading(true)
       try {
         const response = await saveProfile(data)
         setHasProfile(true)
         // Update URL with new timestamp if provided
         if (response.updated_at) {
           window.location.hash = `#profile-edit/${encodeURIComponent(response.updated_at)}`
         }
         onSuccess('Profile saved successfully!')
       } catch (error: any) {
         onError(error.message)
       } finally {
         setIsSubmitting(false)
         setLoading(false)
       }
     },
     [setLoading, onSuccess, onError]
   )
   ```

### Option 2: Fallback to Most Recent Profile

If a profile with the specified timestamp doesn't exist, automatically load the most recent profile:

```typescript
const loadInitialProfile = async () => {
  setIsLoadingProfile(true)
  try {
    let profile: ProfileData | null = null
    if (profileUpdatedAt) {
      // Try to load specific profile from hash
      profile = await getProfileByUpdatedAt(profileUpdatedAt)
      // If not found, fallback to most recent
      if (!profile) {
        profile = await getProfile()
        // Update URL with new timestamp
        if (profile?.updated_at) {
          window.location.hash = `#profile-edit/${encodeURIComponent(profile.updated_at)}`
        }
      }
    } else {
      // Load most recent profile
      profile = await getProfile()
    }
    // ... rest of the code
  }
}
```

### Option 3: Use Profile ID Instead of Timestamp

Use a stable ID that doesn't change on updates (would require schema changes).

## Recommendation

**Option 1** is the best solution because:
- It ensures URLs are always up-to-date after saves
- It provides immediate feedback to users
- It prevents broken bookmarks
- It's a minimal change to existing code

**Option 2** is a good defensive measure to add alongside Option 1, as it handles edge cases where URLs might be stale.

## Implementation Status

✅ **Option 2 has been implemented** (safest approach):
- Added fallback logic in `ProfileManager.loadInitialProfile()`
- When a profile with a specific timestamp isn't found, it automatically loads the most recent profile
- The URL is automatically updated with the current timestamp to prevent future issues
- Updated `ProfileData` TypeScript type to include optional `updated_at` field to match API response

The implementation ensures that stale URLs (like `2025-12-26T10:26:34.160030`) will automatically redirect to the current profile URL, preventing 404 errors and improving user experience.
