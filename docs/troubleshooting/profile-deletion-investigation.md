# Profile Deletion Investigation

## Problem Description

Profiles are being deleted unexpectedly. The deletion occurs without explicit user action to delete the profile.

## Investigation Status

**Status**: Active investigation with runtime instrumentation

**Instrumentation Added**: Debug logging has been added to track all profile deletion paths:
- Frontend `ProfileManager.handleDelete()` - logs when delete is called, confirmed, or cancelled
- Frontend `profileService.deleteProfile()` - logs API calls and responses
- Frontend `profileService.deleteProfileByUpdatedAt()` - logs API calls with updated_at
- Backend `DELETE /api/profile` endpoint - logs endpoint calls and execution
- Backend `DELETE /api/profile/{updated_at}` endpoint - logs endpoint calls with updated_at
- Backend `delete_profile()` function - logs function calls and query results
- Backend `delete_profile_by_updated_at()` function - logs function calls with updated_at
- Backend `update_profile()` function - logs update flow to ensure Profile node isn't deleted

**Log Location**: `/home/cocodedk/0-projects/cv/.cursor/debug.log` (NDJSON format)

## Hypotheses Under Investigation

1. **User accidentally clicks delete** - ProfileManager delete handler triggered
2. **Frontend code path calls deleteProfile() without user intent** - Unintended call
3. **Backend DELETE /api/profile called incorrectly** - delete_profile() invoked when it shouldn't be
4. **Backend DELETE /api/profile/{updated_at} called with wrong timestamp** - delete_profile_by_updated_at() called incorrectly
5. **Profile update flow deletes Profile node** - update_profile() may delete instead of update
6. **Test cleanup still deleting real profiles** - Despite fixes, tests may delete real profiles

## How to Reproduce

1. Ensure backend and frontend are running
2. Navigate to profile page (#profile)
3. Use the application normally - create/edit/save profiles
4. Monitor when profile disappears
5. Check debug logs at `.cursor/debug.log` to identify deletion path

## Next Steps

Once reproduction occurs, analyze logs to:
- Identify which deletion path was triggered
- Determine root cause
- Implement targeted fix
- Verify fix with post-fix logs

## Related Issues

- [Profile Deleted by Tests](common-issues.md#profile-deleted-by-tests) - Fixed test cleanup issue
- [Test Cleanup Safety](../development/testing.md#test-cleanup-safety) - Test profile deletion safeguards
